"""Agent Prospecteur CapVisio — Dashboard Streamlit."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import (
    DEFAULT_GEO_ZONES,
    DEFAULT_SIGNAL_TYPES,
    SCORE_THRESHOLD,
    SIGNAL_LABELS,
    PRIORITY_LABELS,
    THEME,
)
from src.search import search_signals
from src.extract import extract_prospects
from src.score import score_prospects
from src.message import generate_messages

# --- Page config ---
st.set_page_config(
    page_title="Agent Prospecteur CapVisio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load CSS ---
css_path = Path(__file__).parent / "styles" / "main.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --- Session state ---
if "prospects" not in st.session_state:
    st.session_state.prospects = []
if "search_done" not in st.session_state:
    st.session_state.search_done = False

DATA_PATH = Path(__file__).parent / "data" / "prospects.json"


def save_prospects(prospects: list[dict]):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(prospects, f, ensure_ascii=False, indent=2)


def load_prospects() -> list[dict]:
    """Charge les prospects depuis le cache JSON."""
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Supporte les deux formats : liste directe ou dict avec clé "prospects"
    if isinstance(data, dict) and "prospects" in data:
        return data["prospects"]
    if isinstance(data, list):
        return data
    return []


# --- Header ---
st.markdown(
    """
    <div class="main-header">
        <h1>🎯 Agent Prospecteur CapVisio</h1>
        <p>Détection automatique de signaux d'achat — Audiovisuel & Smart Workplace</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ⚙️ Paramètres de recherche")

    selected_signals = st.multiselect(
        "Types de signaux",
        options=DEFAULT_SIGNAL_TYPES,
        default=DEFAULT_SIGNAL_TYPES,
        format_func=lambda x: f"{SIGNAL_LABELS.get(x, {}).get('emoji', '')} {SIGNAL_LABELS.get(x, {}).get('label', x)}",
    )

    selected_geo = st.multiselect(
        "Zones géographiques",
        options=DEFAULT_GEO_ZONES,
        default=DEFAULT_GEO_ZONES,
    )

    score_min = st.slider("Score minimum", 0, 100, 0, step=5)

    st.markdown("---")
    st.markdown("### 📊 Filtres d'affichage")
    show_all = st.checkbox("Afficher tous les prospects", value=True)
    priority_filter = st.multiselect(
        "Priorité",
        options=["hot", "warm", "cold"],
        default=["hot", "warm", "cold"],
        format_func=lambda x: PRIORITY_LABELS.get(x, {}).get("label", x),
    )

    st.markdown("---")

    # Charger les résultats précédents
    if st.button("📂 Charger résultats précédents", use_container_width=True):
        loaded = load_prospects()
        if loaded:
            st.session_state.prospects = loaded
            st.session_state.search_done = True
            st.success(f"{len(loaded)} prospects chargés")
        else:
            st.warning("Aucun résultat sauvegardé")

    # Sidebar stats (after data is loaded)
    if st.session_state.search_done and st.session_state.prospects:
        _all = st.session_state.prospects
        _hot = len([p for p in _all if p.get("priority") == "hot"])
        _warm = len([p for p in _all if p.get("priority") == "warm"])
        _cold = len([p for p in _all if p.get("priority") == "cold"])
        st.markdown("---")
        st.markdown("### 📈 Statistiques")
        st.markdown(
            f"""<div class="sidebar-stats">
                <div class="stat-row">
                    <span class="stat-label">Total prospects</span>
                    <span class="stat-value" style="color:#00D4AA;">{len(_all)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Hot</span>
                    <span class="stat-value hot">{_hot}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Warm</span>
                    <span class="stat-value warm">{_warm}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Cold</span>
                    <span class="stat-value cold">{_cold}</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

# --- Bouton recherche ---
col_search, col_status = st.columns([1, 2])

with col_search:
    launch_search = st.button("🚀 Lancer une recherche", type="primary", use_container_width=True)

if launch_search:
    if not selected_signals or not selected_geo:
        st.error("Sélectionnez au moins un signal et une zone géographique.")
    else:
        progress_container = st.container()

        with progress_container:
            # Étape 1 : Recherche web
            st.markdown("### 🔍 Étape 1/4 — Recherche de signaux (Google News)")
            progress_bar = st.progress(0)
            status_text = st.empty()

            def search_progress(i, total, query):
                progress_bar.progress((i + 1) / total)
                status_text.text(f"Recherche {i+1}/{total} : {query[:60]}...")

            search_results = search_signals(selected_signals, selected_geo, progress_callback=search_progress)
            progress_bar.progress(1.0)
            st.success(f"✅ {len(search_results)} résultats trouvés")

            # Étape 2 : Extraction
            st.markdown("### 🧠 Étape 2/4 — Extraction des prospects (LLM)")
            progress_bar2 = st.progress(0)
            status_text2 = st.empty()

            def extract_progress(i, total):
                progress_bar2.progress((i + 1) / total)
                status_text2.text(f"Analyse batch {i+1}/{total}... (pause rate limit entre chaque)")

            prospects = extract_prospects(search_results, progress_callback=extract_progress)
            progress_bar2.progress(1.0)
            st.success(f"✅ {len(prospects)} prospects identifiés")

            if prospects:
                # Étape 3 : Scoring
                st.markdown("### 📊 Étape 3/4 — Scoring & qualification")
                progress_bar3 = st.progress(0)
                status_text3 = st.empty()

                def score_progress(i, total):
                    progress_bar3.progress((i + 1) / total)
                    status_text3.text(f"Scoring batch {i+1}/{total}...")

                prospects = score_prospects(prospects, progress_callback=score_progress)
                progress_bar3.progress(1.0)
                qualified = [p for p in prospects if p.get("qualified")]
                st.success(f"✅ {len(qualified)} prospects qualifiés (score ≥ {SCORE_THRESHOLD})")

                # Étape 4 : Messages
                st.markdown("### ✉️ Étape 4/4 — Génération des messages d'approche")
                progress_bar4 = st.progress(0)
                status_text4 = st.empty()

                def msg_progress(i, total):
                    progress_bar4.progress((i + 1) / total)
                    status_text4.text(f"Message {i+1}/{total}...")

                prospects = generate_messages(prospects, progress_callback=msg_progress)
                progress_bar4.progress(1.0)
                st.success("✅ Messages générés")
            else:
                st.warning("Aucun prospect pertinent détecté. Essayez d'élargir les signaux ou les zones.")

        # Sauvegarder
        st.session_state.prospects = prospects
        st.session_state.search_done = True
        save_prospects(prospects)

# --- Affichage des résultats ---
if st.session_state.search_done and st.session_state.prospects:
    prospects = st.session_state.prospects

    # Filtres
    if not show_all:
        filtered = [
            p for p in prospects
            if p.get("score", 0) >= score_min and p.get("priority", "cold") in priority_filter
        ]
    else:
        filtered = [p for p in prospects if p.get("priority", "cold") in priority_filter]

    # Métriques
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class="metric-card">
                <div class="value">{len(prospects)}</div>
                <div class="label">Prospects détectés</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        qualified_count = len([p for p in prospects if p.get("qualified")])
        st.markdown(
            f"""<div class="metric-card">
                <div class="value">{qualified_count}</div>
                <div class="label">Qualifiés (≥{SCORE_THRESHOLD})</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        hot_count = len([p for p in prospects if p.get("priority") == "hot"])
        st.markdown(
            f"""<div class="metric-card">
                <div class="value">{hot_count}</div>
                <div class="label">🔴 Hot leads</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        avg_score = sum(p.get("score", 0) for p in prospects) / max(len(prospects), 1)
        st.markdown(
            f"""<div class="metric-card">
                <div class="value">{avg_score:.0f}</div>
                <div class="label">Score moyen</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Tableau
    if filtered:
        st.markdown(f"### 📋 Prospects ({len(filtered)} affichés)")

        table_data = []
        for p in filtered:
            signal_info = SIGNAL_LABELS.get(p.get("signal_type", ""), {})
            priority_info = PRIORITY_LABELS.get(p.get("priority", "cold"), {})
            table_data.append({
                "Entreprise": p.get("company_name", "Inconnu"),
                "Signal": f"{signal_info.get('emoji', '')} {signal_info.get('label', p.get('signal_type', ''))}",
                "Score": p.get("score", 0),
                "Priorité": priority_info.get("label", ""),
                "Localisation": p.get("location", ""),
                "Timing": p.get("estimated_date", "Inconnu"),
                "Deal estimé": p.get("deal_estimate", "N/A"),
            })

        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    min_value=0,
                    max_value=100,
                    format="%d",
                ),
            },
        )

        # Fiches détaillées
        st.markdown("### 📇 Fiches détaillées")

        for prospect in filtered:
            signal_info = SIGNAL_LABELS.get(prospect.get("signal_type", ""), {})
            priority_info = PRIORITY_LABELS.get(prospect.get("priority", "cold"), {})
            score = prospect.get("score", 0)
            company = prospect.get("company_name", "Inconnu")

            with st.expander(
                f"{priority_info.get('label', '')} **{company}** — Score: {score}/100 — {signal_info.get('emoji', '')} {signal_info.get('label', '')}"
            ):
                col_info, col_score = st.columns([2, 1])

                with col_info:
                    st.markdown("#### 🏢 Informations")
                    st.markdown(f"**Entreprise** : {company}")
                    st.markdown(f"**Localisation** : {prospect.get('location', 'N/A')}")

                    # Données enrichies si disponibles
                    company_data = prospect.get("company_data", {})
                    if company_data:
                        if company_data.get("siren"):
                            st.markdown(f"**SIREN** : `{company_data['siren']}`")
                        if company_data.get("effectifs"):
                            st.markdown(f"**Effectifs** : {company_data['effectifs']}")
                        if company_data.get("chiffre_affaires"):
                            st.markdown(f"**CA** : {company_data['chiffre_affaires']}")
                        dirigeants = company_data.get("dirigeants", [])
                        if dirigeants:
                            st.markdown(f"**Dirigeants** : {', '.join(dirigeants)}")

                    st.markdown("#### 📡 Signal détecté")
                    st.markdown(f"**Type** : {signal_info.get('emoji', '')} {signal_info.get('label', '')}")
                    st.markdown(f"**Détails** : {prospect.get('project_details', 'N/A')}")
                    st.markdown(f"**Date estimée** : {prospect.get('estimated_date', 'Inconnu')}")
                    if prospect.get("source_url"):
                        st.markdown(f"**Source** : [{prospect['source_url'][:60]}...]({prospect['source_url']})")

                with col_score:
                    priority = prospect.get("priority", "cold")
                    priority_css = priority if priority in ("hot", "warm", "cold") else "cold"
                    st.markdown(
                        f"""<div class="score-gauge">
                            <div class="score-number {priority_css}">{score}</div>
                            <div class="score-label">/ 100</div>
                        </div>
                        <div class="score-bar-container">
                            <div class="score-bar-fill {priority_css}" style="width:{score}%"></div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                    breakdown = prospect.get("score_breakdown", {})
                    if breakdown:
                        label_map = {
                            "pertinence": ("Pertinence", 30),
                            "pertinence_metier": ("Pertinence", 30),
                            "deal_size": ("Taille deal", 20),
                            "taille_deal": ("Taille deal", 20),
                            "urgence": ("Urgence", 25),
                            "urgence_timing": ("Urgence", 25),
                            "geo": ("Proximite geo", 15),
                            "proximite_geo": ("Proximite geo", 15),
                            "signal_quality": ("Qualite signal", 10),
                            "qualite_signal": ("Qualite signal", 10),
                        }
                        bars_html = ""
                        for key, val in breakdown.items():
                            lbl, max_val = label_map.get(key, (key, 30))
                            try:
                                num_val = int(val)
                            except (ValueError, TypeError):
                                num_val = 0
                            pct = min(100, int(num_val / max(max_val, 1) * 100))
                            bars_html += f"""<div class="score-breakdown-row">
                                <span class="sb-label">{lbl}</span>
                                <div class="sb-bar-bg"><div class="sb-bar-fill" style="width:{pct}%"></div></div>
                                <span class="sb-value">{num_val}</span>
                            </div>"""
                        st.markdown(bars_html, unsafe_allow_html=True)

                    st.markdown(f"**Deal estime** : {prospect.get('deal_estimate', 'N/A')}")
                    if prospect.get("approach_angle"):
                        st.markdown(f"**Angle** : {prospect.get('approach_angle')}")

                # Messages d'approche
                messages = prospect.get("messages", {})
                if messages and (messages.get("email_body") or messages.get("whatsapp")):
                    st.markdown("---")
                    st.markdown("#### ✉️ Messages d'approche")

                    tab_email, tab_whatsapp = st.tabs(["📧 Email", "💬 WhatsApp"])

                    with tab_email:
                        if messages.get("email_subject"):
                            st.markdown(f"**Objet** : {messages['email_subject']}")
                        if messages.get("email_body"):
                            st.markdown(
                                f"""<div class="message-box email">{messages['email_body']}</div>""",
                                unsafe_allow_html=True,
                            )
                            st.code(
                                f"Objet: {messages.get('email_subject', '')}\n\n{messages['email_body']}",
                                language=None,
                            )

                    with tab_whatsapp:
                        if messages.get("whatsapp"):
                            st.markdown(
                                f"""<div class="message-box whatsapp">{messages['whatsapp']}</div>""",
                                unsafe_allow_html=True,
                            )
                            st.code(messages["whatsapp"], language=None)

        # Export CSV
        st.markdown("---")
        export_data = []
        for p in filtered:
            cd = p.get("company_data", {})
            msgs = p.get("messages", {})
            export_data.append({
                "Entreprise": p.get("company_name", ""),
                "Signal": p.get("signal_type", ""),
                "Score": p.get("score", 0),
                "Priorité": p.get("priority", ""),
                "Localisation": p.get("location", ""),
                "Détails": p.get("project_details", ""),
                "Date estimée": p.get("estimated_date", ""),
                "Deal estimé": p.get("deal_estimate", ""),
                "Angle approche": p.get("approach_angle", ""),
                "Email objet": msgs.get("email_subject", ""),
                "Email corps": msgs.get("email_body", ""),
                "WhatsApp": msgs.get("whatsapp", ""),
                "Source URL": p.get("source_url", ""),
            })

        df_export = pd.DataFrame(export_data)
        csv = df_export.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Exporter en CSV",
            data=csv,
            file_name="prospects_capvisio.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("Aucun prospect ne correspond aux filtres sélectionnés.")

    st.markdown('</div>', unsafe_allow_html=True)  # close results-container

elif not st.session_state.search_done:
    st.markdown(
        """
        <div style="text-align: center; padding: 4rem 2rem; color: #8B8FA3;">
            <h2>👆 Configurez vos paramètres et lancez une recherche</h2>
            <p>L'agent va détecter automatiquement les signaux d'achat<br>
            et qualifier les prospects pour CapVisio.</p>
            <p style="margin-top: 1rem; font-size: 0.9rem;">
                💡 Ou cliquez sur <b>"Charger résultats précédents"</b> dans la sidebar
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
