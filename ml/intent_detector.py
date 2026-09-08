# Validate whether the supplied text is a BIS procurement-related request.

import re


# Common products and technical domains found in BIS procurement requirements.
PRODUCT_TERMS = {
    # Construction materials
    "cement",
    "concrete",
    "mortar",
    "aggregate",
    "aggregates",
    "sand",
    "brick",
    "bricks",
    "block",
    "blocks",
    "tile",
    "tiles",
    "ceramic",
    "ceramics",
    "stone",
    "stones",
    "glass",
    "construction material",
    "construction materials",
    "building material",
    "building materials",
    "precast",
    "paving",
    "pavement",
    "flooring",

    # Steel and metals
    "steel",
    "iron",
    "rebar",
    "rebars",
    "bar",
    "bars",
    "rod",
    "rods",
    "wire",
    "wires",
    "reinforcement",
    "reinforcing",
    "structural steel",
    "steel section",
    "steel sections",
    "sheet",
    "sheets",
    "plate",
    "plates",
    "strip",
    "strips",
    "stainless steel",
    "alloy steel",
    "carbon steel",
    "mild steel",
    "galvanized steel",
    "galvanised steel",

    # Pipes and water systems
    "pipe",
    "pipes",
    "piping",
    "pipeline",
    "pipelines",
    "pvc",
    "pvc-o",
    "pvc-u",
    "cpvc",
    "hdpe",
    "grP",
    "grp",
    "grP pipe",
    "grp pipe",
    "fitting",
    "fittings",
    "valve",
    "valves",
    "water",
    "drinking water",
    "potable water",
    "irrigation",
    "water supply",
    "water distribution",
    "wastewater",
    "sewer",
    "sewerage",

    # Electrical
    "electrical",
    "electric",
    "cable",
    "cables",
    "conductor",
    "conductors",
    "cord",
    "cords",
    "switch",
    "switches",
    "socket",
    "sockets",
    "plug",
    "plugs",
    "transformer",
    "transformers",
    "lighting",
    "lamp",
    "lamps",
    "led",
    "led module",
    "led modules",
    "electrical equipment",
    "electrical installation",
    "electrical installations",

    # Welding
    "welding",
    "weld",
    "welder",
    "welders",
    "weldment",
    "weldments",
    "electrode",
    "electrodes",
    "welding electrode",
    "welding electrodes",
    "welding consumable",
    "welding consumables",
    "consumable",
    "consumables",
    "welding wire",
    "welding wires",
    "welding cable",
    "welding cables",
    "welding equipment",
    "welding equipment",
    "welding material",
    "welding materials",
    "welding process",
    "welding processes",
    "welding machine",
    "welding machines",

    # Safety and fire
    "helmet",
    "helmets",
    "glove",
    "gloves",
    "safety helmet",
    "safety helmets",
    "safety gloves",
    "safety equipment",
    "safety equipments",
    "safety gear",
    "fire extinguisher",
    "fire extinguishers",
    "extinguisher",
    "extinguishers",
    "fire protection",
    "fire safety",
    "ppe",
    "personal protective equipment",
    "protective equipment",
    "protective gear",

    # Roads and infrastructure
    "road",
    "roads",
    "road construction",
    "road maintenance",
    "highway",
    "highways",
    "pavement",
    "pavements",
    "bitumen",
    "bitumens",
    "asphalt",
    "asphalt paver",
    "asphalt pavers",
    "road equipment",
    "road machinery",

    # Industrial products
    "pressure vessel",
    "pressure vessels",
    "boiler",
    "boilers",
    "machine",
    "machines",
    "machinery",
    "equipment",
    "equipments",
    "industrial equipment",
    "industrial equipments",
    "industrial material",
    "industrial materials",
    "industrial product",
    "industrial products",
    "component",
    "components",
    "device",
    "devices",
    "instrument",
    "instruments",
    "industrial safety equipment",

    # Plastics / rubber / packaging
    "plastic",
    "plastics",
    "rubber",
    "rubbers",
    "polymer",
    "polymers",
    "packaging",
    "package",
    "packages",
    "container",
    "containers",
    "bottle",
    "bottles",
    "pouch",
    "pouches",

    # Food / water / consumer products
    "food",
    "foods",
    "drinking water",
    "packaged drinking water",
    "natural mineral water",
    "mineral water",
    "textile",
    "textiles",
    "fabric",
    "fabrics",
    "furniture",
    "medical equipment",
    "medical devices",

    # Other technical materials
    "chemical",
    "chemicals",
    "coating",
    "coatings",
    "paint",
    "paints",
    "adhesive",
    "adhesives",
    "sealant",
    "sealants",
    "roofing",
    "roof",
    "roofs",
}


# Common words and phrases indicating procurement or technical requirement context.
PROCUREMENT_TERMS = {
    # Procurement actions
    "procure",
    "procures",
    "procured",
    "procurement",
    "purchase",
    "purchases",
    "purchased",
    "purchasing",
    "buy",
    "buying",
    "source",
    "sourcing",
    "order",
    "ordering",
    "supply",
    "supplied",
    "supplier",
    "suppliers",
    "vendor",
    "vendors",
    "tender",
    "tenders",
    "bid",
    "bids",
    "bidding",
    "contract",
    "contracts",
    "contractor",
    "contractors",

    # Requirement language
    "need",
    "needs",
    "needed",
    "require",
    "requires",
    "required",
    "requirement",
    "requirements",
    "specification",
    "specifications",
    "applicable",
    "applicability",
    "standard",
    "standards",
    "compliance",
    "compliant",
    "quality",
    "testing",
    "test",
    "tests",
    "test method",
    "test methods",
    "testing method",
    "testing methods",
    "selection",
    "select",
    "selected",
    "use",
    "used",
    "usage",
    "application",
    "applications",
    "installation",
    "installations",

    # Project / engineering context
    "construction",
    "project",
    "projects",
    "building",
    "buildings",
    "facility",
    "facilities",
    "industrial",
    "commercial",
    "residential",
    "manufacturing",
    "fabrication",
    "engineering",
    "infrastructure",
    "site",
    "sites",
    "work",
    "works",
    "production",
    "plant",
    "plants",

    # Technical procurement context
    "material",
    "materials",
    "equipment",
    "product",
    "products",
    "component",
    "components",
    "device",
    "devices",
    "system",
    "systems",
    "accessory",
    "accessories",
    "consumable",
    "consumables",
    "performance",
    "safety",
    "marking",
    "inspection",
    "inspect",
    "certification",
    "certificate",
    "certificates",
    "approval",
    "approvals",
    "testing requirement",
    "technical requirement",
    "technical requirements",
    "technical specification",
    "technical specifications",
}


# Common BIS and Indian Standard terms.
BIS_TERMS = {
    "bis",
    "bureau of indian standards",
    "indian standard",
    "indian standards",
    "is standard",
    "is standards",
    "is code",
    "is codes",
    "bis standard",
    "bis standards",
    "bis code",
    "bis codes",
    "indian standard code",
    "indian standards code",
    "indian standard specification",
    "indian standards specification",
    "bis specification",
    "bis specifications",
}


# Resume/profile terms used to reject clearly unrelated personal documents.
RESUME_TERMS = {
    "resume",
    "résumé",
    "curriculum vitae",
    "cv",
    "education",
    "experience",
    "skills",
    "projects",
    "work experience",
    "employment",
    "objective",
    "profile",
    "linkedin",
    "github",
    "achievements",
    "certifications",
    "qualification",
    "qualifications",
    "personal details",
}


# Clearly unrelated topics used as negative signals.
UNRELATED_TERMS = {
    "movie",
    "movies",
    "song",
    "songs",
    "joke",
    "jokes",
    "weather",
    "recipe",
    "recipes",
    "cricket",
    "football",
    "game",
    "games",
    "gaming",
    "dating",
    "politics",
    "story",
    "stories",
    "poem",
    "poetry",
    "celebrity",
    "music",
    "travel",
}


def _normalize(text: str) -> str:
    # Normalize input text before keyword and pattern matching.
    text = str(text or "").lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def _count_matches(
    text: str,
    terms: set[str],
) -> int:
    # Count complete words or phrases without accidental substring matches.
    count = 0

    for term in terms:
        pattern = rf"(?<!\w){re.escape(term.lower())}(?!\w)"

        if re.search(
            pattern,
            text,
        ):
            count += 1

    return count


def _looks_like_is_number(
    text: str,
) -> bool:
    # Detect common Indian Standard number references such as IS 269.
    return bool(
        re.search(
            r"\bis\s*/?\s*(?:iec\s*)?\d{2,6}\b",
            text,
            re.IGNORECASE,
        )
    )


def _looks_like_resume(
    text: str,
) -> bool:
    # Detect resume-like structure instead of procurement requirements.
    section_hits = _count_matches(
        text,
        RESUME_TERMS,
    )

    email_found = bool(
        re.search(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            text,
            re.IGNORECASE,
        )
    )

    phone_found = bool(
        re.search(
            r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
            text,
        )
    )

    linkedin_found = (
        "linkedin.com" in text
    )

    github_found = (
        "github.com" in text
    )

    contact_hits = sum(
        [
            email_found,
            phone_found,
            linkedin_found,
            github_found,
        ]
    )

    # Strong resume structure requires multiple resume indicators.
    return (
        section_hits >= 4
        or (
            section_hits >= 2
            and contact_hits >= 1
        )
    )


def validate_text_for_recommendation(
    text: str,
    input_type: str = "text",
) -> tuple[bool, str]:
    # Validate that the input is suitable for BIS recommendation.
    text = _normalize(text)

    if not text:
        return (
            False,
            "Please enter a BIS procurement requirement.",
        )

    if len(text) < 10:
        return (
            False,
            "Please provide a more detailed BIS procurement requirement.",
        )

    if _looks_like_resume(text):
        return (
            False,
            "This appears to be a resume or personal profile. "
            "Please provide a procurement requirement, product specification, "
            "material requirement, or BIS standard query.",
        )

    unrelated_hits = _count_matches(
        text,
        UNRELATED_TERMS,
    )

    if unrelated_hits >= 2:
        return (
            False,
            "This input is not related to BIS standards or procurement.",
        )

    product_hits = _count_matches(
        text,
        PRODUCT_TERMS,
    )

    procurement_hits = _count_matches(
        text,
        PROCUREMENT_TERMS,
    )

    bis_hits = _count_matches(
        text,
        BIS_TERMS,
    )

    is_number = _looks_like_is_number(
        text
    )

    # A direct IS-number query with procurement or product context is valid.
    if (
        is_number
        and (
            product_hits >= 1
            or procurement_hits >= 1
        )
    ):
        return True, ""

    # An explicit BIS query with procurement or product context is valid.
    if (
        bis_hits >= 1
        and (
            product_hits >= 1
            or procurement_hits >= 1
        )
    ):
        return True, ""

    # A standard product/material procurement query is valid.
    if (
        product_hits >= 1
        and procurement_hits >= 1
    ):
        return True, ""

    # Detailed product descriptions with multiple product terms are valid.
    if (
        product_hits >= 2
        and procurement_hits >= 1
    ):
        return True, ""

    return (
        False,
        "Please provide a BIS-related procurement requirement. "
        "Example: 'BIS standard for ordinary Portland cement used "
        "for road construction.'",
    )


def detect_input_intent(
    text: str,
    input_type: str = "text",
):
    # Keep the backend's existing function name compatible with the validator.
    return validate_text_for_recommendation(
        text,
        input_type,
    )