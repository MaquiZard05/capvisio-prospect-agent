# Agent Prospecteur CapVisio

Agent IA de détection automatique de signaux d'achat pour CapVisio (intégrateur audiovisuel & smart workplace).

## Fonctionnalités

- Détection de signaux d'achat (permis de construire, déménagements, levées de fonds, recrutements)
- Extraction structurée via LLM (Groq / Llama 3.1 70B)
- Enrichissement données entreprise (Pappers API)
- Scoring et qualification automatique des prospects
- Génération de messages d'approche personnalisés
- Dashboard Streamlit interactif avec export CSV

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copier `.env` et renseigner les clés API :
```
GROQ_API_KEY=your_groq_api_key
PAPPERS_API_KEY=your_pappers_api_key  # optionnel
```

## Lancement

```bash
streamlit run app.py
```

## Stack

- Python 3.11+
- Streamlit (interface)
- Groq API / Llama 3.1 70B (LLM)
- DuckDuckGo Search (recherche web)
- Pappers API (enrichissement entreprise)
