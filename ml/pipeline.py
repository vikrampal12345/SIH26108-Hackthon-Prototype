# Complete BIS recommendation pipeline with direct relationship expansion for the prototype.

from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from ml.hybrid_ranker import (
    add_classification_score,
    add_certification_score,
    add_hybrid_score,
    add_status_score,
    apply_lifecycle_filter,
    deduplicate_candidates,
    rerank,
)


class BISRecommendationPipeline:
    # Initialize the complete Syncronal BIS recommendation engine.

    def __init__(
        self,
        master_path: str = "data/master_standards.csv",
        relationships_path: str = "data/relationships.csv",
        embeddings_path: str = "models/standard_embeddings.npy",
        faiss_index_path: str = "models/standards.faiss",
        model_name: str = "all-MiniLM-L6-v2",
    ):
        # Store the prototype dataset and model paths.
        self.master_path = Path(
            master_path
        )

        self.relationships_path = Path(
            relationships_path
        )

        self.embeddings_path = Path(
            embeddings_path
        )

        self.faiss_index_path = Path(
            faiss_index_path
        )

        # Load the BIS master standards.
        self.master_df = pd.read_csv(
            self.master_path
        )

        # Load the BIS standard relationships.
        self.relationships_df = pd.read_csv(
            self.relationships_path
        )

        # Clean column names.
        self.master_df.columns = (
            self.master_df.columns
            .str.strip()
        )

        self.relationships_df.columns = (
            self.relationships_df.columns
            .str.strip()
        )

        # Validate the relationship dataset once during startup.
        required_relationship_columns = [
            "source_is_number",
            "related_is_number",
            "relationship_type",
        ]

        missing_columns = [
            column
            for column in required_relationship_columns
            if column not in self.relationships_df.columns
        ]

        if missing_columns:
            raise ValueError(
                "relationships.csv is missing: "
                + ", ".join(
                    missing_columns
                )
            )

        # Load the existing MiniLM model.
        self.model = SentenceTransformer(
            model_name
        )

        # Load the existing FAISS index.
        self.index = faiss.read_index(
            str(
                self.faiss_index_path
            )
        )

        # Load the existing standard embeddings.
        self.embeddings = np.load(
            str(
                self.embeddings_path
            )
        ).astype(
            np.float32
        )

    def _clean_value(
        self,
        value: Any,
    ) -> str:
        # Convert empty, missing and placeholder values into safe frontend text.
        if value is None:
            return "Not Available"

        try:
            if pd.isna(value):
                return "Not Available"
        except (
            TypeError,
            ValueError,
        ):
            pass

        text = str(value).strip()

        if not text:
            return "Not Available"

        if text.lower() in {
            "nan",
            "none",
            "unknown",
            "--",
            "not available",
        }:
            return "Not Available"

        return text

    def _safe_float(
        self,
        value: Any,
    ) -> float:
        # Safely convert ranking values into normal Python floats.
        try:
            value = pd.to_numeric(
                value,
                errors="coerce",
            )

            if pd.isna(value):
                return 0.0

            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    def _row_value(
        self,
        row: pd.Series,
        column: str,
    ) -> str:
        # Safely read any optional master-data field.
        if column not in row.index:
            return "Not Available"

        return self._clean_value(
            row[column]
        )

    def _retrieve_candidates(
        self,
        query: str,
        top_k: int,
    ) -> pd.DataFrame:
        # Convert the query into a MiniLM vector and perform FAISS retrieval.
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        # Search the existing FAISS index.
        scores, indices = (
            self.index.search(
                query_embedding,
                top_k,
            )
        )

        rows = []

        # Convert FAISS positions back to master records.
        for score, position in zip(
            scores[0],
            indices[0],
        ):
            if position < 0:
                continue

            if position >= len(
                self.master_df
            ):
                continue

            row = (
                self.master_df
                .iloc[int(position)]
                .copy()
            )

            row["semantic_score"] = float(
                score
            )

            rows.append(row)

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(
            rows
        )

    def _find_master_record(
        self,
        standard_number: str,
    ):
        # Find a related standard in master data without assuming unique IS numbers.
        if "is_number" not in self.master_df.columns:
            return None

        target = str(
            standard_number
        ).strip().lower()

        matches = (
            self.master_df[
                self.master_df[
                    "is_number"
                ]
                .astype(str)
                .str.strip()
                .str.lower()
                == target
            ]
        )

        if matches.empty:
            return None

        return matches.iloc[0]

    def _get_related_standards(
        self,
        standard_number: str,
        related_k: int = 5,
    ) -> List[Dict[str, Any]]:
        # Directly expand BIS relationships using source and related IS numbers.
        if not standard_number:
            return []

        target = (
            str(standard_number)
            .strip()
            .lower()
        )

        relationships = self.relationships_df.copy()

        # Normalize relationship identifiers for matching.
        relationships[
            "_source"
        ] = (
            relationships[
                "source_is_number"
            ]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        relationships[
            "_related"
        ] = (
            relationships[
                "related_is_number"
            ]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # Find both outgoing and incoming relationships.
        outgoing = relationships[
            relationships["_source"]
            == target
        ].copy()

        incoming = relationships[
            relationships["_related"]
            == target
        ].copy()

        frames = []

        if not outgoing.empty:
            outgoing[
                "_direction"
            ] = "outgoing"

            frames.append(
                outgoing
            )

        if not incoming.empty:
            incoming[
                "_direction"
            ] = "incoming"

            frames.append(
                incoming
            )

        if not frames:
            return []

        combined = pd.concat(
            frames,
            ignore_index=True,
        )

        # Remove duplicate relationship rows.
        combined = (
            combined.drop_duplicates(
                subset=[
                    "source_is_number",
                    "related_is_number",
                    "relationship_type",
                ]
            )
        )

        output = []

        seen_numbers = set()

        # Build clean related-standard records.
        for _, relation in combined.iterrows():
            source_number = self._clean_value(
                relation.get(
                    "source_is_number"
                )
            )

            related_number = self._clean_value(
                relation.get(
                    "related_is_number"
                )
            )

            # Determine the standard on the other side of the relationship.
            if (
                related_number
                .strip()
                .lower()
                == target
            ):
                other_number = source_number
            else:
                other_number = related_number

            if (
                not other_number
                or other_number
                == "Not Available"
            ):
                continue

            other_key = (
                other_number
                .strip()
                .lower()
            )

            # Do not show the recommendation itself as a related record.
            if other_key == target:
                continue

            # Avoid duplicate related standards.
            if other_key in seen_numbers:
                continue

            seen_numbers.add(
                other_key
            )

            master_row = (
                self._find_master_record(
                    other_number
                )
            )

            if master_row is not None:
                title = self._row_value(
                    master_row,
                    "title",
                )

                status = self._row_value(
                    master_row,
                    "status",
                )

                source_url = self._row_value(
                    master_row,
                    "source_url",
                )

            else:
                title = self._clean_value(
                    relation.get(
                        "related_title"
                    )
                )

                status = "Not Available"

                source_url = "Not Available"

            relationship_type = (
                self._clean_value(
                    relation.get(
                        "relationship_type"
                    )
                )
            )

            direction = self._clean_value(
                relation.get(
                    "_direction"
                )
            )

            # Preserve the relationship direction used by the frontend.
            if direction == "outgoing":
                display_direction = (
                    "outgoing"
                )
            else:
                display_direction = (
                    "incoming"
                )

            output.append(
                {
                    "is_number": other_number,
                    "title": title,
                    "status": status,
                    "source_url": source_url,
                    "relationship_type": (
                        relationship_type
                    ),
                    "direction": (
                        display_direction
                    ),
                }
            )

            if len(output) >= related_k:
                break

        return output

    def _prepare_output(
        self,
        recommendations: pd.DataFrame,
        related_k: int,
    ) -> List[Dict[str, Any]]:
        # Convert final ranked standards into the complete frontend response.
        output = []

        for rank, (_, row) in enumerate(
            recommendations.iterrows(),
            start=1,
        ):
            standard_number = (
                self._row_value(
                    row,
                    "is_number",
                )
            )

            # Get related/referred standards directly from the relationship CSV.
            related = (
                self._get_related_standards(
                    standard_number,
                    related_k,
                )
            )

            recommendation = {
                "rank": rank,

                "is_number": standard_number,

                "title": self._row_value(
                    row,
                    "title",
                ),

                "hybrid_score": (
                    self._safe_float(
                        row.get(
                            "hybrid_score",
                            0.0,
                        )
                    )
                ),

                "semantic_score": (
                    self._safe_float(
                        row.get(
                            "semantic_score",
                            0.0,
                        )
                    )
                ),

                "classification_score": (
                    self._safe_float(
                        row.get(
                            "classification_score",
                            0.0,
                        )
                    )
                ),

                "status": self._row_value(
                    row,
                    "status",
                ),

                "certification": self._row_value(
                    row,
                    "certification",
                ),

                "department": self._row_value(
                    row,
                    "department",
                ),

                "technical_committee": (
                    self._row_value(
                        row,
                        "technical_committee",
                    )
                ),

                "group": self._row_value(
                    row,
                    "group",
                ),

                "sub_group": self._row_value(
                    row,
                    "sub_group",
                ),

                "sub_sub_group": (
                    self._row_value(
                        row,
                        "sub_sub_group",
                    )
                ),

                "type_of_standard": (
                    self._row_value(
                        row,
                        "type_of_standard",
                    )
                ),

                "reviewed_in": self._row_value(
                    row,
                    "reviewed_in",
                ),

                "revisions": self._row_value(
                    row,
                    "number_of_revisions",
                ),

                "amendments": self._row_value(
                    row,
                    "number_of_amendments",
                ),

                "reaffirmation_year": (
                    self._row_value(
                        row,
                        "reaffirmation_year",
                    )
                ),

                "superseding_is": (
                    self._row_value(
                        row,
                        "superseding_is",
                    )
                ),

                "relevant_ministries": (
                    self._row_value(
                        row,
                        "relevant_ministries",
                    )
                ),

                "short_common_man_title": (
                    self._row_value(
                        row,
                        "short_common_man_title",
                    )
                ),

                "source_url": self._row_value(
                    row,
                    "source_url",
                ),

                "related_standards": related,
            }

            output.append(
                recommendation
            )

        return output

    def recommend(
        self,
        query: str,
        top_k: int = 50,
        final_k: int = 10,
        related_k: int = 5,
    ) -> Dict[str, Any]:
        # Execute retrieval, hybrid ranking, lifecycle filtering and relationship expansion.
        if not isinstance(
            query,
            str,
        ):
            raise ValueError(
                "Query must be a string."
            )

        query = query.strip()

        if len(query) < 3:
            raise ValueError(
                "Query must contain at least 3 characters."
            )

        if len(query) > 2000:
            raise ValueError(
                "Query must not exceed 2000 characters."
            )

        # Retrieve semantic candidates from FAISS.
        candidates_df = (
            self._retrieve_candidates(
                query,
                top_k,
            )
        )

        candidates_retrieved = len(
            candidates_df
        )

        if candidates_df.empty:
            return {
                "query": query,
                "candidates_retrieved": 0,
                "unique_candidates": 0,
                "recommendation_count": 0,
                "recommendations": [],
            }

        # Remove duplicate standards.
        candidates_df = (
            deduplicate_candidates(
                candidates_df
            )
        )

        unique_candidates = len(
            candidates_df
        )

        # Encode the query for classification scoring.
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        # Calculate classification relevance.
        candidates_df = (
            add_classification_score(
                candidates_df,
                query_embedding,
                self.model,
            )
        )

        # Calculate current/withdrawn status relevance.
        candidates_df = (
            add_status_score(
                candidates_df
            )
        )

        # Calculate certification relevance.
        candidates_df = (
            add_certification_score(
                candidates_df
            )
        )

        # Calculate the original working hybrid score.
        candidates_df = (
            add_hybrid_score(
                candidates_df
            )
        )

        # Remove withdrawn standards from primary results.
        candidates_df = (
            apply_lifecycle_filter(
                candidates_df
            )
        )

        # Sort candidates using the hybrid score.
        candidates_df = rerank(
            candidates_df
        )

        # Select final recommendations.
        recommendations = (
            candidates_df
            .head(final_k)
            .copy()
        )

        # Build the complete frontend response.
        recommendation_output = (
            self._prepare_output(
                recommendations,
                related_k,
            )
        )

        return {
            "query": query,
            "candidates_retrieved": (
                candidates_retrieved
            ),
            "unique_candidates": (
                unique_candidates
            ),
            "recommendation_count": (
                len(
                    recommendation_output
                )
            ),
            "recommendations": (
                recommendation_output
            ),
        }


# Preserve the alternate engine name for compatibility.
BISRecommendationEngine = BISRecommendationPipeline