# Generate and save Sentence Transformer embeddings for all BIS standards.

from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "master_standards.csv"
MODEL_DIR = BASE_DIR / "models"
EMBEDDING_PATH = MODEL_DIR / "standard_embeddings.npy"

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 32


def load_master_data() -> pd.DataFrame:
    """Load the processed BIS master dataset."""
    df = pd.read_csv(DATA_PATH)

    if "search_text" not in df.columns:
        raise ValueError("search_text column is missing from master_standards.csv")

    if df["search_text"].isna().any():
        raise ValueError("search_text contains missing values")

    return df


def generate_embeddings(df: pd.DataFrame) -> np.ndarray:
    """Convert BIS search_text into normalized semantic embeddings."""
    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        df["search_text"].tolist(),
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    return np.asarray(embeddings, dtype=np.float32)


def save_embeddings(embeddings: np.ndarray) -> None:
    """Save the generated embeddings to the models directory."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDING_PATH, embeddings)


def main() -> None:
    """the complete embedding generation process."""
    df = load_master_data()

    embeddings = generate_embeddings(df)

    save_embeddings(embeddings)

    print(f"Standards: {len(df)}")
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Saved to: {EMBEDDING_PATH}")


if __name__ == "__main__":
    main()