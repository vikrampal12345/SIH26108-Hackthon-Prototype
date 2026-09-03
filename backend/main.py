# FastAPI backend for the Syncronal BIS Standard Recommendation prototype.

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import RecommendationRequest
from ml.pipeline import BISRecommendationPipeline


# Create the FastAPI application.
app = FastAPI(
    title="Syncronal BIS Standard Recommendation API",
    version="1.0.0",
)


# Allow the local frontend to call the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create the recommendation engine once when the server starts.
pipeline = BISRecommendationPipeline()


@app.get("/")
def root():
    # Return a simple API status message.
    return {
        "message": "Syncronal BIS Standard Recommendation API",
        "status": "running",
    }


@app.get("/health")
def health():
    # Provide a simple health-check endpoint.
    return {
        "status": "healthy",
    }


@app.post("/recommend")
def recommend(
    request: RecommendationRequest,
) -> Dict[str, Any]:
    # Generate BIS recommendations without response-model validation.
    try:
        result = pipeline.recommend(
            query=request.query,
            top_k=50,
            final_k=10,
            related_k=5,
        )

        # Return the raw JSON-compatible pipeline response.
        return result

    except Exception as exc:
        # Convert recommendation failures into a readable HTTP error.
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation failed: {exc}",
        ) from exc


@app.post("/recommend-document")
async def recommend_document(
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    # Extract text from PDF, DOCX or TXT input and run the same recommendation engine.
    try:
        max_file_size = 10 * 1024 * 1024

        # Read the uploaded file.
        content = await file.read()

        # Reject files larger than the prototype upload limit.
        if len(content) > max_file_size:
            raise HTTPException(
                status_code=413,
                detail="File size must not exceed 10 MB.",
            )

        filename = file.filename or ""
        suffix = Path(filename).suffix.lower()

        extracted_text = ""

        # Extract PDF text.
        if suffix == ".pdf":
            from io import BytesIO

            from pypdf import PdfReader

            reader = PdfReader(
                BytesIO(content)
            )

            pages = []

            for page in reader.pages:
                text = page.extract_text() or ""
                pages.append(text)

            extracted_text = "\n".join(
                pages
            )

        # Extract DOCX text.
        elif suffix == ".docx":
            from io import BytesIO

            from docx import Document

            document = Document(
                BytesIO(content)
            )

            paragraphs = [
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            ]

            extracted_text = "\n".join(
                paragraphs
            )

        # Extract plain text.
        elif suffix == ".txt":
            extracted_text = content.decode(
                "utf-8",
                errors="ignore",
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX and TXT files are supported.",
            )

        # Remove excess whitespace from extracted content.
        extracted_text = " ".join(
            extracted_text.split()
        )

        # Limit the amount of document text sent to the model.
        extracted_text = extracted_text[:20000]

        if len(extracted_text) < 3:
            raise HTTPException(
                status_code=400,
                detail="Could not extract enough text from the uploaded file.",
            )

        # Run the normal recommendation pipeline.
        result = pipeline.recommend(
            query=extracted_text,
            top_k=50,
            final_k=10,
            related_k=5,
        )

        # Add document metadata expected by the frontend.
        result["input_type"] = "document"
        result["filename"] = filename
        result["extracted_text_length"] = len(
            extracted_text
        )

        return result

    except HTTPException:
        # Preserve intentional HTTP errors.
        raise

    except Exception as exc:
        # Return a readable document-processing error.
        raise HTTPException(
            status_code=500,
            detail=f"Document recommendation failed: {exc}",
        ) from exc