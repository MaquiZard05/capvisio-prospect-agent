"""Scoring et qualification des prospects via LLM."""

import json
from groq import Groq
from src.config import (
    GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    PROMPT_SCORE, CAPVISIO_DESCRIPTION, SCORE_THRESHOLD,
)

client = Groq(api_key=GROQ_API_KEY)


def score_prospect(prospect: dict) -> dict:
    """Score un prospect et ajoute les données de qualification."""
    prospect_text = json.dumps(prospect, ensure_ascii=False, indent=2)
    prompt = PROMPT_SCORE.format(
        prospect_data=prospect_text,
        capvisio_desc=CAPVISIO_DESCRIPTION,
    )

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        text = response.choices[0].message.content.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            scoring = json.loads(text[start:end])
            prospect["score"] = scoring.get("score", 0)
            prospect["score_breakdown"] = scoring.get("score_breakdown", {})
            prospect["deal_estimate"] = scoring.get("deal_estimate", "N/A")
            prospect["approach_angle"] = scoring.get("approach_angle", "")
            prospect["priority"] = scoring.get("priority", "cold")
            prospect["qualified"] = prospect["score"] >= SCORE_THRESHOLD
            return prospect
    except Exception:
        pass

    # Fallback : score neutre
    prospect["score"] = 0
    prospect["score_breakdown"] = {}
    prospect["deal_estimate"] = "N/A"
    prospect["approach_angle"] = ""
    prospect["priority"] = "cold"
    prospect["qualified"] = False
    return prospect


def score_prospects(prospects: list[dict], progress_callback=None) -> list[dict]:
    """Score une liste de prospects et les trie par score décroissant."""
    for i, prospect in enumerate(prospects):
        if progress_callback:
            progress_callback(i, len(prospects))
        score_prospect(prospect)

    prospects.sort(key=lambda p: p.get("score", 0), reverse=True)
    return prospects
