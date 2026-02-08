"""
LLM-generated intervention text with strict grounding. Uses only the provided
structured data; no invented numbers or medical claims. Falls back to None when
API key is missing or the call fails so the caller can use interpolated text.
"""

import json
import logging
import re
from typing import Any

from app.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

USER_PROMPT_TEMPLATE = """You are a health data narrator. Turn the following analysis result into one short intervention sentence and one success criterion.

Rules:
- Use ONLY the numbers and labels in the JSON below. Do not add any new numbers, percentages, or statistics.
- Do not give medical advice. This is decision support only.
- Write 1-2 sentences for "intervention" and one short phrase for "success". Be direct and personal (e.g. "Your data shows...", "For you,...").
- Reply with valid JSON only, no other text: {"intervention": "...", "success": "..."}

Data:
{payload}"""


def generate_intervention_text(payload: dict[str, Any]) -> dict[str, str] | None:
    """
    Ask the LLM for intervention + success text from a single card's structured data.
    Returns {"intervention": "...", "success": "..."} or None on failure/missing key.
    """
    if not GEMINI_API_KEY:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        contents = USER_PROMPT_TEMPLATE.format(payload=json.dumps(payload, default=str, indent=0))
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
        )
        text = (response.text or "").strip()
        # Strip markdown code block if present
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
            if match:
                text = match.group(1).strip()
        out = json.loads(text)
        if isinstance(out, dict) and "intervention" in out and "success" in out:
            return {"intervention": str(out["intervention"]), "success": str(out["success"])}
        return None
    except Exception as e:
        logger.warning("LLM intervention generation failed: %s", e)
        return None
