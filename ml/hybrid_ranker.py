# Hybrid ranking engine for the Syncronal BIS recommendation prototype.

import numpy as np
import pandas as pd


# Original prototype weights used for the final ranking.
WEIGHTS = {
    "semantic": 0.70,
    "classification": 0.15,
    "status": 0.10,
    "certification": 0.05,
}


def min_max_normalize(values):
    # Normalize scores into the 0-1 range.
    values = np.asarray(
        values,
        dtype=np.float32,
    )

    if len(values) == 0:
        return values

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum == minimum:
        return np.ones(
            len(values),
            dtype=np.float32,
        )

    return (
        (values - minimum)
        / (maximum - minimum)
    )


def _clean_text(value):
    # Convert a value into normalized lowercase text.
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (
        TypeError,
        ValueError,
    ):
        pass

    text = str(value).strip().lower()

    if text in {
        "",
        "nan",
        "none",
        "unknown",
        "--",
        "not available",
    }:
        return ""

    return " ".join(
        text.split()
    )


def deduplicate_candidates(
    df: pd.DataFrame,
) -> pd.DataFrame:
    # Remove duplicate IS numbers while retaining the strongest semantic match.
    df = df.copy()

    if "is_number" not in df.columns:
        return df

    if "semantic_score" in df.columns:
        df["semantic_score"] = pd.to_numeric(
            df["semantic_score"],
            errors="coerce",
        ).fillna(0.0)

        df = df.sort_values(
            "semantic_score",
            ascending=False,
        )

    return (
        df.drop_duplicates(
            subset=["is_number"],
            keep="first",
        )
        .reset_index(drop=True)
    )


def _classification_text(
    row: pd.Series,
) -> str:
    # Combine BIS group, subgroup and sub-sub-group information.
    fields = [
        row.get("group", ""),
        row.get("sub_group", ""),
        row.get("sub_sub_group", ""),
    ]

    values = []

    for value in fields:
        text = _clean_text(value)

        if text:
            values.append(text)

    return " ".join(values)


def add_classification_score(
    df: pd.DataFrame,
    query_embedding,
    model,
) -> pd.DataFrame:
    # Calculate semantic similarity between the query and BIS classification fields.
    df = df.copy()

    texts = [
        _classification_text(row)
        for _, row in df.iterrows()
    ]

    scores = np.zeros(
        len(df),
        dtype=np.float32,
    )

    valid_indices = [
        index
        for index, text in enumerate(texts)
        if text
    ]

    if valid_indices:
        valid_texts = [
            texts[index]
            for index in valid_indices
        ]

        embeddings = model.encode(
            valid_texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        similarities = (
            embeddings
            @ query_embedding
        )

        for index, similarity in zip(
            valid_indices,
            similarities,
        ):
            scores[index] = float(
                similarity
            )

    df["classification_score"] = (
        min_max_normalize(
            scores
        )
    )

    return df


def add_status_score(
    df: pd.DataFrame,
) -> pd.DataFrame:
    # Assign higher ranking scores to current standards.
    df = df.copy()

    def calculate(value):
        status = _clean_text(value)

        if status == "current":
            return 1.0

        if status == "withdrawn":
            return 0.0

        return 0.5

    df["status_score"] = (
        df["status"].apply(
            calculate
        )
    )

    return df


def add_certification_score(
    df: pd.DataFrame,
) -> pd.DataFrame:
    # Score mandatory, voluntary and unknown certification information.
    df = df.copy()

    def calculate(value):
        certification = _clean_text(
            value
        )

        if certification == "mandatory certification":
            return 1.0

        if certification == "voluntary certification":
            return 0.7

        return 0.5

    df["certification_score"] = (
        df["certification"].apply(
            calculate
        )
    )

    return df


def add_hybrid_score(
    df: pd.DataFrame,
) -> pd.DataFrame:
    # Combine all ranking signals into the final hybrid score.
    df = df.copy()

    semantic = pd.to_numeric(
        df["semantic_score"],
        errors="coerce",
    ).fillna(0.0)

    classification = pd.to_numeric(
        df["classification_score"],
        errors="coerce",
    ).fillna(0.0)

    status = pd.to_numeric(
        df["status_score"],
        errors="coerce",
    ).fillna(0.0)

    certification = pd.to_numeric(
        df["certification_score"],
        errors="coerce",
    ).fillna(0.0)

    semantic_normalized = (
        min_max_normalize(
            semantic.to_numpy(
                dtype=np.float32
            )
        )
    )

    df["semantic_score_normalized"] = (
        semantic_normalized
    )

    df["hybrid_score"] = (
        WEIGHTS["semantic"]
        * semantic_normalized

        + WEIGHTS["classification"]
        * classification.to_numpy(
            dtype=np.float32
        )

        + WEIGHTS["status"]
        * status.to_numpy(
            dtype=np.float32
        )

        + WEIGHTS["certification"]
        * certification.to_numpy(
            dtype=np.float32
        )
    )

    return df


def apply_lifecycle_filter(
    df: pd.DataFrame,
) -> pd.DataFrame:
    # Remove withdrawn standards from the primary recommendations.
    df = df.copy()

    if "status" not in df.columns:
        return df.reset_index(
            drop=True
        )

    status = (
        df["status"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return (
        df[status != "withdrawn"]
        .reset_index(drop=True)
    )


def rerank(
    df: pd.DataFrame,
) -> pd.DataFrame:
    # Sort candidates from highest to lowest hybrid score.
    return (
        df.sort_values(
            "hybrid_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )


__all__ = [
    "WEIGHTS",
    "min_max_normalize",
    "deduplicate_candidates",
    "add_classification_score",
    "add_status_score",
    "add_certification_score",
    "add_hybrid_score",
    "apply_lifecycle_filter",
    "rerank",
]