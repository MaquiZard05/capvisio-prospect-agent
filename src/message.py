"""Génération de messages d'approche personnalisés."""

import json
from groq import Groq
from src.config import (
    GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    PROMPT_MESSAGE, CAPVISIO_DESCRIPTION,
)

client = Groq(api_key=GROQ_API_KEY)


def generate_message(prospect: dict) -> dict:
    """Génère les messages d'approche email + WhatsApp pour un prospect."""
    prospect_text = json.dumps(prospect, ensure_ascii=False, indent=2)
    prompt = PROMPT_MESSAGE.format(
        prospect_data=prospect_text,
        capvisio_desc=CAPVISIO_DESCRIPTION,
    )

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=LLM_MAX_TOKENS,
        )
        text = response.choices[0].message.content.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            messages = json.loads(text[start:end])
            prospect["messages"] = {
                "email_subject": messages.get("email_subject", ""),
                "email_body": messages.get("email_body", ""),
                "whatsapp": messages.get("whatsapp_message", ""),
            }
            return prospect
    except Exception:
        pass

    prospect["messages"] = {
        "email_subject": "",
        "email_body": "",
        "whatsapp": "",
    }
    return prospect


def generate_messages(prospects: list[dict], progress_callback=None) -> list[dict]:
    """Génère les messages pour les prospects qualifiés uniquement."""
    for i, prospect in enumerate(prospects):
        if not prospect.get("qualified", False):
            continue
        if progress_callback:
            progress_callback(i, len(prospects))
        generate_message(prospect)
    return prospects
