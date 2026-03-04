"""Enrichissement des données entreprise via Pappers API ou fallback LLM Gemini."""

import json
import time
import requests
from google import genai
from src.config import GOOGLE_API_KEY, PAPPERS_API_KEY, MODEL_SCORE, LLM_MAX_TOKENS, LLM_SLEEP

client = genai.Client(api_key=GOOGLE_API_KEY)

PAPPERS_SEARCH_URL = "https://api.pappers.fr/v2/recherche"
PAPPERS_COMPANY_URL = "https://api.pappers.fr/v2/entreprise"


def enrich_via_pappers(company_name: str) -> dict | None:
    """Enrichit via l'API Pappers (données SIREN, CA, effectifs, dirigeants)."""
    if not PAPPERS_API_KEY:
        print(f"   [ENRICH] Pappers: pas de clé API, skip pour '{company_name}'")
        return None

    try:
        resp = requests.get(
            PAPPERS_SEARCH_URL,
            params={"api_token": PAPPERS_API_KEY, "q": company_name, "par_page": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("resultats", [])
        if not results:
            print(f"   [ENRICH] Pappers: aucun résultat pour '{company_name}'")
            return None

        company = results[0]
        print(f"   [ENRICH] Pappers: trouvé '{company.get('nom_entreprise', company_name)}'")
        return {
            "siren": company.get("siren", ""),
            "nom_complet": company.get("nom_entreprise", company_name),
            "siege": company.get("siege", {}).get("ville", ""),
            "code_naf": company.get("code_naf", ""),
            "libelle_naf": company.get("libelle_code_naf", ""),
            "effectifs": company.get("effectif", "Non disponible"),
            "chiffre_affaires": company.get("chiffre_affaires", "Non disponible"),
            "dirigeants": [
                f"{d.get('prenom', '')} {d.get('nom', '')} ({d.get('qualite', '')})"
                for d in company.get("dirigeants", [])[:3]
            ],
            "date_creation": company.get("date_creation", ""),
            "forme_juridique": company.get("forme_juridique", ""),
            "source": "pappers",
        }
    except Exception as e:
        print(f"   [ENRICH] Pappers erreur pour '{company_name}': {e}")
        return None


def enrich_via_llm(company_name: str, context: str = "") -> dict:
    """Fallback : enrichissement via LLM à partir du contexte disponible."""
    prompt = f"""À partir du nom d'entreprise et du contexte ci-dessous, donne les informations
que tu connais au format JSON strict. Si tu ne sais pas, mets "Non disponible".

Entreprise : {company_name}
Contexte : {context}

Retourne UNIQUEMENT un JSON :
{{
  "siren": "...",
  "nom_complet": "...",
  "siege": "ville",
  "secteur": "...",
  "effectifs": "...",
  "chiffre_affaires": "...",
  "dirigeants": ["..."],
  "source": "llm_estimation"
}}"""

    try:
        print(f"   [ENRICH] LLM fallback pour '{company_name}'")
        response = client.models.generate_content(
            model=MODEL_SCORE,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=LLM_MAX_TOKENS,
            ),
        )
        text = response.text.strip() if response.text else ""
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(text[start:end])
            print(f"   [ENRICH] LLM: enrichissement OK pour '{company_name}'")
            return result
    except Exception as e:
        print(f"   [ENRICH] LLM erreur pour '{company_name}': {e}")

    return {
        "nom_complet": company_name,
        "source": "non_enrichi",
    }


def enrich_prospect(prospect: dict) -> dict:
    """Enrichit un prospect avec des données entreprise."""
    company_name = prospect.get("company_name", "")
    if not company_name:
        return prospect

    # Skip si déjà enrichi
    if prospect.get("_enriched"):
        return prospect

    enrichment = enrich_via_pappers(company_name)
    if enrichment is None:
        context = f"{prospect.get('project_details', '')} - {prospect.get('location', '')}"
        enrichment = enrich_via_llm(company_name, context)

    prospect["company_data"] = enrichment
    prospect["_enriched"] = True
    return prospect


def enrich_prospects(prospects: list[dict], progress_callback=None) -> list[dict]:
    """Enrichit une liste de prospects."""
    to_enrich = [p for p in prospects if not p.get("_enriched")]
    already = len(prospects) - len(to_enrich)

    if not to_enrich:
        print(f"   [ENRICH] Tous les prospects sont déjà enrichis, skip.")
        return prospects

    print(f"   [ENRICH] {len(to_enrich)} à enrichir, {already} déjà traités")

    for i, prospect in enumerate(prospects):
        if prospect.get("_enriched"):
            continue
        if progress_callback:
            progress_callback(i, len(prospects))
        try:
            enrich_prospect(prospect)
        except Exception as e:
            print(f"   [ENRICH] Erreur pour '{prospect.get('company_name', '?')}': {e}")
            prospect["_enriched"] = True
            prospect["company_data"] = {"nom_complet": prospect.get("company_name", ""), "source": "erreur"}

        # Pause entre appels LLM si on utilise le fallback LLM
        if i < len(prospects) - 1 and not PAPPERS_API_KEY:
            time.sleep(LLM_SLEEP)

    print(f"   [ENRICH] Terminé: {len(prospects)} prospects")
    return prospects
