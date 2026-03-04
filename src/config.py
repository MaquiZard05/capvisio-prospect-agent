import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PAPPERS_API_KEY = os.getenv("PAPPERS_API_KEY", "")

# --- LLM ---
LLM_MODEL = "llama-3.1-70b-versatile"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 2000

# --- Recherche ---
DEFAULT_GEO_ZONES = ["Nantes", "Rennes", "Bretagne", "Paris", "Île-de-France"]
DEFAULT_SIGNAL_TYPES = ["demenagement", "construction", "levee_fonds", "recrutement", "renovation"]
SEARCH_MAX_RESULTS = 8
CURRENT_YEAR = "2026"

# --- Scoring ---
SCORE_THRESHOLD = 60

# --- CapVisio ---
CAPVISIO_DESCRIPTION = (
    "CapVisio est un intégrateur audiovisuel et smart workplace basé à Nantes. "
    "CapVisio conçoit et installe des espaces de travail connectés : visioconférence, "
    "audiovisuel, affichage dynamique, bâtiment intelligent. "
    "Clients : entreprises tertiaires (bureaux, sièges sociaux). "
    "Couverture : Grand Ouest (Nantes, Rennes, Bretagne) + IDF + réseau GIE AUVNI national."
)

# --- Prompts LLM ---
PROMPT_EXTRACT = """Tu es un analyste commercial expert. À partir de ce résultat de recherche web,
extrais les informations suivantes au format JSON strict (pas de texte autour, uniquement le JSON) :

{{
  "relevant": true,
  "company_name": "nom de l'entreprise",
  "signal_type": "demenagement" | "construction" | "renovation" | "levee_fonds" | "recrutement",
  "location": "ville/département",
  "project_details": "description courte du projet (1-2 phrases)",
  "estimated_date": "YYYY-MM ou inconnu",
  "source_url": "URL de la source",
  "confidence": 0.0-1.0
}}

Si le résultat ne contient pas de signal d'achat pertinent pour un intégrateur
audiovisuel/smart building, retourne uniquement : {{"relevant": false}}

Résultat de recherche :
{search_result}"""

PROMPT_SCORE = """Tu es un commercial expert chez CapVisio, intégrateur audiovisuel et smart workplace.
{capvisio_desc}

Évalue ce prospect pour CapVisio :
{prospect_data}

Score sur 100 selon :
- Pertinence métier CapVisio (besoin de salles de réunion, visio, AV ?) : /30
- Taille du deal potentiel : /20
- Urgence/timing : /25
- Accessibilité géographique (CapVisio = Nantes, IDF, Bretagne + réseau AUVNI national) : /15
- Qualité du signal (source fiable, info récente) : /10

Retourne UNIQUEMENT un JSON strict :
{{
  "score": <int 0-100>,
  "score_breakdown": {{"pertinence": 0, "deal_size": 0, "urgence": 0, "geo": 0, "signal_quality": 0}},
  "deal_estimate": "<estimation en K€>",
  "approach_angle": "<angle commercial recommandé en 2 phrases>",
  "priority": "hot" | "warm" | "cold"
}}"""

PROMPT_MESSAGE = """Tu es un commercial CapVisio. Rédige un message d'approche court et percutant
pour ce prospect. Le message doit :
- Mentionner le signal détecté (sans dire qu'on l'a trouvé via un outil automatisé)
- Positionner CapVisio comme expert en espaces de travail connectés
- Proposer un audit gratuit / échange rapide
- Ton : professionnel mais pas corporate, direct
- Max 150 mots par version

Contexte prospect :
{prospect_data}

{capvisio_desc}

Retourne UNIQUEMENT un JSON strict :
{{
  "email_subject": "objet de l'email",
  "email_body": "corps de l'email",
  "whatsapp_message": "message WhatsApp court"
}}"""

# --- UI ---
THEME = {
    "bg_color": "#0F1117",
    "accent_color": "#00D4AA",
    "text_color": "#FFFFFF",
    "card_bg": "#1A1D27",
    "card_border": "#2D3140",
}

SIGNAL_LABELS = {
    "demenagement": {"label": "Déménagement", "color": "#FF6B6B", "emoji": "🏢"},
    "construction": {"label": "Construction", "color": "#4ECDC4", "emoji": "🏗️"},
    "renovation": {"label": "Rénovation", "color": "#FFE66D", "emoji": "🔧"},
    "levee_fonds": {"label": "Levée de fonds", "color": "#A8E6CF", "emoji": "💰"},
    "recrutement": {"label": "Recrutement", "color": "#DDA0DD", "emoji": "👥"},
}

PRIORITY_LABELS = {
    "hot": {"label": "🔴 Hot", "color": "#FF4444"},
    "warm": {"label": "🟠 Warm", "color": "#FFA500"},
    "cold": {"label": "🔵 Cold", "color": "#4488FF"},
}
