"""Génération de messages d'approche personnalisés via Gemini (cache-aware)."""

import json
import time
from google import genai
from src.config import (
    GOOGLE_API_KEY, MODEL_MESSAGE, LLM_MAX_TOKENS, LLM_SLEEP,
    CAPVISIO_DESCRIPTION, PROMPT_MESSAGE,
)

client = genai.Client(api_key=GOOGLE_API_KEY)


def _call_llm(prompt: str, max_retries: int = 2) -> str:
    for attempt in range(max_retries + 1):
        try:
            print(f"   [MESSAGE] Appel LLM ({MODEL_MESSAGE}), tentative {attempt+1}/{max_retries+1}")
            response = client.models.generate_content(
                model=MODEL_MESSAGE,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=LLM_MAX_TOKENS,
                ),
            )
            text = response.text.strip() if response.text else ""
            print(f"   [MESSAGE] Réponse reçue ({len(text)} chars)")
            return text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                print(f"   [MESSAGE] Rate limit 429 — pause 15s (tentative {attempt+1}/{max_retries})")
                time.sleep(15)
            else:
                print(f"   [MESSAGE] Erreur LLM: {e}")
                return ""
    return ""


def _parse_message_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return None


def generate_messages(prospects: list[dict], progress_callback=None) -> list[dict]:
    """Génère les messages pour les prospects qualifiés. Skip ceux déjà traités."""
    # Filtrer : qualifiés sans message
    to_process = [
        p for p in prospects
        if p.get("qualified", False) and not p.get("_messaged")
    ]

    if not to_process:
        already = len([p for p in prospects if p.get("_messaged")])
        if already:
            print(f"   [MESSAGE] {already} prospects ont déjà des messages, skip.")
        return prospects

    print(f"   [MESSAGE] {len(to_process)} messages à générer")

    for i, prospect in enumerate(to_process):
        if progress_callback:
            progress_callback(i, len(to_process))

        prompt = PROMPT_MESSAGE.format(
            capvisio_desc=CAPVISIO_DESCRIPTION,
            company_name=prospect.get("company_name", ""),
            signal_type=prospect.get("signal_type", ""),
            project_details=prospect.get("project_details", ""),
            location=prospect.get("location", ""),
            approach_angle=prospect.get("approach_angle", ""),
            deal_estimate=prospect.get("deal_estimate", "N/A"),
        )

        try:
            print(f"   [MESSAGE] Génération {i+1}/{len(to_process)}: {prospect.get('company_name', '?')}")
            response = _call_llm(prompt)
            messages = _parse_message_json(response)
            if messages:
                prospect["messages"] = {
                    "email_subject": messages.get("email_subject", ""),
                    "email_body": messages.get("email_body", ""),
                    "whatsapp": messages.get("whatsapp_message", messages.get("whatsapp", "")),
                }
                print(f"   [MESSAGE] OK pour {prospect.get('company_name', '?')}")
            else:
                print(f"   [MESSAGE] Parsing JSON échoué pour {prospect.get('company_name', '?')}")
                prospect["messages"] = {"email_subject": "", "email_body": "", "whatsapp": ""}
        except Exception as e:
            print(f"   [MESSAGE] Erreur pour {prospect.get('company_name', '?')}: {e}")
            prospect["messages"] = {"email_subject": "", "email_body": "", "whatsapp": ""}

        prospect["_messaged"] = True

        # Pause entre les appels
        if i < len(to_process) - 1:
            print(f"   [MESSAGE] Pause {LLM_SLEEP}s (rate limit)...")
            time.sleep(LLM_SLEEP)

    print(f"   [MESSAGE] Terminé: {len(to_process)} messages générés")
    return prospects
