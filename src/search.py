"""Module de recherche web pour détecter les signaux d'achat."""

import json
from pathlib import Path
from duckduckgo_search import DDGS
from src.config import SEARCH_MAX_RESULTS, CURRENT_YEAR

QUERIES_PATH = Path(__file__).parent.parent / "data" / "search_queries.json"


def load_query_templates() -> dict:
    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_queries(signal_types: list[str], geo_zones: list[str]) -> list[dict]:
    """Construit les requêtes de recherche à partir des templates."""
    templates = load_query_templates()
    queries = []
    for signal in signal_types:
        if signal not in templates:
            continue
        for template in templates[signal]:
            for geo in geo_zones:
                query_text = template.format(geo=geo, year=CURRENT_YEAR)
                queries.append({"query": query_text, "signal_type": signal, "geo": geo})
    return queries


def search_signals(
    signal_types: list[str],
    geo_zones: list[str],
    max_results_per_query: int = SEARCH_MAX_RESULTS,
    progress_callback=None,
) -> list[dict]:
    """Recherche des signaux d'achat sur le web via DuckDuckGo.

    Returns:
        Liste de résultats bruts avec métadonnées de requête.
    """
    queries = build_queries(signal_types, geo_zones)
    all_results = []
    seen_urls = set()

    for i, q in enumerate(queries):
        if progress_callback:
            progress_callback(i, len(queries), q["query"])

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(q["query"], region="fr-fr", max_results=max_results_per_query))
        except Exception:
            results = []

        for r in results:
            url = r.get("href", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            all_results.append({
                "title": r.get("title", ""),
                "url": url,
                "snippet": r.get("body", ""),
                "signal_type": q["signal_type"],
                "geo_zone": q["geo"],
                "query_used": q["query"],
            })

    return all_results
