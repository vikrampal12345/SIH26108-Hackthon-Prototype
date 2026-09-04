# FastAPI backend for BIS text and document recommendation with strict input validation.

from pathlib import Path
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from docx import Document

from backend.schemas import RecommendationRequest
from ml.pipeline import BISRecommendationPipeline
from ml.intent_detector import detect_input_intent
# Allow the deployed Vercel frontend and local development frontend to call FastAPI.
from fastapi.middleware.cors import CORSMiddleware



# Create the FastAPI application.
app = FastAPI(
    title="BIS Standard Recommendation API",
    description="AI-powered BIS Indian Standard recommendation system",
    version="1.0.0",
)


# Allow the local frontend to call the backend.
# Allow the deployed Vercel frontend and local development frontend to call FastAPI.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sih-26108-hackthon-prototype.vercel.app",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the recommendation pipeline once when the server starts.
pipeline = BISRecommendationPipeline()


# Maximum uploaded file size: 10 MB.
MAX_FILE_SIZE = 10 * 1024 * 1024


# Supported document formats.
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


def validate_text_for_recommendation(
    text: str,
    input_type: str = "text",
) -> None:
    # Validate content before MiniLM, FAISS, and hybrid ranking are executed.

    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text was found in the input.",
        )

    is_valid, message = detect_input_intent(
        text,
        input_type,
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=message,
        )


def extract_text_from_pdf(file_path: str) -> str:
    # Extract selectable text from a PDF file.

    try:
        reader = PdfReader(file_path)

        pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        return "\n".join(pages).strip()

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read PDF file: {exc}",
        )


def extract_text_from_docx(file_path: str) -> str:
    # Extract paragraph text from a DOCX file.

    try:
        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n".join(paragraphs).strip()

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read DOCX file: {exc}",
        )


def extract_text_from_txt(file_path: str) -> str:
    # Read plain text from a TXT file.

    try:
        return Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore",
        ).strip()

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read TXT file: {exc}",
        )


def extract_text_from_file(
    file_path: str,
    filename: str,
) -> str:
    # Select the correct extractor based on the uploaded extension.

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    raise HTTPException(
        status_code=400,
        detail="Unsupported file type. Please upload PDF, DOCX, or TXT.",
    )


@app.get("/")
def root():
    # Return basic information about the backend.
    return {
        "message": "BIS Standard Recommendation API is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    # Provide a simple backend health check.
    return {
        "status": "ok",
        "service": "BIS Standard Recommendation API",
    }


@app.post("/recommend")
def recommend(
    request: RecommendationRequest,
):
    # Validate manual text before running the recommendation engine.

    query = request.query.strip()

    validate_text_for_recommendation(
        query,
        "text",
    )

    try:
        result = pipeline.recommend(query)

        result["query"] = query
        result["input_type"] = "text"
        result["filename"] = None
        result["extracted_text_length"] = len(query)

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation failed: {exc}",
        )


@app.post("/recommend-document")
async def recommend_document(
    file: UploadFile = File(...),
):
    # Validate, extract, and classify an uploaded document before recommendation.

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was selected.",
        )

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    # Reject unsupported formats immediately.
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF, DOCX, or TXT.",
        )

    # Read the upload.
    file_content = await file.read()

    # Reject empty files.
    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    # Enforce the 10 MB limit.
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum allowed size is 10 MB.",
        )

    temp_path = None

    try:
        # Create a temporary file for document extraction.
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            temp_file.write(file_content)

            temp_path = Path(temp_file.name)

        # Extract the document text.
        extracted_text = extract_text_from_file(
            str(temp_path),
            filename,
        )

        # Reject documents with no readable text.
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text could be extracted from this document. "
                    "Please upload a text-based PDF, DOCX, or TXT procurement document."
                ),
            )

        # Keep a bounded amount of text for the AI pipeline.
        extracted_text = extracted_text[:20000]

        # IMPORTANT:
        # Uploaded documents are validated as "document", not "text".
        validate_text_for_recommendation(
            extracted_text,
            "document",
        )

        # Only valid BIS procurement documents reach the recommendation engine.
        result = pipeline.recommend(
            extracted_text,
        )

        result["query"] = extracted_text
        result["input_type"] = "document"
        result["filename"] = filename
        result["extracted_text_length"] = len(extracted_text)

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document recommendation failed: {exc}",
        )

    finally:
        # Remove the temporary file after processing.
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass