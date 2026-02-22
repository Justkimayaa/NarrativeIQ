import spacy
from typing import List, Dict, Any

# Load the small English model.
# Run once after pip install: python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Auto-download if missing (useful in CI/deploy)
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# spaCy entity type → our graph node type mapping
ENTITY_TYPE_MAP = {
    "PERSON": "character",
    "GPE": "location",      # Geopolitical entity (cities, countries)
    "LOC": "location",
    "ORG": "character",     # Treat orgs as character-like nodes
    "EVENT": "event",
    "WORK_OF_ART": "object",
    "FAC": "location",      # Facilities
}


def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Run spaCy NER on text and return a list of unique entities.
    Each entity: {id, label, type, count}
    count = how many times mentioned (useful for sizing nodes in the graph)
    """
    # spaCy has a 1M char limit — chunk if needed
    doc = nlp(text[:100000])

    seen: Dict[str, Dict] = {}

    for ent in doc.ents:
        entity_type = ENTITY_TYPE_MAP.get(ent.label_)
        if not entity_type:
            continue

        key = ent.text.strip().lower()
        label = ent.text.strip()

        if key in seen:
            seen[key]["count"] += 1
        else:
            seen[key] = {
                "id": key.replace(" ", "_"),
                "label": label,
                "type": entity_type,
                "count": 1,
                "attributes": {},
            }

    return list(seen.values())


def extract_themes_heuristic(text: str) -> List[str]:
    """
    Basic theme detection using keyword frequency.
    The LLM will refine this — this is just a pre-processing hint.
    """
    theme_keywords = {
        "Friendship": ["friend", "friendship", "together", "bond", "companion"],
        "Conflict": ["fight", "conflict", "battle", "argue", "enemy", "war"],
        "Love": ["love", "romance", "heart", "affection", "kiss", "beloved"],
        "Betrayal": ["betray", "backstab", "deceive", "lie", "cheat", "trust"],
        "Growth": ["grow", "learn", "change", "evolve", "transform", "journey"],
        "Loss": ["loss", "grief", "death", "mourn", "miss", "gone"],
        "Power": ["power", "control", "authority", "rule", "dominate", "influence"],
        "Redemption": ["redeem", "forgive", "second chance", "atone", "guilt"],
    }

    text_lower = text.lower()
    found_themes = []

    for theme, keywords in theme_keywords.items():
        score = sum(text_lower.count(kw) for kw in keywords)
        if score >= 2:
            found_themes.append((theme, score))

    # Return top 5 by frequency
    found_themes.sort(key=lambda x: x[1], reverse=True)
    return [t[0] for t in found_themes[:5]]