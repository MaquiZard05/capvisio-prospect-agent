import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
PAPPERS_API_KEY = os.getenv("PAPPERS_API_KEY", "")

# --- LLM Multi-modèle ---
MODEL_EXTRACT = "gemini-2.5-flash"          # Le plus puissant pour l'extraction
MODEL_EXTRACT_FALLBACK = "gemini-2.5-flash-lite"  # Fallback si quota flash épuisé
MODEL_SCORE = "gemini-2.5-flash-lite"       # Rapide et économique pour le scoring
MODEL_MESSAGE = "gemini-2.5-flash-lite"     # Idem pour les messages

LLM_MAX_TOKENS = 2000
LLM_SLEEP = 13  # Pause entre appels (free tier = 5 req/min par modèle)

# --- Recherche ---
DEFAULT_GEO_ZONES = ["Nantes", "Rennes", "Bretagne", "Paris", "Île-de-France"]
DEFAULT_SIGNAL_TYPES = ["demenagement", "construction", "levee_fonds", "recrutement", "renovation"]
SEARCH_MAX_RESULTS = 8
CURRENT_YEAR = "2026"

# --- Scoring ---
SCORE_THRESHOLD = 60

# --- Chemins fichiers ---
DATA_DIR = Path(__file__).parent.parent / "data"
PROSPECTS_FILE = DATA_DIR / "prospects.json"
QUERIES_FILE = DATA_DIR / "search_queries.json"

# --- CapVisio ---
CAPVISIO_DESCRIPTION = (
    "CapVisio est un intégrateur audiovisuel et smart workplace basé à Nantes. "
    "CapVisio conçoit et installe des espaces de travail connectés : visioconférence, "
    "audiovisuel, affichage dynamique, bâtiment intelligent. "
    "Clients : entreprises tertiaires (bureaux, sièges sociaux). "
    "Couverture : Grand Ouest (Nantes, Rennes, Bretagne) + IDF + réseau GIE AUVNI national."
)

# --- Prompts LLM ---
PROMPT_EXTRACT_BATCH = """Tu es un analyste commercial expert spécialisé dans la détection d'opportunités B2B.
Tu travailles pour CapVisio, un intégrateur audiovisuel et smart workplace basé à Nantes.
{capvisio_desc}

Analyse ces résultats de recherche web et extrais les opportunités commerciales.
Pour CHAQUE résultat qui contient un signal d'achat pertinent, retourne un objet JSON.

Signaux pertinents :
- Déménagement de siège / nouveaux bureaux → besoin d'équiper les salles
- Construction / rénovation de bâtiment tertiaire → besoin d'intégration AV
- Levée de fonds importante (> 2M€) → croissance = nouveaux locaux probables
- Recrutement massif → besoin d'espace = besoin d'équipement

Résultats de recherche :
{search_results_batch}

Retourne UNIQUEMENT un JSON valide (pas de texte autour, pas de ```json```) :
[
  {{
    "relevant": true,
    "company_name": "Nom de l'entreprise",
    "signal_type": "demenagement|construction|renovation|levee_fonds|recrutement",
    "location": "Ville, Département",
    "project_details": "Description courte du projet (2-3 phrases max)",
    "estimated_date": "YYYY-MM ou inconnu",
    "source_url": "URL de la source",
    "source_title": "Titre de l'article",
    "confidence": 0.0-1.0
  }}
]

Si aucun résultat n'est pertinent, retourne : []
"""

PROMPT_SCORE_BATCH = """Tu es un directeur commercial chez CapVisio, intégrateur audiovisuel et smart workplace.

Contexte CapVisio :
{capvisio_desc}
- Projets typiques : 50K-500K€ (salles de réunion, auditoriums, espaces collaboratifs)
- Partenaires tech : Cisco, Microsoft, Barco, Q-SYS, Samsung

Évalue ces prospects :
{prospects_batch}

Pour CHAQUE prospect, retourne UNIQUEMENT un JSON valide :
[
  {{
    "company_name": "reprendre le nom exact",
    "score": <int 0-100>,
    "score_breakdown": {{
      "pertinence_metier": <0-30>,
      "taille_deal": <0-20>,
      "urgence_timing": <0-25>,
      "proximite_geo": <0-15>,
      "qualite_signal": <0-10>
    }},
    "deal_estimate_keur": "<estimation ex: 50-150>",
    "approach_angle": "<angle commercial recommandé en 2 phrases>",
    "priority": "hot|warm|cold"
  }}
]

Seuils : hot > 70, warm 40-70, cold < 40
"""

PROMPT_MESSAGE = """Tu es un commercial senior chez CapVisio, expert en approche B2B.
{capvisio_desc}

Rédige un message d'approche pour ce prospect. Tu dois :
1. Mentionner naturellement le signal détecté (SANS dire que tu utilises un outil de veille)
2. Positionner CapVisio comme expert en espaces de travail connectés
3. Proposer un audit gratuit des espaces ou un échange rapide de 15 min
4. Ton : professionnel, direct, humain. Pas corporate ni froid.

Prospect :
- Entreprise : {company_name}
- Signal : {signal_type} — {project_details}
- Localisation : {location}
- Angle recommandé : {approach_angle}
- Deal estimé : {deal_estimate}

Retourne UNIQUEMENT un JSON valide :
{{
  "email_subject": "Objet de l'email (court, accrocheur)",
  "email_body": "Corps de l'email (max 150 mots, avec signature 'Prénom Nom — CapVisio')",
  "whatsapp_message": "Message WhatsApp court et direct (max 80 mots)"
}}

IMPORTANT : Le message doit sembler écrit par un humain, pas par une IA.
Le commercial ne dit JAMAIS qu'il a "vu un article" ou "détecté un signal".
Il dit plutôt "j'ai appris que", "félicitations pour", "je vois que vous êtes en pleine croissance".
"""

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
