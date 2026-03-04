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
            response = client.models.generate_content(
                model=MODEL_MESSAGE,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=LLM_MAX_TOKENS,
                ),
            )
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                print(f"   ⏳ Rate limit — pause 15s (tentative {attempt+1}/{max_retries})")
                time.sleep(15)
            else:
                raise
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
            print(f"   {already} prospects ont déjà des messages, skip.")
        return prospects

    print(f"   {len(to_process)} messages à générer")

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
            response = _call_llm(prompt)
            messages = _parse_message_json(response)
            if messages:
                prospect["messages"] = {
                    "email_subject": messages.get("email_subject", ""),
                    "email_body": messages.get("email_body", ""),
                    "whatsapp": messages.get("whatsapp_message", messages.get("whatsapp", "")),
                }
            else:
                prospect["messages"] = {"email_subject": "", "email_body": "", "whatsapp": ""}
        except Exception:
            prospect["messages"] = {"email_subject": "", "email_body": "", "whatsapp": ""}

        prospect["_messaged"] = True

        # Pause entre les appels
        if i < len(to_process) - 1:
            print(f"   ⏳ Pause {LLM_SLEEP}s (rate limit)...")
            time.sleep(LLM_SLEEP)

    return prospects
