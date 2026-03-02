"""
LLM-generated intervention text with strict grounding. Uses only the provided
structured data; no invented numbers or medical claims. Falls back to None when
API key is missing or the call fails so the caller can use interpolated text.
Supports OpenAI (default) via OPENAI_API_KEY.
"""

import json
import logging
import re
from typing import Any

from app.config import OPENAI_API_KEY, OPENAI_MODEL

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
    if not OPENAI_API_KEY:
        return None
    if not isinstance(payload, dict) or len(payload) == 0:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        content = USER_PROMPT_TEMPLATE.format(payload=json.dumps(payload, default=str, indent=0))
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You output valid JSON only. No markdown, no extra text."},
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_object"},
        )
        text = (response.choices[0].message.content or "").strip()
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
