# Enrich, clean, deduplicate, and limit related BIS standards for final recommendations.

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_PATH = BASE_DIR / "data" / "master_standards.csv"
RELATIONSHIP_PATH = BASE_DIR / "data" / "relationships.csv"
TOP10_PATH = BASE_DIR / "models" / "top10_recommendations.csv"
OUTPUT_PATH = BASE_DIR / "models" / "top10_with_relationships.csv"

MAX_RELATED_PER_STANDARD = 5


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load master standards, relationships, and Top-10 recommendations."""

    master = pd.read_csv(MASTER_PATH)
    relationships = pd.read_csv(RELATIONSHIP_PATH)
    recommendations = pd.read_csv(TOP10_PATH)

    return master, relationships, recommendations


def build_standard_lookup(master: pd.DataFrame) -> pd.DataFrame:
    """Create a unique lookup table for standard metadata."""

    lookup = (
        master[
            [
                "is_number",
                "title",
                "status",
                "source_url",
            ]
        ]
        .drop_duplicates(subset=["is_number"])
        .copy()
    )

    return lookup


def get_related_standards(
    standard_number: str,
    relationships: pd.DataFrame,
    standard_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """Find related standards in both incoming and outgoing directions."""

    # Find relationships where the recommended standard is the source.
    outgoing = relationships[
        relationships["source_is_number"] == standard_number
    ].copy()

    if not outgoing.empty:
        outgoing["related_standard"] = outgoing["related_is_number"]
        outgoing["relationship_direction"] = "outgoing"

    # Find relationships where the recommended standard is the related target.
    incoming = relationships[
        relationships["related_is_number"] == standard_number
    ].copy()

    if not incoming.empty:
        incoming["related_standard"] = incoming["source_is_number"]
        incoming["relationship_direction"] = "incoming"

    # Combine both relationship directions.
    related = pd.concat(
        [outgoing, incoming],
        ignore_index=True,
    )

    if related.empty:
        return pd.DataFrame(
            columns=[
                "related_standard",
                "related_title",
                "related_status",
                "related_source_url",
                "relationship_type",
                "reviewed_in",
                "relationship_direction",
            ]
        )

    related = related[
        [
            "related_standard",
            "relationship_type",
            "reviewed_in",
            "relationship_direction",
        ]
    ].copy()

    # Remove self-references.
    related = related[
        related["related_standard"] != standard_number
    ].copy()

    # Remove duplicate standard pairs even when relationship direction/type differs.
    related = (
        related
        .sort_values(
            by=["related_standard", "reviewed_in"],
            ascending=[True, False],
            na_position="last",
        )
        .drop_duplicates(
            subset=["related_standard"],
            keep="first",
        )
        .reset_index(drop=True)
    )

    # Add official title, status, and BIS source URL from the master dataset.
    related = related.merge(
        standard_lookup,
        left_on="related_standard",
        right_on="is_number",
        how="left",
    )

    related = related.rename(
        columns={
            "title": "related_title",
            "status": "related_status",
            "source_url": "related_source_url",
        }
    )

    related = related[
        [
            "related_standard",
            "related_title",
            "related_status",
            "related_source_url",
            "relationship_type",
            "reviewed_in",
            "relationship_direction",
        ]
    ].copy()

    # Keep current standards first, then unknown, and put withdrawn last.
    status_priority = {
        "Current": 0,
        "Unknown": 1,
        "Withdrawn": 2,
    }

    related["status_priority"] = (
        related["related_status"]
        .fillna("Unknown")
        .map(status_priority)
        .fillna(1)
    )

    related = related.sort_values(
        by=["status_priority", "reviewed_in"],
        ascending=[True, False],
        na_position="last",
    )

    # Exclude withdrawn standards from displayed related standards.
    related = related[
        related["related_status"].isin(
            ["Current", "Unknown"]
        )
    ].copy()

    related = related.drop(
        columns=["status_priority"]
    )

    return related.reset_index(drop=True)


def main() -> None:
    """Generate clean related-standard results for the Top-10 recommendations."""

    master, relationships, recommendations = load_data()

    standard_lookup = build_standard_lookup(master)

    rows = []

    for _, recommendation in recommendations.iterrows():

        standard_number = recommendation["is_number"]

        related = get_related_standards(
            standard_number=standard_number,
            relationships=relationships,
            standard_lookup=standard_lookup,
        )

        # Limit the number of related standards shown per recommendation.
        related = related.head(
            MAX_RELATED_PER_STANDARD
        )

        for _, relation in related.iterrows():

            rows.append(
                {
                    "recommended_is_number": standard_number,
                    "recommended_title": recommendation["title"],
                    "related_is_number": relation[
                        "related_standard"
                    ],
                    "related_title": relation[
                        "related_title"
                    ],
                    "related_status": relation[
                        "related_status"
                    ],
                    "related_source_url": relation[
                        "related_source_url"
                    ],
                    "relationship_type": relation[
                        "relationship_type"
                    ],
                    "reviewed_in": relation[
                        "reviewed_in"
                    ],
                    "relationship_direction": relation[
                        "relationship_direction"
                    ],
                }
            )

    related_results = pd.DataFrame(rows)

    # Remove any final duplicate pair across the generated output.
    if not related_results.empty:
        related_results = (
            related_results
            .drop_duplicates(
                subset=[
                    "recommended_is_number",
                    "related_is_number",
                ]
            )
            .reset_index(drop=True)
        )

    related_results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("Recommendations:", len(recommendations))
    print("Relationships:", len(relationships))
    print(
        "Related standards selected:",
        len(related_results),
    )
    print(
        f"Saved to: {OUTPUT_PATH}"
    )

    if not related_results.empty:
        print("\nSample results:\n")

        print(
            related_results.head(20).to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()