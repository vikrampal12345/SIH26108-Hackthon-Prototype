# Strictly validate manual requirements and uploaded documents before BIS recommendation.

import re


# Words that indicate procurement or technical requirement context.
PROCUREMENT_TERMS = {
    "procure",
    "procurement",
    "purchase",
    "purchasing",
    "supply",
    "supplier",
    "tender",
    "bid",
    "quotation",
    "contract",
    "requirement",
    "requirements",
    "specification",
    "specifications",
    "technical specification",
    "boq",
    "bill of quantities",
    "work order",
    "material requirement",
}


# Terms that strongly indicate BIS or Indian Standards context.
BIS_TERMS = {
    "bis",
    "bureau of indian standards",
    "indian standard",
    "indian standards",
    "is standard",
    "is code",
    "is specification",
    "is 269",
    "is 455",
    "is 1489",
    "is 432",
}


# Product/material concepts that exist in the BIS knowledge base.
PRODUCT_TERMS = {
    "cement",
    "concrete",
    "steel",
    "reinforcement bar",
    "reinforcement bars",
    "reinforcement",
    "rebar",
    "wire",
    "cable",
    "cables",
    "electrical cable",
    "pipe",
    "pipes",
    "pvc",
    "pvc-u",
    "tile",
    "tiles",
    "helmet",
    "helmets",
    "safety helmet",
    "gloves",
    "welding electrode",
    "welding electrodes",
    "extinguisher",
    "extinguishers",
    "water",
    "drinking water",
    "packaged drinking water",
    "pressure vessel",
    "pressure vessels",
    "led",
    "lighting",
    "construction material",
    "construction materials",
    "building material",
    "building materials",
    "masonry",
    "brick",
    "bricks",
    "sand",
    "aggregate",
    "asphalt",
    "bitumen",
}


# Terms that commonly identify resumes/CVs.
RESUME_TERMS = {
    "resume",
    "curriculum vitae",
    "curriculum",
    "vitae",
    "cv",
    "work experience",
    "professional experience",
    "employment history",
    "education",
    "educational qualification",
    "qualifications",
    "skills",
    "technical skills",
    "soft skills",
    "projects",
    "project experience",
    "certifications",
    "certificate",
    "career objective",
    "objective",
    "linkedin",
    "github",
    "portfolio",
    "date of birth",
    "dob",
    "experience",
    "internship",
    "internships",
}


# Terms that strongly suggest the uploaded content is unrelated.
UNRELATED_TERMS = {
    "recipe",
    "movie",
    "song",
    "poem",
    "novel",
    "fiction",
    "story",
    "travel itinerary",
    "medical prescription",
    "prescription",
    "exam question",
    "exam paper",
    "personal diary",
}


def _normalize_text(text: str) -> str:
    # Normalize extracted text so validation is consistent.
    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _count_matches(text: str, terms: set[str]) -> int:
    # Count distinct validation signals present in the text.
    return sum(1 for term in terms if term in text)


def _looks_like_resume(text: str) -> bool:
    # Detect a resume using multiple independent resume signals.
    resume_hits = _count_matches(text, RESUME_TERMS)

    return resume_hits >= 2


def detect_input_intent(
    text: str,
    input_type: str = "text",
) -> tuple[bool, str]:
    # Decide whether the supplied content can safely enter the BIS recommendation pipeline.

    normalized = _normalize_text(text)

    # Reject empty or unreadable content.
    if not normalized:
        return (
            False,
            "No readable text was found in the input.",
        )

    # Reject extremely short content.
    if len(normalized) < 10:
        return (
            False,
            "The input is too short to identify a BIS procurement requirement.",
        )

    # Resume detection has priority over product-word detection.
    if _looks_like_resume(normalized):
        return (
            False,
            "This document appears to be a resume or CV, not a BIS procurement requirement.",
        )

    # Reject clearly unrelated documents.
    unrelated_hits = _count_matches(
        normalized,
        UNRELATED_TERMS,
    )

    if unrelated_hits >= 2:
        return (
            False,
            "This content does not appear to be a BIS procurement requirement.",
        )

    procurement_hits = _count_matches(
        normalized,
        PROCUREMENT_TERMS,
    )

    bis_hits = _count_matches(
        normalized,
        BIS_TERMS,
    )

    product_hits = _count_matches(
        normalized,
        PRODUCT_TERMS,
    )

    # Uploaded documents use a stricter validation rule.
    if input_type == "document":

        # Product + procurement context is valid.
        if product_hits >= 1 and procurement_hits >= 1:
            return (
                True,
                "Valid BIS procurement document.",
            )

        # Product + explicit BIS context is also valid.
        if product_hits >= 1 and bis_hits >= 1:
            return (
                True,
                "Valid BIS-related procurement document.",
            )

        # Several independent BIS signals are sufficient.
        if bis_hits >= 2:
            return (
                True,
                "Valid BIS-related document.",
            )

        # Everything else is rejected.
        return (
            False,
            "Uploaded document does not appear to contain a BIS procurement requirement.",
        )

    # Manual text can be shorter but still needs a recognizable product/context.

    if product_hits >= 1 and procurement_hits >= 1:
        return (
            True,
            "Valid BIS procurement requirement.",
        )

    if product_hits >= 1 and bis_hits >= 1:
        return (
            True,
            "Valid BIS-related requirement.",
        )

    if bis_hits >= 1 and procurement_hits >= 1:
        return (
            True,
            "Valid BIS procurement requirement.",
        )

    return (
        False,
        "This input does not appear to contain a BIS procurement requirement.",
    )