# Run all evaluation queries through Syncronal and save the resulting recommendations.

import sys
from pathlib import Path

import pandas as pd


# Add the project root to the Python import path.
PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from ml.pipeline import BISRecommendationPipeline


# Define the evaluation input and output files.
INPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "test_queries.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "verification_results.csv"
)


def main():
    # Load the evaluation queries.
    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig",
    )

    if "query" not in df.columns:
        raise ValueError(
            "test_queries.csv must contain a 'query' column."
        )

    # Remove empty queries.
    df = df.dropna(
        subset=["query"]
    ).copy()

    df["query"] = (
        df["query"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["query"] != ""
    ].reset_index(
        drop=True
    )

    if df.empty:
        raise ValueError(
            "No valid queries were found."
        )

    # Load the same pipeline used by Syncronal.
    pipeline = BISRecommendationPipeline()

    all_results = []

    total_queries = len(df)

    print("=" * 80)
    print(
        "SYNCRONAL RECOMMENDATION VERIFICATION"
    )
    print("=" * 80)

    print(
        f"Test queries: {total_queries}"
    )

    print()

    # Process every test query.
    for query_number, query in enumerate(
        df["query"],
        start=1,
    ):
        print("-" * 80)

        print(
            f"Query {query_number}/{total_queries}"
        )

        print(
            f"Requirement: {query}"
        )

        try:
            # Run the query through the complete recommendation pipeline.
            result = pipeline.recommend(
                query=query,
                top_k=50,
                final_k=10,
                related_k=5,
            )

        except Exception as exc:
            # Stop immediately so a failed query cannot contaminate the evaluation CSV.
            raise RuntimeError(
                f"Query {query_number} failed: {exc}"
            ) from exc

        recommendations = (
            result["recommendations"]
        )

        print(
            f"Candidates: "
            f"{result['candidates_retrieved']}"
        )

        print(
            f"Unique candidates: "
            f"{result['unique_candidates']}"
        )

        print(
            f"Recommendations returned: "
            f"{len(recommendations)}"
        )

        # Require exactly ten recommendations for evaluation consistency.
        if len(recommendations) != 10:
            raise RuntimeError(
                f"Query {query_number} returned "
                f"{len(recommendations)} recommendations instead of 10."
            )

        # Save each recommendation as one evaluation row.
        for recommendation in recommendations:

            all_results.append(
                {
                    "query_number": query_number,

                    "query": query,

                    "rank": recommendation[
                        "rank"
                    ],

                    "is_number": recommendation[
                        "is_number"
                    ],

                    "title": recommendation[
                        "title"
                    ],

                    "hybrid_score": recommendation[
                        "hybrid_score"
                    ],

                    "semantic_score": recommendation[
                        "semantic_score"
                    ],

                    "classification_score":
                        recommendation[
                            "classification_score"
                        ],

                    "status": recommendation[
                        "status"
                    ],

                    "certification": recommendation[
                        "certification"
                    ],

                    "type_of_standard":
                        recommendation[
                            "type_of_standard"
                        ],

                    "department": recommendation[
                        "department"
                    ],

                    "group": recommendation[
                        "group"
                    ],

                    "sub_group": recommendation[
                        "sub_group"
                    ],

                    "sub_sub_group":
                        recommendation[
                            "sub_sub_group"
                        ],

                    "superseding_is":
                        recommendation[
                            "superseding_is"
                        ],

                    "related_count":
                        len(
                            recommendation.get(
                                "related_standards",
                                [],
                            )
                        ),
                }
            )

            print(
                f"  #{recommendation['rank']}: "
                f"{recommendation['is_number']} — "
                f"{recommendation['title']} | "
                f"score="
                f"{recommendation['hybrid_score']:.4f} | "
                f"status="
                f"{recommendation['status']}"
            )

        print()

    # Convert all successful recommendation rows to a dataframe.
    df1 = pd.DataFrame(
        all_results
    )

    expected_rows = (
        total_queries * 10
    )

    # Make sure exactly 200 recommendations were generated.
    if len(df1) != expected_rows:
        raise RuntimeError(
            f"Expected {expected_rows} rows, "
            f"but generated {len(df1)} rows."
        )

    # Save the new verification results.
    df1.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("=" * 80)
    print(
        "VERIFICATION COMPLETE"
    )
    print("=" * 80)

    print(
        f"Queries tested: {total_queries}"
    )

    print(
        f"Rows saved: {len(df1)}"
    )

    print(
        f"Results saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    # Start the Syncronal verification process.
    main()