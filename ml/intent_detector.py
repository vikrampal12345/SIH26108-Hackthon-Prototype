# Validates whether the supplied text is a BIS procurement-related request.
import re


PRODUCT_TERMS = {
    "cement", "concrete", "steel", "iron", "rebar", "reinforcement",
    "brick", "block", "tile", "pipe", "pipes", "pvc", "hdpe",
    "cable", "wire", "electrical", "helmet", "gloves", "extinguisher",
    "water", "drinking water", "welding", "electrode", "sheet",
    "stainless steel", "road", "pavement", "lighting", "led",
    "pressure vessel", "irrigation", "construction material",
    "aggregate", "sand", "bitumen", "asphalt", "glass", "ceramic"
}

PROCUREMENT_TERMS = {
    "procurement", "purchase", "purchasing", "tender", "tenders",
    "specification", "specifications", "requirement", "requirements",
    "supply", "supplier", "material", "materials", "construction",
    "project", "applicable", "standard", "standards", "compliance",
    "quality", "testing", "test method", "use", "used", "required",
    "selection", "select", "applicable standard"
}

BIS_TERMS = {
    "bis", "bureau of indian standards", "indian standard",
    "indian standards", "is standard", "is code"
}

RESUME_TERMS = {
    "resume", "curriculum vitae", "cv", "education", "experience",
    "skills", "projects", "work experience", "employment",
    "objective", "profile", "linkedin", "github", "achievements"
}

UNRELATED_TERMS = {
    "movie", "song", "joke", "weather", "recipe", "cricket",
    "football", "game", "dating", "politics", "story", "poem"
}


def _normalize(text: str) -> str:
    """Normalize text for matching."""
    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _count_matches(text: str, terms: set[str]) -> int:
    """Count how many relevant terms appear in the text."""
    return sum(1 for term in terms if term in text)


def _looks_like_is_number(text: str) -> bool:
    """Detect common Indian Standard number patterns."""
    return bool(re.search(r"\bis\s*\d{2,6}\b", text))


def _looks_like_resume(text: str) -> bool:
    """Detect resume-like structure instead of procurement requirements."""
    section_hits = _count_matches(text, RESUME_TERMS)

    email_found = bool(
        re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I)
    )

    phone_found = bool(
        re.search(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b", text)
    )

    linkedin_found = "linkedin.com" in text
    github_found = "github.com" in text

    contact_hits = sum([
        email_found,
        phone_found,
        linkedin_found,
        github_found,
    ])

    # Strong resume structure: several resume sections or sections + contact data.
    return section_hits >= 4 or (section_hits >= 2 and contact_hits >= 1)


def validate_text_for_recommendation(
    text: str,
    input_type: str = "text"
) -> tuple[bool, str]:
    """Return whether the input is suitable for BIS recommendation."""
    text = _normalize(text)

    if not text:
        return False, "Please enter a BIS procurement requirement."

    if len(text) < 10:
        return False, "Please provide a more detailed BIS procurement requirement."

    if _looks_like_resume(text):
        return False, (
            "This appears to be a resume or personal profile. "
            "Please provide a procurement requirement, product specification, "
            "material requirement, or BIS standard query."
        )

    unrelated_hits = _count_matches(text, UNRELATED_TERMS)

    if unrelated_hits >= 2:
        return False, (
            "This input is not related to BIS standards or procurement."
        )

    product_hits = _count_matches(text, PRODUCT_TERMS)
    procurement_hits = _count_matches(text, PROCUREMENT_TERMS)
    bis_hits = _count_matches(text, BIS_TERMS)
    is_number = _looks_like_is_number(text)

    # Explicit BIS/IS references are strong evidence of a valid query.
    if is_number and (product_hits >= 1 or procurement_hits >= 1):
        return True, ""

    if bis_hits >= 1 and (product_hits >= 1 or procurement_hits >= 1):
        return True, ""

    # Normal procurement query: product/material + procurement context.
    if product_hits >= 1 and procurement_hits >= 1:
        return True, ""

    # Detailed technical/material queries can be valid even without
    # the exact word "procurement".
    if product_hits >= 2 and procurement_hits >= 1:
        return True, ""

    return False, (
        "Please provide a BIS-related procurement requirement. "
        "Example: 'BIS standard for ordinary Portland cement used "
        "for road construction.'"
    )

# Keep the old backend function name compatible with the new validator.
def detect_input_intent(text: str, input_type: str = "text"):
    return validate_text_for_recommendation(text, input_type)