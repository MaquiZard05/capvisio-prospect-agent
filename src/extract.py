"""Extraction structurée des prospects via LLM Groq."""

import json
from groq import Groq
from src.config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, PROMPT_EXTRACT

client = Groq(api_key=GROQ_API_KEY)


def _call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )
    return response.choices[0].message.content.strip()


def _parse_json(text: str) -> dict | None:
    """Tente d'extraire un JSON depuis la réponse LLM."""
    # Cherche un bloc JSON dans la réponse
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Tente de trouver le premier { ... }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                return None
    return None


def extract_prospect(search_result: dict) -> dict | None:
    """Extrait un prospect structuré depuis un résultat de recherche brut.

    Returns:
        Dict prospect structuré ou None si non pertinent.
    """
    search_text = f"Titre: {search_result['title']}\nURL: {search_result['url']}\nExtrait: {search_result['snippet']}"
    prompt = PROMPT_EXTRACT.format(search_result=search_text)

    try:
        response = _call_llm(prompt)
        data = _parse_json(response)
    except Exception:
        return None

    if not data or not data.get("relevant", False):
        return None

    # Enrichir avec les métadonnées de recherche
    data["source_signal_type"] = search_result.get("signal_type", "")
    data["source_geo"] = search_result.get("geo_zone", "")
    data["raw_title"] = search_result.get("title", "")
    data["raw_snippet"] = search_result.get("snippet", "")

    return data


def extract_prospects(
    search_results: list[dict],
    progress_callback=None,
) -> list[dict]:
    """Extrait les prospects depuis une liste de résultats de recherche.

    Returns:
        Liste de prospects structurés (filtrés, dédupliqués par company_name).
    """
    prospects = []
    seen_companies = set()

    for i, result in enumerate(search_results):
        if progress_callback:
            progress_callback(i, len(search_results))

        prospect = extract_prospect(result)
        if prospect is None:
            continue

        company = prospect.get("company_name", "").lower().strip()
        if company and company in seen_companies:
            continue
        if company:
            seen_companies.add(company)

        prospects.append(prospect)

    return prospects
