# Agent Prospecteur CapVisio

Agent IA de détection automatique d'opportunités commerciales pour CapVisio — intégrateur audiovisuel & smart workplace.

## Ce que fait l'outil

1. **Détecte** des signaux d'achat sur le web (déménagements, constructions, levées de fonds, rénovations, recrutements)
2. **Extrait** les prospects via IA (nom, localisation, détails du projet, timeline)
3. **Score** chaque prospect sur 100 selon sa pertinence pour CapVisio
4. **Génère** des messages d'approche personnalisés (email + WhatsApp)
5. **Affiche** tout dans un dashboard interactif avec filtres et export CSV

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Créer un fichier `.env` à la racine :

```
GOOGLE_API_KEY=votre_clé_gemini
PAPPERS_API_KEY=votre_clé_pappers  # optionnel
```

Obtenir une clé Gemini gratuite sur [ai.google.dev](https://ai.google.dev/).

## Lancement

```bash
# Dashboard interactif
streamlit run app.py

# Pipeline CLI (sans interface)
python3 run_pipeline.py --signals demenagement,construction --geo Nantes,Paris
```

## Stack technique

| Composant | Outil |
|-----------|-------|
| Langage | Python 3.11+ |
| LLM | Google Gemini 2.5 Flash / Flash-Lite |
| Recherche web | Google News RSS + DuckDuckGo News (fallback) |
| Enrichissement | Pappers API (optionnel) |
| Interface | Streamlit |
| Stockage | JSON local |

## Structure

```
├── app.py                 # Dashboard Streamlit
├── run_pipeline.py        # Pipeline CLI
├── src/
│   ├── config.py          # Configuration + prompts LLM
│   ├── search.py          # Recherche web (Google News RSS)
│   ├── extract.py         # Extraction structurée (Gemini)
│   ├── enrich.py          # Enrichissement entreprise (Pappers)
│   ├── score.py           # Scoring & qualification
│   └── message.py         # Génération messages d'approche
├── data/
│   ├── prospects.json     # Cache des résultats
│   └── search_queries.json # Templates de requêtes
└── styles/
    └── main.css           # Thème UI
```

## Licence

Projet privé — tous droits réservés.
