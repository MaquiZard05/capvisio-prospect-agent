"""
Pipeline complet : search → extract → score → message → save
Cache après chaque étape — jamais de double appel sur un prospect déjà traité.
Usage : python run_pipeline.py [--signals demenagement,construction] [--max 3] [--geo Nantes,Rennes]
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from src.config import (
    DEFAULT_SIGNAL_TYPES, DEFAULT_GEO_ZONES, SCORE_THRESHOLD,
    MODEL_EXTRACT, MODEL_SCORE, MODEL_MESSAGE, PROSPECTS_FILE,
)
from src.search import search_signals
from src.extract import extract_prospects
from src.score import score_prospects
from src.message import generate_messages


def _save_cache(prospects, search_params, step: str):
    """Sauvegarde intermédiaire après chaque étape."""
    PROSPECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "last_search": datetime.now().isoformat(),
        "last_step": step,
        "search_params": search_params,
        "prospects": prospects,
    }
    with open(PROSPECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def _load_cache() -> tuple[list[dict], dict]:
    """Charge le cache existant."""
    if not PROSPECTS_FILE.exists():
        return [], {}
    try:
        with open(PROSPECTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data.get("prospects", []), data.get("search_params", {})
        if isinstance(data, list):
            return data, {}
    except Exception:
        pass
    return [], {}


def run(signal_types=None, geo_zones=None, max_results=3, fresh=False):
    signal_types = signal_types or DEFAULT_SIGNAL_TYPES
    geo_zones = geo_zones or ["Nantes", "Rennes", "Paris"]
    search_params = {
        "signal_types": signal_types,
        "geo_zones": geo_zones,
        "max_results_per_query": max_results,
    }

    print(f"\n{'='*60}")
    print(f"  AGENT PROSPECTEUR CAPVISIO — Pipeline")
    print(f"  Signaux : {', '.join(signal_types)}")
    print(f"  Zones : {', '.join(geo_zones)}")
    print(f"  Modèles : Extract={MODEL_EXTRACT} | Score={MODEL_SCORE} | Msg={MODEL_MESSAGE}")
    print(f"{'='*60}\n")

    # Charger le cache existant
    cached_prospects, cached_params = _load_cache()
    if cached_prospects and not fresh:
        print(f"📦 Cache chargé : {len(cached_prospects)} prospects existants")
    else:
        cached_prospects = []

    # 1. SEARCH
    print("🔍 Étape 1/4 — Recherche web (Google News RSS)...")
    start = time.time()
    search_results = search_signals(signal_types, geo_zones, max_results_per_query=max_results)
    print(f"   ✅ {len(search_results)} résultats bruts trouvés ({time.time()-start:.1f}s)")

    if not search_results and not cached_prospects:
        print("   ❌ Aucun résultat. Vérifiez la connexion internet.")
        return

    # 2. EXTRACT (skip prospects déjà extraits)
    print(f"\n🧠 Étape 2/4 — Extraction des prospects ({MODEL_EXTRACT})...")
    start = time.time()

    def extract_cb(i, total):
        print(f"   Batch {i+1}/{total}...", end="\r")

    prospects = extract_prospects(search_results, existing_prospects=cached_prospects, progress_callback=extract_cb)
    new_count = len(prospects) - len(cached_prospects)
    print(f"   ✅ {len(prospects)} prospects total ({new_count} nouveaux) ({time.time()-start:.1f}s)")

    _save_cache(prospects, search_params, "extract")

    if not prospects:
        print("   ⚠️ Aucun prospect pertinent trouvé.")
        return

    # 3. SCORE (skip prospects déjà scorés)
    print(f"\n📊 Étape 3/4 — Scoring & qualification ({MODEL_SCORE})...")
    start = time.time()

    def score_cb(i, total):
        print(f"   Batch {i+1}/{total}...", end="\r")

    prospects = score_prospects(prospects, progress_callback=score_cb)
    hot = [p for p in prospects if p.get("priority") == "hot"]
    warm = [p for p in prospects if p.get("priority") == "warm"]
    cold = [p for p in prospects if p.get("priority") == "cold"]
    print(f"   ✅ 🔴 {len(hot)} hot | 🟠 {len(warm)} warm | 🔵 {len(cold)} cold ({time.time()-start:.1f}s)")

    _save_cache(prospects, search_params, "score")

    # 4. MESSAGE (skip prospects qui ont déjà des messages)
    print(f"\n✉️ Étape 4/4 — Génération des messages ({MODEL_MESSAGE})...")
    start = time.time()
    qualified = [p for p in prospects if p.get("qualified")]

    def msg_cb(i, total):
        print(f"   Message {i+1}/{total}...", end="\r")

    prospects = generate_messages(prospects, progress_callback=msg_cb)
    print(f"   ✅ {len(qualified)} prospects qualifiés avec messages ({time.time()-start:.1f}s)")

    _save_cache(prospects, search_params, "complete")

    # RÉSUMÉ
    print(f"\n{'='*60}")
    print(f"  RÉSUMÉ — {len(prospects)} prospects")
    print(f"{'='*60}")

    for p in prospects:
        score = p.get("score", 0)
        priority = p.get("priority", "cold")
        badge = {"hot": "🔴", "warm": "🟠", "cold": "🔵"}.get(priority, "⚪")
        company = p.get("company_name", "Inconnu")
        signal = p.get("signal_type", "")
        location = p.get("location", "")
        deal = p.get("deal_estimate", "N/A")

        print(f"\n  {badge} [{score}/100] {company}")
        print(f"     Signal: {signal} | Lieu: {location} | Deal: {deal}")

        if p.get("messages", {}).get("email_subject"):
            print(f"     Email: {p['messages']['email_subject']}")

    print(f"\n{'='*60}")
    print(f"  💾 Cache sauvé dans {PROSPECTS_FILE}")
    print(f"  Lancer `streamlit run app.py` pour le dashboard.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Prospecteur CapVisio — Pipeline CLI")
    parser.add_argument("--signals", type=str, default=None,
                        help="Types de signaux séparés par des virgules")
    parser.add_argument("--max", type=int, default=3,
                        help="Nombre max de résultats par requête (défaut: 3)")
    parser.add_argument("--geo", type=str, default=None,
                        help="Zones géo séparées par des virgules")
    parser.add_argument("--fresh", action="store_true",
                        help="Ignorer le cache et tout recalculer")
    args = parser.parse_args()

    signals = args.signals.split(",") if args.signals else None
    geos = args.geo.split(",") if args.geo else None
    run(signal_types=signals, geo_zones=geos, max_results=args.max, fresh=args.fresh)
