# ROADMAP BUILD — Agent Prospecteur CapVisio

## Contexte
**Projet** : POC Agent Prospecteur IA pour CapVisio
**Deadline** : Ce soir — démo demain pour Nicolas Bourdin (Dir Marketing CapVisio)
**Stack** : Python + Gemini API + duckduckgo-search + Streamlit
**LLM** : Gemini 2.0 Flash (essai 90 jours gratuit)
**Règle** : Chaque étape doit être TERMINÉE et TESTÉE avant de passer à la suivante.

---

## ÉTAPE 0 — INIT PROJET (10 min)

### Objectif
Créer la structure de fichiers, installer les dépendances, vérifier que tout tourne.

### Actions
- [ ] Créer le dossier `capvisio-prospect-agent/`
- [ ] Créer la structure :
```
capvisio-prospect-agent/
├── CLAUDE.md
├── .env                    # GEMINI_API_KEY=...
├── .gitignore
├── requirements.txt
├── app.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── search.py
│   ├── extract.py
│   ├── score.py
│   └── message.py
├── data/
│   ├── prospects.json      # [] vide au départ
│   └── queries.json        # Templates de requêtes
└── styles/
    └── main.css
```
- [ ] Créer `requirements.txt` :
```
streamlit>=1.30.0
google-generativeai>=0.4.0
duckduckgo-search>=4.0
python-dotenv>=1.0.0
```
- [ ] `pip install -r requirements.txt`
- [ ] Créer `.env` avec `GEMINI_API_KEY=...`
- [ ] Créer `.gitignore` (`.env`, `__pycache__/`, `data/prospects.json`, `.venv/`)
- [ ] Tester : `python -c "import google.generativeai; print('OK')"` → doit afficher OK

### Checkpoint ✅
> Structure créée, dépendances installées, import Gemini OK.

---

## ÉTAPE 1 — CONFIG (15 min)

### Objectif
Fichier de configuration centralisé. Toutes les constantes, clés API, paramètres au même endroit.

### Fichier : `src/config.py`
Doit contenir :
- Chargement `.env` (dotenv)
- `GEMINI_API_KEY` depuis l'environnement
- Nom du modèle Gemini : `gemini-2.0-flash`
- Paramètres de scoring : seuils (HOT > 70, WARM > 40, COLD < 40)
- Chemins fichiers : `DATA_DIR`, `PROSPECTS_FILE`, `QUERIES_FILE`
- Configuration Gemini : température 0 pour extraction/scoring, 0.7 pour messages

### Fichier : `data/queries.json`
Templates de requêtes de recherche par type de signal :
```json
{
  "demenagement": [
    "déménagement siège entreprise Nantes 2025 2026",
    "déménagement bureaux entreprise Rennes 2025 2026",
    "nouveau siège social entreprise Loire-Atlantique 2025 2026",
    "entreprise déménage nouveaux locaux Paris IDF 2025 2026",
    "nouveau siège entreprise Bretagne 2025 2026"
  ],
  "construction": [
    "permis construire bureaux Nantes 2025 2026",
    "construction immeuble bureaux Loire-Atlantique 2025 2026",
    "projet immobilier tertiaire Grand Ouest France 2025 2026",
    "nouveau campus entreprise Bretagne Nantes 2025 2026",
    "construction bureaux neufs IDF Paris 2025 2026"
  ],
  "levee_fonds": [
    "levée de fonds startup Nantes 2025 2026",
    "levée fonds entreprise Rennes millions 2025 2026",
    "financement série A B startup Grand Ouest France",
    "levée fonds millions startup Paris tech 2025 2026"
  ],
  "renovation": [
    "rénovation bureaux tertiaire Nantes 2025 2026",
    "travaux réaménagement siège entreprise Loire-Atlantique",
    "smart building rénovation tertiaire Grand Ouest",
    "réhabilitation immeuble bureaux Rennes Bretagne 2025 2026"
  ],
  "recrutement": [
    "entreprise recrute massivement Nantes 2025 2026",
    "plan recrutement 50 postes Rennes Nantes Bretagne",
    "forte croissance recrutement entreprise Grand Ouest 2025 2026"
  ]
}
```

### Checkpoint ✅
> `from src.config import *` fonctionne. Les queries se chargent depuis le JSON.

---

## ÉTAPE 2 — MODULE SEARCH (30 min)

### Objectif
Rechercher des signaux d'achat sur le web via `duckduckgo-search`. Retourner des résultats bruts structurés.

### Fichier : `src/search.py`

### Fonction principale
```python
def search_signals(signal_types: list[str] = None, max_results_per_query: int = 5) -> list[dict]
```

### Comportement
1. Charger les requêtes depuis `data/queries.json`
2. Si `signal_types` est None → chercher tous les types
3. Pour chaque requête : appeler `duckduckgo-search` (module `DDGS`)
4. Chaque résultat brut = `{"title": ..., "body": ..., "href": ...}`
5. Ajouter le `signal_type` et la `query` utilisée à chaque résultat
6. **sleep(1.5)** entre chaque requête (éviter rate limit DuckDuckGo)
7. Dédoublonner par URL (set de href)
8. Retourner la liste complète des résultats bruts

### Gestion d'erreurs
- Try/except sur chaque appel DDGS
- Si rate limit → sleep(5) et retry 1 fois
- Si échec → log l'erreur, continuer avec les autres requêtes
- Ne JAMAIS crash le programme entier

### Test CLI
```python
if __name__ == "__main__":
    results = search_signals(["demenagement"], max_results_per_query=3)
    for r in results:
        print(f"[{r['signal_type']}] {r['title']}")
        print(f"  URL: {r['href']}")
        print()
    print(f"Total: {len(results)} résultats")
```

### Checkpoint ✅
> `python src/search.py` retourne 10-20 résultats web réels avec titres et URLs.

---

## ÉTAPE 3 — MODULE EXTRACT (45 min)

### Objectif
Le LLM analyse chaque résultat de recherche et extrait des prospects structurés en JSON.

### Fichier : `src/extract.py`

### Fonction principale
```python
def extract_prospects(search_results: list[dict]) -> list[dict]
```

### Comportement
1. Pour chaque résultat de recherche, envoyer au LLM (Gemini) :
   - Le titre + body + URL du résultat
   - Le type de signal associé
   - Le prompt d'extraction (voir ci-dessous)
2. Parser la réponse JSON du LLM
3. Filtrer : garder seulement les résultats où `relevant == true`
4. Dédoublonner par nom d'entreprise (normalisation basique : lower + strip)
5. **Batcher les appels** : grouper 3-5 résultats dans un seul prompt pour économiser les appels API
6. sleep(1) entre chaque appel Gemini

### Prompt d'extraction
```
Tu es un analyste commercial expert spécialisé dans la détection d'opportunités B2B.
Tu travailles pour CapVisio, un intégrateur audiovisuel et smart workplace basé à Nantes.
CapVisio installe des espaces de travail connectés : salles de visioconférence, audiovisuel,
bâtiment intelligent. Clients : entreprises tertiaires (bureaux, sièges sociaux).

Analyse ces résultats de recherche web et extrais les opportunités commerciales.
Pour CHAQUE résultat qui contient un signal d'achat pertinent, retourne un objet JSON.

Signaux pertinents :
- Déménagement de siège / nouveaux bureaux
- Construction / rénovation de bâtiment tertiaire
- Levée de fonds importante (> 2M€) = croissance = nouveaux locaux probables
- Recrutement massif = besoin d'espace = besoin d'équipement

Résultats de recherche :
{search_results_batch}

Retourne UNIQUEMENT un JSON valide (pas de texte autour, pas de ```json```) :
[
  {
    "relevant": true,
    "company_name": "Nom de l'entreprise",
    "signal_type": "demenagement|construction|renovation|levee_fonds|recrutement",
    "location": "Ville, Département",
    "project_details": "Description courte du projet (2-3 phrases max)",
    "estimated_date": "YYYY-MM ou inconnu",
    "source_url": "URL de la source",
    "source_title": "Titre de l'article/source",
    "confidence": 0.0-1.0
  }
]

Si un résultat n'est pas pertinent, ne l'inclus pas dans la liste.
Si aucun résultat n'est pertinent, retourne [].
```

### Parsing JSON robuste
```python
def parse_llm_json(text: str) -> list | dict:
    """Parse le JSON du LLM avec fallback regex si le LLM envoie du texte autour."""
    # 1. Essayer json.loads() direct
    # 2. Si échec : chercher le premier [ ... ] ou { ... } avec regex
    # 3. Si échec : retourner []
```

### Gestion d'erreurs
- Si Gemini timeout → retry 1 fois après 3 secondes
- Si JSON invalide → log + skip ce batch
- Si rate limit Gemini → sleep(10) et retry

### Test CLI
```python
if __name__ == "__main__":
    from src.search import search_signals
    raw = search_signals(["demenagement"], max_results_per_query=3)
    prospects = extract_prospects(raw)
    for p in prospects:
        print(f"[{p['signal_type']}] {p['company_name']} — {p['location']}")
        print(f"  {p['project_details']}")
        print()
    print(f"Total: {len(prospects)} prospects extraits")
```

### Checkpoint ✅
> `python src/extract.py` retourne 3-10 prospects structurés avec nom, signal, localisation.

---

## ÉTAPE 4 — MODULE SCORE (30 min)

### Objectif
Le LLM évalue chaque prospect sur sa pertinence pour CapVisio. Score 0-100 + priorité.

### Fichier : `src/score.py`

### Fonction principale
```python
def score_prospects(prospects: list[dict]) -> list[dict]
```

### Comportement
1. Batcher les prospects par groupes de 3 max dans un seul appel LLM
2. Le LLM attribue un score et une priorité à chaque prospect
3. Ajouter les champs de scoring à chaque prospect
4. Trier par score décroissant
5. Retourner la liste enrichie

### Prompt scoring
```
Tu es un directeur commercial chez CapVisio, intégrateur audiovisuel et smart workplace.

Contexte CapVisio :
- Métier : conception et installation d'espaces de travail connectés (visioconférence, AV, bâtiment intelligent)
- CA : 22,3 M€, 70 collaborateurs, siège Nantes + IDF + Bretagne
- Clients : entreprises tertiaires (bureaux, sièges sociaux), 900+ clients actifs
- Couverture nationale via GIE AUVNI (réseau de 8 intégrateurs AV)
- Projets typiques : 50K-500K€ (salles de réunion, auditoriums, espaces collaboratifs)
- Partenaires tech : Cisco, Microsoft, Barco, Q-SYS, Samsung

Évalue ces prospects :
{prospects_batch}

Pour CHAQUE prospect, retourne UNIQUEMENT un JSON valide :
[
  {
    "company_name": "reprendre le nom exact",
    "score": <int 0-100>,
    "score_breakdown": {
      "pertinence_metier": <0-30>,
      "taille_deal": <0-20>,
      "urgence_timing": <0-25>,
      "proximite_geo": <0-15>,
      "qualite_signal": <0-10>
    },
    "deal_estimate_keur": "<estimation chiffrée ex: 50-150>",
    "approach_angle": "<angle commercial recommandé en 2 phrases>",
    "priority": "hot|warm|cold"
  }
]

Critères de scoring :
- pertinence_metier (/30) : est-ce que l'entreprise aura besoin de salles équipées, visio, AV, smart workplace ?
- taille_deal (/20) : quel volume potentiel ? (une ETI qui déménage son siège = gros deal, une PME de 20 personnes = petit)
- urgence_timing (/25) : le projet est-il imminent (< 6 mois) ou lointain (> 18 mois) ?
- proximite_geo (/15) : Nantes/Rennes/Bretagne/IDF = 15, couverture AUVNI = 10, hors zone = 5
- qualite_signal (/10) : la source est-elle fiable ? L'info est-elle récente ?

Seuils : hot > 70, warm 40-70, cold < 40
```

### Merge avec les prospects
Après le scoring, fusionner les données de scoring dans chaque prospect :
```python
prospect["score"] = scored["score"]
prospect["score_breakdown"] = scored["score_breakdown"]
prospect["deal_estimate"] = scored["deal_estimate_keur"]
prospect["approach_angle"] = scored["approach_angle"]
prospect["priority"] = scored["priority"]
```

### Checkpoint ✅
> Pipeline search → extract → score fonctionne. Chaque prospect a un score, une priorité, un breakdown.

---

## ÉTAPE 5 — MODULE MESSAGE (30 min)

### Objectif
Générer un message d'approche personnalisé pour chaque prospect qualifié (hot ou warm).

### Fichier : `src/message.py`

### Fonction principale
```python
def generate_messages(prospects: list[dict]) -> list[dict]
```

### Comportement
1. Filtrer : ne générer des messages que pour les prospects hot et warm (score >= 40)
2. Pour chaque prospect qualifié, appeler le LLM avec température 0.7
3. Générer DEUX versions : email + WhatsApp
4. Ajouter les messages au prospect

### Prompt message
```
Tu es un commercial senior chez CapVisio, expert en approche B2B.
CapVisio conçoit et installe des espaces de travail connectés (visioconférence, AV, smart building).

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
{
  "email": {
    "subject": "Objet de l'email (court, accrocheur)",
    "body": "Corps de l'email (max 150 mots, avec signature 'Prénom Nom — CapVisio')"
  },
  "whatsapp": "Message WhatsApp court et direct (max 80 mots, tutoiement évité)"
}

IMPORTANT : Le message doit sembler écrit par un humain, pas par une IA.
Le commercial ne dit JAMAIS qu'il a "vu un article" ou "détecté un signal".
Il dit plutôt "j'ai appris que", "félicitations pour", "je vois que vous êtes en pleine croissance".
```

### Merge
```python
prospect["email_subject"] = message["email"]["subject"]
prospect["email_body"] = message["email"]["body"]
prospect["whatsapp_message"] = message["whatsapp"]
```

### Checkpoint ✅
> Pipeline complet search → extract → score → message. Les prospects hot/warm ont des messages prêts à copier-coller.

---

## ÉTAPE 6 — SAUVEGARDE & CACHE (15 min)

### Objectif
Sauvegarder les résultats en JSON local pour ne pas tout relancer à chaque refresh Streamlit.

### Ajouter dans `src/config.py` ou créer `src/storage.py`

### Fonctions
```python
def save_prospects(prospects: list[dict]) -> None:
    """Sauvegarde les prospects dans data/prospects.json"""

def load_prospects() -> list[dict]:
    """Charge les prospects depuis data/prospects.json. Retourne [] si vide."""

def clear_prospects() -> None:
    """Vide le cache de prospects."""
```

### Comportement
- `save_prospects` écrit le JSON avec `indent=2` et `ensure_ascii=False` (accents français)
- `load_prospects` retourne une liste vide si le fichier n'existe pas ou est vide
- Le timestamp de la dernière recherche est sauvé avec les données

### Format data/prospects.json
```json
{
  "last_search": "2026-03-04T22:15:00",
  "search_params": {"signal_types": ["demenagement", "construction"], "max_results": 5},
  "prospects": [
    {
      "company_name": "...",
      "signal_type": "...",
      "location": "...",
      "project_details": "...",
      "source_url": "...",
      "score": 78,
      "priority": "hot",
      "email_subject": "...",
      "email_body": "...",
      "whatsapp_message": "..."
    }
  ]
}
```

### Checkpoint ✅
> Après une recherche, les résultats sont sauvés. Au relancement, les données sont là sans re-rechercher.

---

## ÉTAPE 7 — PIPELINE COMPLET CLI (15 min)

### Objectif
Un script qui enchaîne tout le pipeline de bout en bout et affiche les résultats en console.

### Créer `run_pipeline.py` à la racine

### Comportement
```python
"""
Pipeline complet : search → extract → score → message → save
Usage : python run_pipeline.py [--signals demenagement,construction] [--max 5]
"""
```

1. Parser les arguments (argparse basique)
2. Appeler `search_signals()`
3. Afficher : "X résultats bruts trouvés"
4. Appeler `extract_prospects()`
5. Afficher : "X prospects identifiés"
6. Appeler `score_prospects()`
7. Afficher : "X hot, X warm, X cold"
8. Appeler `generate_messages()`
9. Sauvegarder avec `save_prospects()`
10. Afficher un résumé tableau en console

### Checkpoint ✅
> `python run_pipeline.py` tourne de A à Z, affiche des prospects scorés avec messages, et sauve en JSON.
> C'EST LE TEST CRITIQUE. Si ça marche ici, le reste c'est de l'interface.

---

## ÉTAPE 8 — INTERFACE STREAMLIT (1h)

### Objectif
Dashboard visuel propre pour la démo Nicolas. C'est ici que le POC devient IMPRESSIONNANT.

### Fichier : `app.py`

### Layout global
```
┌─────────────────────────────────────────────────────┐
│ SIDEBAR                        │  MAIN CONTENT      │
│                                │                     │
│ Logo CapVisio (texte)          │  Header + stats     │
│ ─────────────────              │  ─────────────────  │
│ Filtres :                      │                     │
│  □ Déménagement                │  Tableau prospects  │
│  □ Construction                │  (triable, cliquable│
│  □ Levée de fonds              │                     │
│  □ Rénovation                  │  ─────────────────  │
│  □ Recrutement                 │                     │
│                                │  Fiche détaillée    │
│ Score minimum : [slider]       │  (expander)         │
│                                │  - Infos entreprise │
│ Géo : [multiselect]           │  - Score + jauge    │
│                                │  - Message email    │
│ [🔍 Lancer la recherche]      │  - Message WhatsApp │
│ [📂 Charger le cache]         │  - Bouton copier    │
│                                │                     │
│ ─────────────────              │  ─────────────────  │
│ Stats :                        │                     │
│  X prospects trouvés           │  Export CSV         │
│  X hot / X warm / X cold       │                     │
└─────────────────────────────────────────────────────┘
```

### Composants clés

**Header** :
- Titre : "Agent Prospecteur CapVisio"
- Sous-titre : "Détection automatique d'opportunités commerciales"
- Métriques en colonnes : Total prospects | Hot | Warm | Cold

**Tableau de prospects** :
- Colonnes : Priorité (badge coloré) | Entreprise | Signal | Localisation | Score | Deal estimé
- Trié par score décroissant par défaut
- Chaque ligne cliquable via `st.expander`

**Fiche prospect (dans l'expander)** :
- 2 colonnes : infos à gauche, score à droite
- Jauge de score (st.progress_bar ou barre CSS custom)
- Breakdown du score en sous-barres
- Source URL cliquable
- Onglets : Email | WhatsApp
- Bouton "Copier" pour chaque message (st.code avec copy button)

**Bouton recherche** :
- Lance le pipeline complet avec spinner
- Messages de progression : "Recherche en cours... X signaux détectés... Analyse... Scoring..."
- Sauvegarde automatique après

### Fichier : `styles/main.css`
- Dark theme : `#0F1117` fond principal, `#1A1B2E` fond cards, `#00D4AA` accent vert
- Texte blanc `#FFFFFF`, texte secondaire `#8B8FA3`
- Badges : Hot = `#FF4B4B`, Warm = `#FFA500`, Cold = `#6B7280`
- Police : Source Sans 3 (import Google Fonts via CSS)
- Border-radius : 8px sur les cards
- Hover subtle sur les éléments cliquables
- Messages WhatsApp : fond `#075E54` (vert WhatsApp), bulle avec border-radius 12px

### Checkpoint ✅
> `streamlit run app.py` affiche le dashboard. Le bouton "Lancer la recherche" fonctionne.
> Les prospects s'affichent avec scores, badges, messages. L'interface est propre et impressionnante.

---

## ÉTAPE 9 — POLISH & DONNÉES RÉELLES (30 min)

### Objectif
S'assurer que le POC contient de vraies données convaincantes pour la démo.

### Actions
- [ ] Lancer une recherche complète (tous les types de signaux)
- [ ] Vérifier que 5-10 prospects réels apparaissent
- [ ] Vérifier la qualité des messages générés (sont-ils crédibles ? envoyables ?)
- [ ] Si les résultats duckduckgo sont pauvres : ajouter manuellement 2-3 prospects réels dans `data/prospects.json` (chercher sur Google des vrais déménagements/constructions récents)
- [ ] Tester l'export CSV
- [ ] Vérifier le responsive (pas critique mais pas cassé)
- [ ] Prendre 2-3 screenshots pour backup si la démo live plante

### Prospects à pre-seeder si besoin (chercher les vrais)
Chercher manuellement sur Google :
- "déménagement siège Nantes 2025 2026"
- "nouveau campus entreprise Loire-Atlantique"
- "levée de fonds startup Nantes"
Et injecter les vrais résultats dans le JSON si le scraping automatique ne les trouve pas.

### Checkpoint ✅
> Dashboard avec 5-10 vrais prospects, messages réalistes, interface fluide. PRÊT POUR LA DÉMO.

---

## ÉTAPE 10 — PRÉPARATION DÉMO (15 min)

### Objectif
Préparer le scénario de démo pour Nicolas demain.

### Script de démo (3-5 minutes)

**Intro (30s)** :
"Nicolas, je te montre un prototype d'agent de prospection automatisé, pensé pour CapVisio. L'idée : au lieu que tes commerciaux passent des heures à chercher des opportunités, l'outil le fait automatiquement."

**Démo live (2-3 min)** :
1. Montrer le dashboard avec les résultats déjà chargés
2. Cliquer sur un prospect "Hot" → montrer la fiche détaillée
3. Montrer le score et le breakdown ("Voilà pourquoi on le considère prioritaire")
4. Montrer le message WhatsApp généré → "Ton commercial copie ça et l'envoie en 10 secondes"
5. Montrer le message email → "Ou en version email plus formelle"
6. Lancer une nouvelle recherche en live (si le temps le permet)
7. Montrer l'export CSV → "Et tout est exportable pour le CRM"

**Conclusion (30s)** :
"C'est un prototype. L'étape suivante : on le connecte à vos vraies sources de données, on automatise les alertes quotidiennes, et on intègre ça dans votre workflow commercial."

### Questions anticipées de Nicolas
- "C'est quoi les sources de données ?" → Sources publiques : presse éco, annonces légales, data.gouv. En V2 on peut ajouter LinkedIn Sales Navigator, Pappers premium, etc.
- "C'est fiable ?" → C'est de l'IA, il y a un score de confiance. Le commercial valide avant d'envoyer. L'outil détecte, l'humain décide.
- "Combien ça coûte à maintenir ?" → Actuellement gratuit (API Gemini trial). En production : ~50-100€/mois max pour les API.
- "On peut l'intégrer au CRM ?" → Oui, en V2. Export CSV dès maintenant, connexion Sage CRM ou HubSpot en phase suivante.

### Checkpoint ✅
> Script de démo prêt. Tu sais exactement quoi montrer et dans quel ordre.

---

## RÉSUMÉ TIMELINE

| Étape | Durée | Livrable |
|-------|-------|----------|
| 0. Init | 10 min | Structure + dépendances |
| 1. Config | 15 min | config.py + queries.json |
| 2. Search | 30 min | Résultats web bruts |
| 3. Extract | 45 min | Prospects structurés JSON |
| 4. Score | 30 min | Prospects scorés + priorité |
| 5. Message | 30 min | Messages email + WhatsApp |
| 6. Storage | 15 min | Cache JSON local |
| 7. Pipeline CLI | 15 min | Test end-to-end en console |
| 8. Interface | 60 min | Dashboard Streamlit |
| 9. Polish | 30 min | Données réelles + screenshots |
| 10. Démo | 15 min | Script + préparation |
| **TOTAL** | **~4h30** | **POC fonctionnel + démo prête** |

---

## RÈGLES POUR CLAUDE CODE

1. **Séquentiel strict** : Termine une étape avant de passer à la suivante. Pas de parallélisme.
2. **Test après chaque module** : Le test CLI doit passer AVANT de continuer.
3. **Si blocage > 15 min sur un module** : Simplifier. Hardcoder des valeurs si nécessaire.
4. **Pas d'over-engineering** : Pas de classes abstraites, pas de design patterns, pas de types complexes. Des fonctions simples qui prennent des dicts et retournent des dicts.
5. **Gemini API** : google-generativeai, modèle gemini-2.0-flash, pas d'autre provider.
6. **Commit à chaque checkpoint** : `git add -A && git commit -m "étape X terminée"`
7. **Le pipeline CLI (étape 7) est le gate critique** : Si le pipeline tourne en console, tout le reste c'est du Streamlit qu'on connaît déjà.

---

*Roadmap validée — prête pour exécution Claude Code*
*Deadline : ce soir*
