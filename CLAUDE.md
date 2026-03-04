# Agent Prospecteur CapVisio

## Projet
POC d'agent IA de prospection commerciale pour CapVisio (intégrateur audiovisuel/smart building).

## Stack
- Python 3.11+, Streamlit, Groq API (Llama 3.1 70B), duckduckgo-search, BeautifulSoup
- Stockage JSON local (pas de DB)
- Dark theme : fond #0F1117, accent #00D4AA, texte #FFFFFF

## Structure
- `app.py` : point d'entrée Streamlit
- `src/config.py` : configuration centralisée
- `src/search.py` : recherche web de signaux
- `src/extract.py` : extraction structurée LLM
- `src/enrich.py` : enrichissement données entreprise
- `src/score.py` : scoring et qualification
- `src/message.py` : génération messages d'approche

## Conventions
- Tous les appels LLM passent par Groq avec le modèle défini dans config.py
- Les résultats sont des dicts/listes Python, sérialisés en JSON
- Le scoring est sur 100, seuil d'alerte > 60
