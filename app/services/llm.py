import litellm
from litellm import acompletion
from app.config import settings
import os

# Set the API key for LiteLLM
os.environ["GEMINI_API_KEY"] = settings.LLM_API_KEY  # LiteLLM reads from env

# Persona system prompts — each feels genuinely distinct
PERSONA_PROMPTS = {
    "technical": (
        "You are a precise technical writing engine. Rewrite the provided text to be "
        "structured, jargon-aware, and logically sequenced. Use clear headings where "
        "appropriate, avoid ambiguity, and ensure every sentence adds information value. "
        "Do not use filler words."
    ),
    "business": (
        "You are a professional business communication expert. Rewrite the text to be "
        "persuasive, executive-ready, and results-oriented. Use confident, active voice. "
        "Highlight value propositions and keep sentences concise."
    ),
    "finance": (
        "You are a financial analyst and writer. Rewrite the text with an analytical, "
        "data-oriented tone. Use precise language, reference quantifiable outcomes where "
        "inferred, and maintain a formal, objective style."
    ),
    "simplified": (
        "You are a clarity specialist. Rewrite the text so a 12-year-old can understand it "
        "without losing the core meaning. Use short sentences, common words, and concrete "
        "examples. No jargon."
    ),
    "comedian": (
        "You are a witty writer with sharp comedic timing. Rewrite the text to be light, "
        "clever, and entertaining — without sacrificing the core message. Use wordplay, "
        "irony, and a conversational tone. Keep it punchy."
    ),
    "poet": (
        "You are a creative writing poet. Rewrite the text with expressive, lyrical language. "
        "Use metaphors, rhythm, and vivid imagery to transform the content into something "
        "beautiful and emotionally resonant while preserving the original meaning."
    ),
}

ENHANCE_USER_TEMPLATE = """
Rewrite the following text using the persona guidelines above.

After the rewrite, output a JSON array of changes under the key "change_log" explaining 
what you changed and why. Format your entire response as JSON:
{{
  "enhanced_text": "<your rewritten text>",
  "change_log": [
    {{"change": "description of what changed", "reason": "why"}},
    ...
  ]
}}

TEXT TO REWRITE:
{text}
"""


async def enhance_text(text: str, persona: str) -> dict:
    """Non-streaming enhance — returns enhanced_text + change_log."""
    system_prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["simplified"])

    response = await acompletion(
        model=settings.LLM_PROVIDER,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ENHANCE_USER_TEMPLATE.format(text=text)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    import json
    content = response.choices[0].message.content
    return json.loads(content)


async def stream_enhance_text(text: str, persona: str):
    """
    Streaming version — yields raw token strings.
    The router wraps these in SSE format.
    """
    system_prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["simplified"])

    response = await acompletion(
        model=settings.LLM_PROVIDER,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Rewrite the following text. Only return the rewritten text, nothing else:\n\n{text}",
            },
        ],
        stream=True,
        temperature=0.7,
    )

    async for chunk in response:
        token = chunk.choices[0].delta.content
        if token:
            yield token


async def run_llm(system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
    """
    Generic LLM call used by mindmap, consistency, evolution pipelines.
    Returns raw string content.
    """
    kwargs = {
        "model": settings.LLM_PROVIDER,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = await acompletion(**kwargs)
    return response.choices[0].message.content