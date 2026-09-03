# Calculate Syncronal baseline recommendation metrics from the labeled evaluation CSV.

from pathlib import Path

import pandas as pd


# Define the evaluation input file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "verification_labeling_fast.csv"
)


def main():
    # Load the labeled recommendation results.
    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    # Check that all 200 recommendation rows have labels.
    unlabeled = df[
        df["relevance"]
        .isna()
        |
        (df["relevance"].astype(str).str.strip() == "")
    ]

    if len(unlabeled) > 0:
        raise ValueError(
            f"{len(unlabeled)} rows are still unlabeled."
        )

    # Store metrics for every query.
    query_results = []

    # Evaluate each procurement query independently.
    for query_number, df1 in df.groupby(
        "query_number",
        sort=True
    ):

        # Sort recommendations by their original rank.
        df1 = df1.sort_values(
            "rank"
        )

        labels = (
            df1["relevance"]
            .tolist()
        )

        # Check exact relevance at rank 1.
        top1 = (
            labels[0] == "Relevant"
        )

        # Check whether a fully relevant result exists in the top 5.
        top5 = any(
            label == "Relevant"
            for label in labels[:5]
        )

        # Check whether a fully relevant result exists in the top 10.
        top10 = any(
            label == "Relevant"
            for label in labels[:10]
        )

        # Treat partial relevance as acceptable for the broader metric.
        acceptable = {
            "Relevant",
            "Partially Relevant"
        }

        top1_acceptable = (
            labels[0]
            in acceptable
        )

        top5_acceptable = any(
            label in acceptable
            for label in labels[:5]
        )

        top10_acceptable = any(
            label in acceptable
            for label in labels[:10]
        )

        query_results.append(
            {
                "query_number": query_number,
                "top1": int(top1),
                "top5": int(top5),
                "top10": int(top10),
                "top1_acceptable": int(
                    top1_acceptable
                ),
                "top5_acceptable": int(
                    top5_acceptable
                ),
                "top10_acceptable": int(
                    top10_acceptable
                )
            }
        )

    # Convert the per-query results to a dataframe.
    df1 = pd.DataFrame(
        query_results
    )

    # Calculate the overall baseline metrics.
    total_queries = len(df1)

    top1 = (
        df1["top1"].mean()
        * 100
    )

    top5 = (
        df1["top5"].mean()
        * 100
    )

    top10 = (
        df1["top10"].mean()
        * 100
    )

    top1_acceptable = (
        df1["top1_acceptable"].mean()
        * 100
    )

    top5_acceptable = (
        df1["top5_acceptable"].mean()
        * 100
    )

    top10_acceptable = (
        df1["top10_acceptable"].mean()
        * 100
    )

    # Count the total number of labels by category.
    relevant = (
        df["relevance"]
        == "Relevant"
    ).sum()

    partial = (
        df["relevance"]
        == "Partially Relevant"
    ).sum()

    not_relevant = (
        df["relevance"]
        == "Not Relevant"
    ).sum()

    # Print the baseline evaluation report.
    print()
    print("=" * 60)
    print("SYNCRONAL BASELINE EVALUATION")
    print("=" * 60)

    print(
        f"Queries tested        : {total_queries}"
    )

    print(
        f"Recommendations tested: {len(df)}"
    )

    print()

    print(
        f"Top-1 relevance       : {top1:.2f}%"
    )

    print(
        f"Top-5 relevance       : {top5:.2f}%"
    )

    print(
        f"Top-10 relevance      : {top10:.2f}%"
    )

    print()

    print(
        f"Top-1 acceptable      : "
        f"{top1_acceptable:.2f}%"
    )

    print(
        f"Top-5 acceptable      : "
        f"{top5_acceptable:.2f}%"
    )

    print(
        f"Top-10 acceptable     : "
        f"{top10_acceptable:.2f}%"
    )

    print()

    print(
        f"Relevant labels       : {relevant}"
    )

    print(
        f"Partially relevant   : {partial}"
    )

    print(
        f"Not relevant         : {not_relevant}"
    )

    print("=" * 60)


if __name__ == "__main__":
    # Run the baseline evaluation.
    main()