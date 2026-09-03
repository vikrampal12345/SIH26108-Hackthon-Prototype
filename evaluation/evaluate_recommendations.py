# Calculate Top-1, Top-5, Top-10, MRR, and weighted relevance metrics from the labeled recommendations.

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "verification_labeling.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "evaluation_summary.csv"
)


VALID_LABELS = {
    "Relevant",
    "Partially Relevant",
    "Not Relevant"
}


LABEL_SCORES = {
    "Relevant": 1.0,
    "Partially Relevant": 0.5,
    "Not Relevant": 0.0
}


def validate_input(df):
    # Validate that the labeling file contains the required columns and valid labels.

    required_columns = {
        "query_number",
        "query",
        "rank",
        "is_number",
        "title",
        "hybrid_score",
        "status",
        "relevance",
        "notes"
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Normalize the relevance labels.
    df["relevance"] = (
        df["relevance"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    unlabeled = df[
        df["relevance"] == ""
    ]

    if not unlabeled.empty:
        print(
            f"WARNING: {len(unlabeled)} recommendations are still unlabeled."
        )

    invalid_labels = df[
        (df["relevance"] != "")
        & (~df["relevance"].isin(VALID_LABELS))
    ]

    if not invalid_labels.empty:
        examples = (
            invalid_labels["relevance"]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Invalid relevance labels found: "
            + ", ".join(examples)
            + ". Use only: Relevant, Partially Relevant, Not Relevant."
        )


def calculate_query_metrics(query_df):
    # Calculate ranking metrics for one procurement query.

    query_df = query_df.sort_values(
        "rank"
    ).reset_index(drop=True)

    labeled = query_df[
        query_df["relevance"] != ""
    ].copy()

    if labeled.empty:
        return {
            "top1_relevant": np.nan,
            "top5_relevant": np.nan,
            "top10_relevant": np.nan,
            "top1_acceptable": np.nan,
            "top5_acceptable": np.nan,
            "top10_acceptable": np.nan,
            "mrr": np.nan,
            "ndcg10": np.nan,
        }

    labels = labeled["relevance"].tolist()

    # Find the first fully relevant recommendation.
    relevant_positions = [
        index + 1
        for index, label in enumerate(labels)
        if label == "Relevant"
    ]

    first_relevant_rank = (
        relevant_positions[0]
        if relevant_positions
        else None
    )

    # Treat both Relevant and Partially Relevant as acceptable.
    acceptable_labels = {
        "Relevant",
        "Partially Relevant"
    }

    # Calculate exact relevance at Top 1.
    top1_relevant = (
        1.0
        if len(labels) >= 1
        and labels[0] == "Relevant"
        else 0.0
    )

    # Calculate whether at least one fully relevant result is in Top 5.
    top5_relevant = (
        1.0
        if any(
            label == "Relevant"
            for label in labels[:5]
        )
        else 0.0
    )

    # Calculate whether at least one fully relevant result is in Top 10.
    top10_relevant = (
        1.0
        if any(
            label == "Relevant"
            for label in labels[:10]
        )
        else 0.0
    )

    # Calculate whether an acceptable result appears at Top 1.
    top1_acceptable = (
        1.0
        if len(labels) >= 1
        and labels[0] in acceptable_labels
        else 0.0
    )

    # Calculate whether an acceptable result appears in Top 5.
    top5_acceptable = (
        1.0
        if any(
            label in acceptable_labels
            for label in labels[:5]
        )
        else 0.0
    )

    # Calculate whether an acceptable result appears in Top 10.
    top10_acceptable = (
        1.0
        if any(
            label in acceptable_labels
            for label in labels[:10]
        )
        else 0.0
    )

    # Calculate Mean Reciprocal Rank using the first fully relevant result.
    mrr = (
        1.0 / first_relevant_rank
        if first_relevant_rank is not None
        else 0.0
    )

    # Convert relevance labels into graded scores for NDCG.
    relevance_scores = [
        LABEL_SCORES[label]
        for label in labels[:10]
    ]

    dcg = 0.0

    for position, score in enumerate(
        relevance_scores,
        start=1
    ):
        dcg += (
            (2 ** score - 1)
            / np.log2(position + 1)
        )

    ideal_scores = sorted(
        relevance_scores,
        reverse=True
    )

    idcg = 0.0

    for position, score in enumerate(
        ideal_scores,
        start=1
    ):
        idcg += (
            (2 ** score - 1)
            / np.log2(position + 1)
        )

    ndcg10 = (
        dcg / idcg
        if idcg > 0
        else 0.0
    )

    return {
        "top1_relevant": top1_relevant,
        "top5_relevant": top5_relevant,
        "top10_relevant": top10_relevant,
        "top1_acceptable": top1_acceptable,
        "top5_acceptable": top5_acceptable,
        "top10_acceptable": top10_acceptable,
        "mrr": mrr,
        "ndcg10": ndcg10,
    }


def main():
    # Load the manually labeled recommendation results.

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    validate_input(df)

    # Stop before calculating final metrics if any result remains unlabeled.
    unlabeled_count = (
        df["relevance"] == ""
    ).sum()

    if unlabeled_count > 0:
        raise ValueError(
            f"{unlabeled_count} recommendation rows are still unlabeled. "
            "Fill the relevance column before running the evaluation."
        )

    # Calculate metrics separately for every procurement query.
    query_metrics = []

    for query_number, query_df in df.groupby(
        "query_number",
        sort=True
    ):

        metrics = calculate_query_metrics(
            query_df
        )

        query_metrics.append(
            {
                "query_number": query_number,
                "query": query_df["query"].iloc[0],
                **metrics
            }
        )

    df1 = pd.DataFrame(
        query_metrics
    )

    # Calculate aggregate performance across all test queries.
    summary = {
        "total_queries": len(df1),

        "top1_relevance": (
            df1["top1_relevant"].mean()
        ),

        "top5_relevance": (
            df1["top5_relevant"].mean()
        ),

        "top10_relevance": (
            df1["top10_relevant"].mean()
        ),

        "top1_acceptable": (
            df1["top1_acceptable"].mean()
        ),

        "top5_acceptable": (
            df1["top5_acceptable"].mean()
        ),

        "top10_acceptable": (
            df1["top10_acceptable"].mean()
        ),

        "mrr": (
            df1["mrr"].mean()
        ),

        "ndcg10": (
            df1["ndcg10"].mean()
        ),

        "relevant_results": int(
            (
                df["relevance"]
                == "Relevant"
            ).sum()
        ),

        "partially_relevant_results": int(
            (
                df["relevance"]
                == "Partially Relevant"
            ).sum()
        ),

        "not_relevant_results": int(
            (
                df["relevance"]
                == "Not Relevant"
            ).sum()
        )
    }

    # Create a one-row summary dataframe for easy reporting.
    summary_df = pd.DataFrame(
        [summary]
    )

    # Save the detailed per-query evaluation.
    query_output = (
        PROJECT_ROOT
        / "evaluation"
        / "query_metrics.csv"
    )

    df1.to_csv(
        query_output,
        index=False,
        encoding="utf-8-sig"
    )

    # Save the overall evaluation summary.
    summary_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # Print the metrics in a judge-friendly format.
    print()
    print("=" * 70)
    print("SYNCRONAL EVALUATION RESULTS")
    print("=" * 70)

    print(
        f"Queries evaluated : {summary['total_queries']}"
    )

    print(
        f"Top-1 relevance   : "
        f"{summary['top1_relevance'] * 100:.2f}%"
    )

    print(
        f"Top-5 relevance   : "
        f"{summary['top5_relevance'] * 100:.2f}%"
    )

    print(
        f"Top-10 relevance  : "
        f"{summary['top10_relevance'] * 100:.2f}%"
    )

    print(
        f"Top-1 acceptable  : "
        f"{summary['top1_acceptable'] * 100:.2f}%"
    )

    print(
        f"Top-5 acceptable  : "
        f"{summary['top5_acceptable'] * 100:.2f}%"
    )

    print(
        f"Top-10 acceptable : "
        f"{summary['top10_acceptable'] * 100:.2f}%"
    )

    print(
        f"MRR               : "
        f"{summary['mrr']:.4f}"
    )

    print(
        f"NDCG@10           : "
        f"{summary['ndcg10']:.4f}"
    )

    print()
    print(
        f"Relevant          : "
        f"{summary['relevant_results']}"
    )

    print(
        f"Partially Relevant: "
        f"{summary['partially_relevant_results']}"
    )

    print(
        f"Not Relevant      : "
        f"{summary['not_relevant_results']}"
    )

    print()
    print(
        f"Per-query results : {query_output}"
    )

    print(
        f"Overall summary   : {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    # Start the Syncronal evaluation.
    main()