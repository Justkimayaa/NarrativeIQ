import json
from typing import List, Dict, Any
from app.services.nlp import extract_entities, extract_themes_heuristic
from app.services.llm import run_llm


RELATIONSHIP_SYSTEM_PROMPT = """You are a narrative analysis engine. 
Given a list of entities extracted from a story/script and the original text, 
identify meaningful relationships between entities.

Return ONLY valid JSON in this exact format:
{
  "edges": [
    {"source": "entity_id_1", "target": "entity_id_2", "label": "RelationshipType"}
  ],
  "entity_attributes": {
    "entity_id": {"age": "optional", "role": "optional", "trait": "optional"}
  },
  "summary": "2-3 sentence summary of the narrative",
  "themes": ["theme1", "theme2"]
}

Relationship types can be: Friend, Enemy, Rival, Mentor, Student, Family, Employer, 
Romantic, Conflict, Ally, Neutral, Located_In, Part_Of, Leads_To, etc.
Only include relationships that are clearly supported by the text.
"""


async def build_graph(text: str) -> Dict[str, Any]:
    """
    Full mindmap pipeline:
    1. spaCy extracts entities (fast, local)
    2. LLM infers relationships + enriches attributes
    3. Returns React Flow compatible {nodes, edges} + summary + themes
    """

    # Step 1: spaCy NER
    raw_entities = extract_entities(text)
    heuristic_themes = extract_themes_heuristic(text)

    if not raw_entities:
        # Fallback: ask LLM to extract everything if spaCy found nothing
        return await _full_llm_graph(text)

    # Step 2: LLM for relationships
    entity_list_str = json.dumps(
        [{"id": e["id"], "label": e["label"], "type": e["type"]} for e in raw_entities],
        indent=2,
    )

    user_prompt = f"""
Entities extracted from the text:
{entity_list_str}

Heuristic themes detected: {heuristic_themes}

Original text (first 4000 chars):
{text[:4000]}

Now identify relationships between these entities and enrich their attributes.
"""

    llm_output = await run_llm(RELATIONSHIP_SYSTEM_PROMPT, user_prompt, json_mode=True)

    try:
        llm_data = json.loads(llm_output)
    except json.JSONDecodeError:
        llm_data = {"edges": [], "entity_attributes": {}, "summary": "", "themes": heuristic_themes}

    # Step 3: Merge entity attributes from LLM into spaCy entities
    enriched_attrs = llm_data.get("entity_attributes", {})
    nodes = []
    for entity in raw_entities:
        entity["attributes"] = enriched_attrs.get(entity["id"], {})
        nodes.append({
            "id": entity["id"],
            "label": entity["label"],
            "type": entity["type"],
            "attributes": entity["attributes"],
        })

    edges = llm_data.get("edges", [])

    # Validate edges — only keep edges where both nodes exist
    node_ids = {n["id"] for n in nodes}
    valid_edges = [e for e in edges if e["source"] in node_ids and e["target"] in node_ids]

    themes = llm_data.get("themes") or heuristic_themes

    return {
        "nodes": nodes,
        "edges": valid_edges,
        "summary": llm_data.get("summary", ""),
        "themes": themes[:6],  # cap at 6
    }


async def _full_llm_graph(text: str) -> Dict[str, Any]:
    """Fallback when spaCy finds no entities — let LLM do everything."""
    system = """You are a narrative graph builder. Extract entities and relationships from the text.
Return ONLY JSON:
{
  "nodes": [{"id": "slug", "label": "Name", "type": "character|location|theme|event", "attributes": {}}],
  "edges": [{"source": "id1", "target": "id2", "label": "RelationType"}],
  "summary": "...",
  "themes": ["..."]
}"""
    result = await run_llm(system, f"Extract from this text:\n\n{text[:5000]}", json_mode=True)
    try:
        return json.loads(result)
    except Exception:
        return {"nodes": [], "edges": [], "summary": "Could not parse narrative.", "themes": []}