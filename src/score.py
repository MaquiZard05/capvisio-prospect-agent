"""Scoring et qualification des prospects via LLM Gemini (batching + cache)."""

import json
import time
from google import genai
from src.config import (
    GOOGLE_API_KEY, MODEL_SCORE, LLM_MAX_TOKENS, LLM_SLEEP,
    BATCH_SIZE_SCORE, CAPVISIO_DESCRIPTION, SCORE_THRESHOLD, PROMPT_SCORE_BATCH,
)

client = None

def _get_client():
    global client
    if client is None:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    return client


def _call_llm(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries + 1):
        try:
            print(f"   [SCORE] Appel LLM ({MODEL_SCORE}), tentative {attempt+1}/{max_retries+1}")
            response = _get_client().models.generate_content(
                model=MODEL_SCORE,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=LLM_MAX_TOKENS,
                ),
            )
            text = response.text.strip() if response.text else ""
            print(f"   [SCORE] Réponse reçue ({len(text)} chars)")
            return text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries:
                import re
                wait = 20 + attempt * 10
                m = re.search(r"retryDelay.*?(\d+)", error_str)
                if m:
                    wait = int(m.group(1)) + 2
                print(f"   [SCORE] Rate limit 429 — pause {wait}s (tentative {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                print(f"   [SCORE] Erreur LLM: {e}")
                return ""
    return ""


def _parse_json(text: str) -> list | None:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        result = json.loads(text)
        return result if isinstance(result, list) else [result]
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return [json.loads(text[start:end])]
            except json.JSONDecodeError:
                pass
    return None


def score_prospects(prospects: list[dict], progress_callback=None, batch_size: int = BATCH_SIZE_SCORE) -> list[dict]:
    """Score les prospects par batch. Skip ceux déjà scorés."""
    # Séparer : déjà scorés vs à scorer
    to_score = [p for p in prospects if not p.get("_scored")]
    already_scored = [p for p in prospects if p.get("_scored")]

    if not to_score:
        print("   [SCORE] Tous les prospects sont déjà scorés, skip.")
        prospects.sort(key=lambda p: p.get("score", 0), reverse=True)
        return prospects

    print(f"   [SCORE] {len(to_score)} à scorer, {len(already_scored)} déjà traités")

    total_batches = max(1, (len(to_score) + batch_size - 1) // batch_size)

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(to_score))
        batch = to_score[start:end]

        if progress_callback:
            progress_callback(batch_idx, total_batches)

        batch_text = json.dumps(
            [{"company_name": p.get("company_name"), "signal_type": p.get("signal_type"),
              "location": p.get("location"), "project_details": p.get("project_details")}
             for p in batch],
            ensure_ascii=False, indent=2
        )

        prompt = PROMPT_SCORE_BATCH.format(
            capvisio_desc=CAPVISIO_DESCRIPTION,
            prospects_batch=batch_text,
        )

        try:
            print(f"   [SCORE] Batch {batch_idx+1}/{total_batches} — {len(batch)} prospects")
            response = _call_llm(prompt)
            scored_list = _parse_json(response)
            if scored_list:
                print(f"   [SCORE] Batch {batch_idx+1}: {len(scored_list)} scores reçus")
            else:
                print(f"   [SCORE] Batch {batch_idx+1}: parsing JSON échoué ou vide")
        except Exception as e:
            print(f"   [SCORE] Erreur scoring batch {batch_idx+1}: {e}")
            scored_list = None

        if scored_list:
            score_map = {s.get("company_name", "").lower().strip(): s for s in scored_list if isinstance(s, dict)}
            for p in batch:
                name = p.get("company_name", "").lower().strip()
                scored = score_map.get(name, {})
                p["score"] = scored.get("score", 0)
                breakdown = scored.get("score_breakdown", {})
                p["score_breakdown"] = {
                    "pertinence": breakdown.get("pertinence_metier", breakdown.get("pertinence", 0)),
                    "deal_size": breakdown.get("taille_deal", breakdown.get("deal_size", 0)),
                    "urgence": breakdown.get("urgence_timing", breakdown.get("urgence", 0)),
                    "geo": breakdown.get("proximite_geo", breakdown.get("geo", 0)),
                    "signal_quality": breakdown.get("qualite_signal", breakdown.get("signal_quality", 0)),
                }
                p["deal_estimate"] = scored.get("deal_estimate_keur", "N/A")
                p["approach_angle"] = scored.get("approach_angle", "")
                p["priority"] = scored.get("priority", "cold")
                p["qualified"] = p["score"] >= SCORE_THRESHOLD
                p["_scored"] = True
        else:
            for p in batch:
                p["score"] = 0
                p["score_breakdown"] = {}
                p["deal_estimate"] = "N/A"
                p["approach_angle"] = ""
                p["priority"] = "cold"
                p["qualified"] = False
                p["_scored"] = True

        # Pause entre les batches
        if batch_idx < total_batches - 1:
            print(f"   [SCORE] Pause {LLM_SLEEP}s (rate limit)...")
            time.sleep(LLM_SLEEP)

    print(f"   [SCORE] Terminé: {len(prospects)} prospects scorés")
    prospects.sort(key=lambda p: p.get("score", 0), reverse=True)
    return prospects
