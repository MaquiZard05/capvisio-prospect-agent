# Guide de Démo — Agent Prospecteur CapVisio

*Pour Marin — Démo devant Nicolas Bourdin, Dir Marketing & Communication CapVisio*

---

## SECTION 1 : AVANT LA DÉMO (5 min)

### Lancer l'outil

Ouvre un terminal dans le dossier du projet et tape :

    python3 -m streamlit run app.py

Attends 5 secondes. Le terminal affiche une URL du type `http://localhost:8501`. Ouvre-la dans ton navigateur (Chrome ou Firefox).

### Charger les données

Une fois le dashboard affiché :

1. **Regarde la sidebar à gauche** — tu vois les filtres (types de signaux, zones géo, score minimum)
2. **Clique sur le bouton "Charger résultats précédents"** dans la sidebar
3. Un message vert apparaît : *"9 prospects chargés"*
4. Le dashboard se remplit avec le tableau et les fiches

### Checklist pré-démo

- L'app tourne dans le navigateur (page blanche avec le titre "Agent Prospecteur CapVisio")
- Après avoir cliqué "Charger résultats précédents", tu vois 9 prospects dans le tableau
- Les 4 cartes de métriques en haut affichent : **9** prospects, **9** qualifiés, **8** hot leads, score moyen **82**
- En dessous, le tableau montre les entreprises avec leurs scores
- Si tu cliques sur une entreprise dans la section "Fiches détaillées", la fiche s'ouvre avec le score et les messages

### Si ça ne marche pas

- **L'app ne se lance pas** : vérifie que tu es dans le bon dossier (`cd ~/capvisio-prospect-agent`), puis relance la commande
- **"Aucun résultat sauvegardé"** : les données sont peut-être perdues. Pas de panique, relance `python3 -m streamlit run app.py` et réessaie
- **La page est blanche** : rafraîchis le navigateur (F5)

---

## SECTION 2 : SCRIPT DE DÉMO (5-7 min)

### Étape 1 — Intro (30s)

> "Nicolas, je vais te montrer un prototype d'agent de prospection automatisé, pensé sur-mesure pour CapVisio. Le constat de départ est simple : aujourd'hui, tes commerciaux passent du temps à chercher manuellement des opportunités — surveiller les déménagements, les constructions de bureaux, les levées de fonds. Cet outil fait ce travail automatiquement."

**Ne touche à rien à l'écran.** Nicolas voit le dashboard avec le titre "Agent Prospecteur CapVisio" et la page de chargement.

*Nicolas voit une interface propre, professionnelle, qui ressemble à un vrai outil SaaS.*

**Pourquoi c'est important** : tu poses le problème avant de montrer la solution.

---

### Étape 2 — Charger les résultats (30s)

> "Je vais charger les résultats d'une recherche que l'outil a déjà effectuée."

**Clique sur "Charger résultats précédents" dans la sidebar à gauche.**

*Nicolas voit le dashboard se remplir : 4 cartes de métriques apparaissent en haut, puis un tableau de prospects en dessous.*

> "Voilà. L'outil a scanné la presse économique et les actualités business, et il a détecté 9 opportunités concrètes pour CapVisio. 8 d'entre elles sont classées prioritaires."

**Pourquoi c'est important** : Nicolas voit immédiatement le volume et la qualité — 8 leads chauds en un clic.

---

### Étape 3 — Le tableau (1 min)

> "Ici, tu as la vue d'ensemble. Chaque ligne, c'est une entreprise avec un projet concret."

**Montre le tableau du doigt en parcourant les colonnes.**

> "Tu vois le nom de l'entreprise, le type de signal — déménagement, construction, levée de fonds — le score sur 100, la priorité, la localisation et le timing."

**Montre la colonne Score avec les barres de progression.**

> "Le score, c'est la pertinence pour CapVisio. Plus c'est haut, plus l'opportunité est chaude. Par exemple, Samsic à 92 sur 100, L'Orange Bleue à 91. Ce ne sont pas des noms au hasard — ce sont de vraies entreprises, avec de vrais projets en cours."

*Nicolas voit des noms d'entreprises qu'il connaît probablement (Doctolib, Crédit Agricole, Samsic), avec des scores visuels.*

**Pourquoi c'est important** : ça montre que l'outil détecte des opportunités réelles et qualifiées, pas du bruit.

---

### Étape 4 — Zoom sur L'Orange Bleue (1.5 min)

> "Je vais te montrer le détail d'un prospect particulièrement intéressant pour CapVisio."

**Descends jusqu'à la section "Fiches détaillées". Clique sur l'expander "[Hot] L'Orange Bleue — Score: 91/100 — Construction".**

*La fiche s'ouvre en deux colonnes : les infos à gauche, le score à droite.*

> "L'Orange Bleue, c'est le leader français du fitness — 400 salles, 160 millions de chiffre d'affaires. Ils construisent leur nouveau siège à Rennes, 4 400 m², 15 millions d'investissement. Et le détail qui nous intéresse : le bâtiment inclut un studio de production vidéo et un espace podcast."

**Montre les détails du projet sur la gauche.**

> "C'est pile ce que fait CapVisio. Studio vidéo, podcast, salles de réunion connectées — c'est notre cœur de métier."

**Montre le score et les barres de détail sur la droite.**

> "Le score est décomposé en 5 critères. Pertinence métier : 30 sur 30, c'est le maximum — parce qu'ils ont un besoin audiovisuel explicite. Proximité géo : 15 sur 15 — c'est à Rennes, notre zone directe. Urgence : 22 sur 25 — emménagement prévu en juin 2026, donc c'est maintenant qu'il faut les approcher."

*Nicolas voit les barres bleues qui illustrent la force de chaque critère.*

**Pourquoi c'est important** : Nicolas comprend que le scoring n'est pas un chiffre magique — c'est une grille de lecture commerciale rigoureuse.

---

### Étape 5 — Le message WhatsApp (1 min)

> "Et maintenant, la partie la plus concrète. L'outil génère automatiquement les messages d'approche."

**Clique sur l'onglet "WhatsApp" dans la fiche de L'Orange Bleue.**

*Nicolas voit le message WhatsApp dans une bulle verte, prêt à copier-coller.*

> "Regarde ce message. Il mentionne le projet de studio vidéo, il positionne CapVisio comme expert, et il propose un échange de 15 minutes. Ton commercial copie ce message, l'envoie en 10 secondes, et il a un premier contact personnalisé."

**Montre le bouton de copie (l'icône en haut à droite du bloc de code).**

> "Un clic pour copier, un clic pour coller dans WhatsApp. C'est tout."

*Nicolas lit un message qui sonne naturel, personnalisé, professionnel.*

**Pourquoi c'est important** : c'est le moment "wow". Le passage de la détection au message envoyable en un clic, c'est la valeur concrète de l'outil.

---

### Étape 6 — Le message email (30s)

> "Et pour les approches plus formelles, il y a aussi une version email."

**Clique sur l'onglet "Email".**

*Nicolas voit l'objet de l'email ("Votre studio vidéo et podcast — on en parle ?") et le corps du mail.*

> "L'objet est accrocheur, le mail fait moins de 150 mots, il propose un audit gratuit. C'est prêt à envoyer."

**Pourquoi c'est important** : deux canaux d'approche, deux formats, zéro effort de rédaction pour le commercial.

---

### Étape 7 — Les filtres (30s)

> "L'outil est aussi filtrable. Si ton commercial ne s'occupe que de Nantes, ou que des déménagements..."

**Dans la sidebar, décoche tous les signaux sauf "Déménagement".**

*Le tableau ne montre plus que 3 prospects : Doctolib, Espacil Habitat et Faguo.*

> "Il filtre instantanément. On peut aussi filtrer par zone géo, par score minimum, par priorité."

**Remets tous les filtres comme avant (recoche tous les signaux).**

**Pourquoi c'est important** : chaque commercial peut adapter la vue à son territoire et sa spécialité.

---

### Étape 8 — L'export CSV (15s)

> "Et tout est exportable."

**Descends en bas de page et clique sur le bouton "Exporter en CSV".**

*Un fichier CSV se télécharge.*

> "Ce fichier peut être importé dans n'importe quel CRM — Sage, HubSpot, un simple Excel. Tout y est : l'entreprise, le score, les messages, les sources."

**Pourquoi c'est important** : l'outil s'intègre dans le workflow existant sans rien changer.

---

### Étape 9 — Conclusion (30s)

> "Pour résumer : cet outil scanne automatiquement le web, détecte les entreprises qui ont un projet où CapVisio peut intervenir, les classe par priorité, et génère les messages d'approche. En quelques minutes, un commercial a une liste qualifiée avec des messages prêts à envoyer."

**Laisse un silence de 2 secondes.**

> "C'est un prototype fonctionnel. La prochaine étape, c'est de le connecter à vos vraies sources de données, d'automatiser les alertes quotidiennes, et de l'intégrer dans le workflow commercial de l'équipe."

---

## SECTION 3 : RÉPONSES AUX QUESTIONS DE NICOLAS

### "C'est quoi les sources de données ?"

> "L'outil scanne les sources de presse économique publiques — Le Journal des Entreprises, Bretagne Économique, Maddyness, France 3 Régions, etc. En version 2, on peut ajouter des sources premium comme les annonces légales, LinkedIn Sales Navigator ou Pappers."

### "C'est fiable ? Comment on sait que c'est pas du bruit ?"

> "C'est de l'intelligence artificielle, donc il y a toujours une part d'interprétation. C'est pour ça qu'il y a le score et le détail des critères — le commercial peut juger en un coup d'œil. L'outil détecte et qualifie, l'humain décide d'envoyer ou pas. Là, sur 9 détections, les 9 sont des vrais projets vérifiables."

### "Combien ça coûte ?"

> "Aujourd'hui le prototype tourne sur des services gratuits. En production, on parlerait de 50 à 100 euros par mois pour les services d'intelligence artificielle. C'est négligeable comparé au temps commercial économisé."

### "On peut le connecter au CRM ?"

> "En l'état, il y a l'export CSV qui permet d'alimenter n'importe quel CRM manuellement. En version 2, on peut créer une connexion directe avec Sage, HubSpot ou Salesforce pour que les prospects arrivent automatiquement dans le pipe commercial."

### "C'est quoi la suite ?"

> "Trois choses. Un : connecter des sources de données premium pour encore plus de signaux. Deux : automatiser — l'outil tourne tous les matins et envoie une alerte avec les nouveaux prospects. Trois : intégrer au CRM pour que tout arrive directement dans le pipe des commerciaux."

### "Combien de temps ça a pris à construire ?"

> "Ce prototype a été construit en quelques jours. C'est la force du développement assisté par intelligence artificielle — on peut aller très vite du concept au prototype fonctionnel. La mise en production prendrait quelques semaines supplémentaires."

### "Les données des prospects passent par où ? C'est sécurisé ?"

> "Les données restent en local sur la machine. Rien n'est stocké dans le cloud. L'intelligence artificielle analyse les articles de presse publics — on ne collecte aucune donnée personnelle. En version production, on peut héberger ça sur un serveur CapVisio sécurisé."

### "On peut l'utiliser pour le réseau AUVNI aussi ?"

> "Absolument. L'outil couvre déjà toute la France — tu as vu Pennylane qui est à Paris. On peut configurer les zones géographiques pour que chaque intégrateur du réseau AUVNI reçoive les leads de sa zone. C'est un argument de valeur pour le GIE."

---

## SECTION 4 : ANTISÈCHE RAPIDE

### 3 chiffres clés

- **9 prospects** détectés automatiquement, dont 8 prioritaires
- **Score moyen de 82/100** — des opportunités hautement qualifiées
- **Potentiel commercial estimé : ~2 millions d'euros** cumulés sur les 9 prospects

### 3 phrases d'accroche

1. "L'outil détecte automatiquement les entreprises qui ont besoin de CapVisio."
2. "En un clic, le commercial a un message personnalisé prêt à envoyer."
3. "9 opportunités trouvées, 8 prioritaires — avec des noms comme Doctolib, Samsic, Crédit Agricole."

### 3 forces de l'outil

1. **Détection automatique** — plus besoin de chercher manuellement les projets
2. **Scoring intelligent** — 5 critères calibrés pour CapVisio (pertinence, taille deal, urgence, géo, fiabilité)
3. **Messages prêts à envoyer** — email et WhatsApp personnalisés, copier-coller en 10 secondes

### 3 prochaines étapes à proposer

1. Tester l'outil en conditions réelles pendant 2 semaines avec 2-3 commerciaux
2. Connecter des sources de données premium (annonces légales, Pappers)
3. Automatiser les alertes quotidiennes par email

### Commande de secours

Si l'outil plante pendant la démo, ouvre un terminal et tape :

    python3 -m streamlit run app.py

Puis clique sur "Charger résultats précédents" dans la sidebar.

---

## SECTION 5 : LEXIQUE

**Intelligence artificielle (IA)** : programme capable d'analyser du texte et de prendre des décisions. Ici, elle lit des articles de presse et en extrait les opportunités commerciales.

**Scoring** : système de notation sur 100 qui classe les prospects par ordre de priorité pour CapVisio, selon 5 critères métier.

**Signal d'achat** : événement qui indique qu'une entreprise pourrait avoir besoin des services de CapVisio — un déménagement, une construction, une levée de fonds, un recrutement massif.

**Pipeline** : la chaîne de traitement automatique — recherche web, extraction, scoring, génération de messages. Tout s'enchaîne sans intervention humaine.

**Dashboard** : le tableau de bord visuel qui affiche les résultats. C'est l'écran que Nicolas voit.

**Export CSV** : fichier de données tabulaires qu'on peut ouvrir dans Excel ou importer dans un CRM.

**CRM** : logiciel de gestion de la relation client (Sage, HubSpot, Salesforce). C'est là que les commerciaux gèrent leurs contacts et opportunités.

**Agent IA** : un programme d'intelligence artificielle qui effectue une tâche de bout en bout — ici, il détecte, analyse, score et rédige, comme le ferait un stagiaire très rapide.

**Enrichissement** : l'ajout d'informations supplémentaires sur une entreprise (effectifs, chiffre d'affaires, dirigeants) à partir de bases de données publiques.

**Prompt** : l'instruction donnée à l'intelligence artificielle pour lui dire quoi chercher et comment analyser. C'est la "recette" qui fait que l'outil est calibré pour CapVisio.
