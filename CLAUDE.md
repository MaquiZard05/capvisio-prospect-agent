# CLAUDE.md — Agent Prospecteur CapVisio (POC)

## Identité
Tu travailles avec Marin sur un POC d'agent prospecteur IA pour CapVisio.
Marin est un non-développeur qui apprend par la pratique (vibe coding). Il a de l'expérience avec Python/Streamlit via son projet RAG (Assistant conformité chantier BTP). C'est son premier projet d'agent IA.

## Objectif du POC
Construire un **Agent Prospecteur** qui détecte automatiquement des opportunités commerciales pour CapVisio en scannant des sources web publiques.
Démo prévue demain pour **Nicolas Bourdin** (Directeur Marketing & Communication, CapVisio).
Le POC doit être FONCTIONNEL et IMPRESSIONNANT visuellement. Pas parfait — démontrable.

## Contexte CapVisio (à connaître pour les prompts)
- **Métier** : Intégrateur audiovisuel & smart workplace (visioconférence, AV, bâtiment intelligent)
- **CA** : 22,3 M€, ~70 collaborateurs, siège Nantes + IDF + Bretagne
- **Clients** : Entreprises tertiaires (bureaux, sièges sociaux), 900+ clients actifs, 7000+ espaces installés
- **Partenaires tech** : Cisco, Microsoft, Barco, Q-SYS, Samsung, Promethean, Extron, Pexip
- **GIE AUVNI** : Réseau de 8 intégrateurs AV = couverture nationale
- **Positionnement** : 3ème intégrateur visio France, indépendant multi-constructeurs
- **Services** : Audit → Conception → Intégration → Installation → Maintenance → Support 24/7
- **Prix typiques** : Projets 50K-500K€ (équipement salles de réunion, auditoriums, espaces collaboratifs)

## Prospects cibles CapVisio
**Qui** : ETI et grandes entreprises tertiaires (bureaux), CA > 5M€, effectif > 50
**Où** : Grand Ouest (Nantes, Rennes, Bretagne) + IDF + national via AUVNI
**Quand** : Projet immobilier en cours ou prévu 6-18 mois
**Signaux d'achat** :
1. Permis de construire bureaux/tertiaire
2. Déménagement de siège
3. Levée de fonds > 5M€
4. Recrutement massif (> 20 postes)
5. Rénovation tertiaire
6. Obligation décret tertiaire / BACS

## Stack Technique (NE PAS CHANGER SANS DEMANDER)
- **Langage** : Python 3.11+
- **LLM** : Google Gemini 2.5 Flash (gemini-2.5-flash) via google-genai SDK
- **Recherche web** : `duckduckgo-search` (Python, gratuit, sans clé API)
- **Interface** : Streamlit
- **Stockage** : JSON local (data/prospects.json)
- **Enrichissement** : Optionnel — Pappers API free tier si le temps le permet

> ⚠️ Ne propose JAMAIS de changer de lib ou d'outil sans que Marin le demande. Pas de LangGraph, pas de LangChain, pas de CrewAI. Python natif + Gemini + Streamlit.

## Structure du Projet
```
capvisio-prospect-agent/
├── CLAUDE.md                  # Ce fichier
├── README.md                  # Doc rapide
├── requirements.txt           # Dépendances Python
├── .env                       # GOOGLE_API_KEY=AIza...
├── .gitignore
├── app.py                     # Point d'entrée Streamlit (dashboard)
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration centralisée
│   ├── search.py              # Recherche web (duckduckgo-search)
│   ├── extract.py             # Extraction structurée via LLM
│   ├── score.py               # Scoring & qualification via LLM
│   └── message.py             # Génération messages d'approche
├── data/
│   ├── prospects.json         # Prospects trouvés (cache)
│   └── queries.json           # Templates de requêtes de recherche
└── styles/
    └── main.css               # Dark theme CapVisio
```

## Conventions de Code

### Langue
- **Variables, fonctions** : anglais
- **Commentaires** : français
- **Messages Streamlit (UI)** : français
- **Prompts LLM** : français (on cherche des entreprises françaises)

### Style
- Code SIMPLE et LISIBLE
- Une fonction = une responsabilité
- Pas de classes si une fonction suffit
- Pas d'abstraction inutile (pas de factory, pas de base classes)
- Try/except autour des appels API Gemini et des recherches web
- Messages d'erreur français dans l'UI
- print() pour le debug

## Pipeline de l'Agent
```
1. SEARCH  → duckduckgo-search sur N requêtes prédéfinies par type de signal
2. EXTRACT → LLM parse chaque résultat → JSON structuré (entreprise, signal, lieu, date)
3. SCORE   → LLM évalue pertinence CapVisio → score 0-100 + priority hot/warm/cold
4. MESSAGE → LLM génère message d'approche personnalisé (email + WhatsApp)
5. DISPLAY → Streamlit dashboard avec tableau, fiches, messages copiables
```

Chaque étape est un module Python séparé dans src/. Le flux est linéaire (pas de graph).

## Prompts LLM — Principes
- Toujours donner le contexte CapVisio dans le system prompt
- Toujours demander du JSON en sortie (avec instruction "retourne UNIQUEMENT du JSON valide")
- Parser le JSON avec json.loads() + fallback regex si le LLM envoie du texte autour
- Température 0 pour extraction et scoring, 0.7 pour messages d'approche

## Interface Streamlit

### Design
- Dark theme : fond #0F1117, accent vert tech #00D4AA, texte blanc
- Police lisible, cards avec bordure subtile
- Badges colorés : 🔴 Hot (rouge/orange), 🟡 Warm (jaune), ⚪ Cold (gris)
- Jauge visuelle pour le score (st.progress ou barre custom)
- Format WhatsApp-like pour les messages (bulle de message, fond légèrement différent)

### Layout
- **Sidebar** : filtres (géo, type de signal, score minimum) + bouton "Lancer la recherche"
- **Main** : tableau de prospects triable → clic/expander → fiche détaillée + message d'approche
- **Fiche prospect** : nom, CA, effectifs, signal, source URL, score, breakdown, message généré
- **Actions** : copier message, exporter CSV

## Variables d'Environnement (.env)
```
GOOGLE_API_KEY=AIza...
```

## Commandes
```bash
# Activer l'environnement
python -m venv venv && source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

## Dépendances (requirements.txt)
```
streamlit>=1.30.0
google-genai>=1.0.0
duckduckgo-search>=4.0
python-dotenv>=1.0.0
```

## Comportement Attendu de Claude Code

### Par défaut
- **Code directement**, sans longues explications
- Teste mentalement avant de proposer (imports, variables, types)
- Propose des checkpoints ("ça marche, on peut tester")
- Après chaque bloc significatif : commit + push

### Anti-patterns (NE PAS FAIRE)
- ❌ Ne pas ajouter LangGraph, LangChain, CrewAI ou tout framework agent
- ❌ Ne pas sur-ingénierer (pas de Docker, pas de CI/CD, pas de tests unitaires)
- ❌ Ne pas proposer d'alternatives de stack
- ❌ Ne pas refactorer du code qui fonctionne
- ❌ Ne pas créer de fichiers inutiles
- ❌ Ne pas utiliser d'API payante sans demander (Serper, SerpAPI, etc.)

### Priorité absolue
Le POC doit tourner ce soir. Si un module prend trop de temps, simplifier :
- Enrichissement Pappers → skip, on utilise ce que le LLM extrait du web
- Scoring complexe → scoring simple par le LLM en un seul appel
- Multiple pages Streamlit → une seule page avec expanders

## Contexte Business
- **Budget : 0€.** Tout doit être gratuit.
- C'est un POC pour montrer la valeur d'un agent prospecteur à Nicolas Bourdin (Dir Marketing CapVisio)
- Si Nicolas valide, ça ouvre la porte à une mission payante (agent B2B intégré aux workflows CapVisio)
- Ce POC est aussi le premier livrable du Projet 2 (Agentique B2B) de la roadmap freelance de Marin
- L'outil ne sera PAS déployé ce soir — démo en local sur l'écran de Marin

## Requêtes de Recherche Prédéfinies
Le fichier data/queries.json contient les templates. Exemples :
```json
{
  "demenagement": [
    "déménagement siège entreprise Nantes 2026",
    "déménagement bureaux entreprise Rennes 2026",
    "nouveau siège social entreprise Loire-Atlantique",
    "entreprise déménage nouveaux locaux IDF 2026"
  ],
  "construction": [
    "permis construire bureaux Nantes 2025 2026",
    "construction immeuble bureaux Loire-Atlantique",
    "projet immobilier tertiaire Grand Ouest France",
    "nouveau campus entreprise Bretagne"
  ],
  "levee_fonds": [
    "levée de fonds startup Nantes 2026",
    "levée fonds entreprise Rennes millions 2026",
    "financement série A B startup Grand Ouest"
  ],
  "renovation": [
    "rénovation bureaux tertiaire Nantes",
    "travaux réaménagement siège entreprise Loire-Atlantique",
    "smart building rénovation tertiaire Grand Ouest"
  ],
  "recrutement": [
    "entreprise recrute massivement Nantes 2026",
    "plan recrutement 50 postes Rennes Nantes Bretagne"
  ]
}
```

## Notes
- Le dédoublonnage des prospects se fait sur le nom d'entreprise (fuzzy matching basique)
- Les résultats sont cachés dans data/prospects.json pour ne pas relancer les recherches à chaque refresh
- Le rate limit Gemini (free tier) impose de batcher les appels avec des pauses
- Si duckduckgo-search rate-limit, ajouter un sleep(2) entre les requêtes