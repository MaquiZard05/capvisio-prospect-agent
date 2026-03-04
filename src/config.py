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

LLM_MAX_TOKENS = 4000
LLM_SLEEP = 15  # Pause entre appels (free tier = 5 req/min par modèle)
BATCH_SIZE_EXTRACT = 10  # Résultats par batch d'extraction (réduit le nb d'appels API)
BATCH_SIZE_SCORE = 10  # Prospects par batch de scoring

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
    "CapVisio est le 3ème intégrateur visioconférence en France, spécialisé smart workplace. "
    "Chiffres clés : 22,3 M€ de CA, 70 collaborateurs, 900+ clients actifs, 7 000+ espaces installés. "
    "Expertises : visioconférence (Cisco, Microsoft Teams Rooms, Zoom Rooms), audiovisuel professionnel "
    "(Barco, Q-SYS, Samsung), affichage dynamique, bâtiment intelligent (GTC/GTB). "
    "Partenaires technologiques : Cisco, Microsoft, Barco, Q-SYS, Samsung, Crestron, Poly. "
    "Clients : entreprises tertiaires, collectivités, enseignement supérieur (bureaux, sièges sociaux, auditoriums). "
    "Siège à Nantes, couverture nationale via le réseau GIE AUVNI (20+ intégrateurs partenaires)."
)

# --- Prompts LLM ---
PROMPT_EXTRACT_BATCH = """Tu es un analyste commercial expert spécialisé dans la détection d'opportunités B2B.
Tu travailles pour CapVisio, un intégrateur audiovisuel et smart workplace.
{capvisio_desc}

MISSION : Analyse les résultats de recherche ci-dessous et extrais UNIQUEMENT les opportunités commerciales réelles et exploitables.

RÈGLES STRICTES DE FILTRAGE :
1. CHAQUE opportunité DOIT avoir un NOM D'ENTREPRISE PRÉCIS et IDENTIFIABLE (raison sociale réelle).
   → REJETER : "une entreprise nantaise", "une startup", "un promoteur", "entreprise inconnue", noms génériques.
2. CHAQUE opportunité DOIT contenir un SIGNAL D'ACHAT CONCRET avec des détails vérifiables (adresse, montant, date, nombre de postes...).
   → REJETER : articles d'opinion, tendances générales, études de marché, listes sans projet précis.
3. Le signal doit concerner une entreprise qui POURRAIT AVOIR BESOIN d'équipements audiovisuels ou smart workplace.
   → REJETER : commerce de détail, restaurants, logements résidentiels, agriculture.

SIGNAUX PERTINENTS (par ordre de priorité) :
- DÉMÉNAGEMENT : entreprise qui déménage son siège ou ouvre de nouveaux bureaux → doit équiper les salles de réunion
- CONSTRUCTION : nouveau bâtiment tertiaire, campus, immeuble de bureaux → intégration AV dès la conception
- RÉNOVATION : réaménagement de bureaux existants, passage en flex office → modernisation des équipements
- LEVÉE DE FONDS : levée > 2M€ avec plan de croissance → nouveaux locaux probables sous 6-18 mois
- RECRUTEMENT : plan de recrutement > 20 postes → besoin d'espace supplémentaire = besoin d'équipement

EXEMPLES DE CE QUI EST PERTINENT :
✅ "Sodexo déménage son siège social à Nanterre dans un immeuble de 15 000 m²" → signal clair, entreprise nommée
✅ "Doctolib lève 500M€ et prévoit 1 000 recrutements" → croissance = nouveaux bureaux
✅ "Bouygues Immobilier lance la construction d'un campus tertiaire de 30 000 m² à Rennes" → projet concret

EXEMPLES DE CE QUI N'EST PAS PERTINENT :
❌ "Le marché de l'immobilier de bureau progresse en 2026" → pas d'entreprise précise
❌ "Une startup nantaise lève des fonds" → nom d'entreprise manquant
❌ "Inauguration d'un centre commercial à Nantes" → commerce de détail, pas de besoin AV

Résultats de recherche :
{search_results_batch}

Retourne UNIQUEMENT un JSON valide (pas de texte autour, pas de ```json```, pas de commentaires) :
[
  {{
    "relevant": true,
    "company_name": "Nom exact de l'entreprise (raison sociale)",
    "signal_type": "demenagement|construction|renovation|levee_fonds|recrutement",
    "location": "Ville, Département",
    "project_details": "Description factuelle du projet en 2-3 phrases avec chiffres si disponibles",
    "estimated_date": "YYYY-MM ou inconnu",
    "source_url": "URL de la source",
    "source_title": "Titre de l'article",
    "confidence": 0.0-1.0
  }}
]

RAPPEL : Ne retourne QUE des entreprises avec un nom précis et un signal concret. En cas de doute, NE PAS inclure. Si aucun résultat n'est pertinent, retourne : []
"""

PROMPT_SCORE_BATCH = """Tu es un directeur commercial chez CapVisio, intégrateur audiovisuel et smart workplace.

Contexte CapVisio :
{capvisio_desc}

Offre et projets typiques :
- Salle de réunion équipée (visio + écran + son) : 15K-50K€
- Salle de direction / boardroom : 50K-150K€
- Auditorium / amphithéâtre : 100K-500K€
- Équipement complet d'un étage (5-10 salles) : 100K-300K€
- Smart building (GTC, affichage dynamique, sonorisation) : 200K-1M€

Partenaires technologiques (bonus si le prospect utilise déjà ces marques) :
- Visioconférence : Cisco Webex, Microsoft Teams Rooms, Zoom Rooms, Poly
- Affichage : Samsung, Barco ClickShare, LG
- Audio/pilotage : Q-SYS, Crestron, Shure, Biamp
- Collaboration : Microsoft 365, Google Workspace

GRILLE DE SCORING (total sur 100) :

1. PERTINENCE MÉTIER (0-30 pts) :
   - 25-30 : Besoin AV explicite (salle de réunion, visioconférence, auditorium, smart building)
   - 15-24 : Besoin AV probable (nouveaux bureaux tertiaires, siège social, campus)
   - 5-14 : Besoin AV possible (croissance, levée de fonds sans mention de locaux)
   - 0-4 : Peu de lien avec l'AV (retail, logistique pure, industrie lourde)

2. TAILLE DU DEAL (0-20 pts) :
   - 15-20 : Projet > 200K€ potentiel (campus, siège social, bâtiment neuf entier)
   - 8-14 : Projet 50K-200K€ (quelques salles, un étage, rénovation partielle)
   - 0-7 : Projet < 50K€ (1-2 salles, petit bureau)

3. URGENCE / TIMING (0-25 pts) :
   - 20-25 : Projet en cours ou livraison < 6 mois, décision imminente
   - 10-19 : Projet annoncé, livraison 6-18 mois
   - 0-9 : Projet lointain (> 18 mois) ou date inconnue

4. PROXIMITÉ GÉOGRAPHIQUE (0-15 pts) :
   - 12-15 : Grand Ouest (Nantes, Rennes, Angers, Brest) = zone directe CapVisio
   - 7-11 : Île-de-France ou grandes métropoles couvertes via GIE AUVNI
   - 0-6 : Autres régions (couverture possible via AUVNI mais moins directe)

5. QUALITÉ DU SIGNAL (0-10 pts) :
   - 8-10 : Source fiable (presse éco, communiqué officiel), détails concrets
   - 4-7 : Source correcte mais peu de détails
   - 0-3 : Source faible ou information vague

Évalue ces prospects :
{prospects_batch}

Pour CHAQUE prospect, retourne UNIQUEMENT un JSON valide (pas de texte autour, pas de ```json```) :
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

Seuils STRICTS : hot > 70, warm 40-70, cold < 40. Sois exigeant : un prospect "hot" doit vraiment représenter une opportunité imminente et qualifiée.
"""

PROMPT_MESSAGE = """Tu es un commercial senior chez CapVisio, expert en approche B2B personnalisée.
{capvisio_desc}

MISSION : Rédige un message d'approche CRÉDIBLE et ENVOYABLE pour ce prospect.

RÈGLES ABSOLUES — Le commercial :
- Dit : "j'ai appris que", "félicitations pour", "je vois que", "en échangeant avec des acteurs de votre secteur"
- Ne dit JAMAIS : "j'ai vu un article", "notre outil de veille", "selon nos informations", "nous avons détecté", "d'après notre analyse"
- Vouvoie toujours dans l'email
- Ne tutoie PAS dans le WhatsApp non plus (vouvoiement partout)
- Ne commence JAMAIS un email par "Cher" ou "Chère" → utiliser "Bonjour," tout court
- Ne termine JAMAIS par "Cordialement" → utiliser "À très vite," ou "Belle journée,"

STRUCTURE EMAIL (max 150 mots) :
1. Accroche : mentionner le signal de façon naturelle (1 phrase)
2. Valeur : positionner CapVisio comme partenaire pertinent pour ce projet précis (2-3 phrases)
3. Call-to-action : proposer un audit gratuit des futurs espaces OU un échange de 15 min
4. Signature : "Prénom Nom — CapVisio, Intégrateur Smart Workplace"

STRUCTURE WHATSAPP (max 80 mots) :
1. Accroche directe liée au signal (1 phrase)
2. Proposition de valeur courte (1 phrase)
3. Call-to-action simple : "Un café pour en discuter ?" ou "15 min pour vous montrer ce qu'on fait ?"

Prospect :
- Entreprise : {company_name}
- Signal : {signal_type} — {project_details}
- Localisation : {location}
- Angle recommandé : {approach_angle}
- Deal estimé : {deal_estimate}

Retourne UNIQUEMENT un JSON valide (pas de texte autour, pas de ```json```) :
{{
  "email_subject": "Objet de l'email (court, accrocheur, max 8 mots, sans point final)",
  "email_body": "Corps de l'email (max 150 mots, signature 'Prénom Nom — CapVisio, Intégrateur Smart Workplace')",
  "whatsapp_message": "Message WhatsApp (max 80 mots, direct, vouvoiement)"
}}

IMPORTANT : Chaque message doit être suffisamment personnalisé pour que le destinataire sente qu'on s'intéresse VRAIMENT à son projet. Pas de template générique.
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
