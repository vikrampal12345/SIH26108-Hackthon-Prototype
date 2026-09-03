# Build a FAISS index over BIS embeddings and retrieve the Top 50 semantic candidates.

from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "master_standards.csv"
EMBEDDING_PATH = BASE_DIR / "models" / "standard_embeddings.npy"
INDEX_PATH = BASE_DIR / "models" / "standards.faiss"

MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 50


class BISFaissRetriever:
    """Retrieve semantically similar BIS standards using FAISS."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

        self.df = pd.read_csv(DATA_PATH)

        if "is_number" not in self.df.columns:
            raise ValueError("is_number column is missing from master_standards.csv")

        embeddings = np.load(EMBEDDING_PATH).astype(np.float32)

        if len(self.df) != len(embeddings):
            raise ValueError(
                f"Dataset rows ({len(self.df)}) do not match "
                f"embedding rows ({len(embeddings)})"
            )

        self.embeddings = embeddings

        dimension = embeddings.shape[1]

        # Inner product works as cosine similarity because embeddings are normalized.
        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

    def save_index(self) -> None:
        """Save the FAISS index to disk."""
        faiss.write_index(self.index, str(INDEX_PATH))
        print(f"FAISS index saved to: {INDEX_PATH}")

    def search(self, query: str, top_k: int = TOP_K) -> pd.DataFrame:
        """Return the most semantically similar BIS standards."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(query_embedding, dtype=np.float32)

        scores, indices = self.index.search(query_embedding, top_k)

        results = self.df.iloc[indices[0]].copy()

        results["semantic_score"] = scores[0]

        results["faiss_rank"] = range(1, len(results) + 1)

        return results.reset_index(drop=True)


def main() -> None:
    """Build the FAISS index and test Top-50 retrieval."""
    retriever = BISFaissRetriever()

    retriever.save_index()

    query = "We need ordinary Portland cement for building construction."

    results = retriever.search(query)

    print("\nTop 10 results from the Top 50 candidates:\n")

    print(
        results[
            [
                "faiss_rank",
                "is_number",
                "title",
                "semantic_score",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()