"""Extraction structurée des prospects via LLM Gemini (batching + cache)."""

import json
import time
from google import genai
from src.config import (
    GOOGLE_API_KEY, MODEL_EXTRACT, MODEL_EXTRACT_FALLBACK, LLM_MAX_TOKENS, LLM_SLEEP,
    CAPVISIO_DESCRIPTION, PROMPT_EXTRACT_BATCH,
)

# Bascule automatique si le modèle principal est épuisé
_active_model = MODEL_EXTRACT

client = genai.Client(api_key=GOOGLE_API_KEY)


def _call_llm(prompt: str, max_retries: int = 2) -> str:
    """Appel LLM avec retry sur 429 + fallback modèle."""
    global _active_model
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=_active_model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=LLM_MAX_TOKENS,
                ),
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                # Si quota journalier épuisé, basculer sur le fallback
                if "PerDay" in error_str and _active_model != MODEL_EXTRACT_FALLBACK:
                    print(f"   ⚠️ Quota jour épuisé pour {_active_model}, bascule → {MODEL_EXTRACT_FALLBACK}")
                    _active_model = MODEL_EXTRACT_FALLBACK
                    continue
                if attempt < max_retries:
                    print(f"   ⏳ Rate limit — pause 15s (tentative {attempt+1}/{max_retries})")
                    time.sleep(15)
                else:
                    raise
            else:
                raise
    return ""


def _parse_json(text: str) -> list | dict | None:
    """Parse le JSON du LLM avec fallback regex."""
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
        # Chercher un array [...]
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        # Chercher un objet {...}
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                result = json.loads(text[start:end])
                return [result] if isinstance(result, dict) else result
            except json.JSONDecodeError:
                pass
    return None


def _pre_filter(result: dict) -> bool:
    """Filtre rapide pour éliminer le bruit avant l'appel LLM."""
    noise_domains = ["wikipedia.org", "wiktionary.org", "larousse.fr", "dictionnaire",
                     "service-public.fr", "pagesjaunes.fr", "allocine.fr", "senscritique.com",
                     "indeed.com", "linkedin.com/jobs", "pole-emploi.fr"]
    url = result.get("url", "").lower()
    title = result.get("title", "").lower()

    for domain in noise_domains:
        if domain in url:
            return False

    noise_words = ["définition", "dictionnaire", "conjugaison", "synonyme", "wikipédia", "série tv"]
    for word in noise_words:
        if word in title:
            return False

    return True


def extract_prospects(
    search_results: list[dict],
    existing_prospects: list[dict] | None = None,
    progress_callback=None,
    batch_size: int = 5,
) -> list[dict]:
    """Extrait les prospects par batch. Skip ceux déjà extraits."""
    # Récupérer les entreprises déjà connues
    seen_companies = set()
    if existing_prospects:
        for p in existing_prospects:
            name = p.get("company_name", "").lower().strip()
            if name:
                seen_companies.add(name)

    # Pré-filtrage du bruit
    filtered_results = [r for r in search_results if _pre_filter(r)]
    print(f"   Pré-filtre : {len(search_results)} → {len(filtered_results)} résultats pertinents")

    if not filtered_results:
        return list(existing_prospects or [])

    prospects = list(existing_prospects or [])
    total_batches = max(1, (len(filtered_results) + batch_size - 1) // batch_size)

    for batch_idx in range(total_batches):
        start_i = batch_idx * batch_size
        end_i = min(start_i + batch_size, len(filtered_results))
        batch = filtered_results[start_i:end_i]

        if progress_callback:
            progress_callback(batch_idx, total_batches)

        # Formater le batch pour le prompt
        batch_text = ""
        for i, r in enumerate(batch, 1):
            batch_text += f"\n--- Résultat {i} ---\n"
            batch_text += f"Titre: {r['title']}\n"
            batch_text += f"URL: {r['url']}\n"
            batch_text += f"Extrait: {r['snippet']}\n"

        prompt = PROMPT_EXTRACT_BATCH.format(
            capvisio_desc=CAPVISIO_DESCRIPTION,
            search_results_batch=batch_text,
        )

        try:
            response = _call_llm(prompt)
            extracted = _parse_json(response)
        except Exception as e:
            print(f"   ⚠️ Erreur batch {batch_idx+1}: {e}")
            extracted = None

        if extracted and isinstance(extracted, list):
            for item in extracted:
                if not isinstance(item, dict):
                    continue
                if not item.get("relevant", True):
                    continue

                company = item.get("company_name", "").lower().strip()
                if not company or company in seen_companies:
                    continue
                seen_companies.add(company)

                # Métadonnées de recherche
                item["source_signal_type"] = batch[0].get("signal_type", "")
                item["source_geo"] = batch[0].get("geo_zone", "")
                item["_extracted"] = True
                prospects.append(item)

        # Pause entre les batches
        if batch_idx < total_batches - 1:
            print(f"   ⏳ Pause {LLM_SLEEP}s (rate limit)...")
            time.sleep(LLM_SLEEP)

    return prospects
