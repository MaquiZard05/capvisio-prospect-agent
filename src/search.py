"""Module de recherche web — Google News RSS + fallback DuckDuckGo News."""

import json
import time
import re
import requests
import feedparser
from pathlib import Path
from src.config import SEARCH_MAX_RESULTS, CURRENT_YEAR

QUERIES_PATH = Path(__file__).parent.parent / "data" / "search_queries.json"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"


def load_query_templates() -> dict:
    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _clean_html(text: str) -> str:
    """Nettoie le HTML des résumés RSS."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _search_google_news(query: str, max_results: int = 5) -> list[dict]:
    """Recherche via Google News RSS."""
    url = GOOGLE_NEWS_RSS.format(query=requests.utils.quote(query))
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CapVisioBot/1.0)"
        })
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        results = []
        for entry in feed.entries[:max_results]:
            results.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "snippet": _clean_html(entry.get("summary", entry.get("description", ""))),
                "published": entry.get("published", ""),
            })
        return results
    except Exception as e:
        print(f"   ⚠️ Google News échoué: {e}")
        return []


def _search_ddg_news(query: str, max_results: int = 5) -> list[dict]:
    """Fallback : DuckDuckGo en mode news."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.news(query, region="fr-fr", max_results=max_results))
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", r.get("href", "")),
                "snippet": r.get("body", ""),
                "published": r.get("date", ""),
            }
            for r in results
        ]
    except Exception as e:
        print(f"   ⚠️ DuckDuckGo News échoué: {e}")
        return []


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
    """Recherche des signaux d'achat via Google News RSS + fallback DDG."""
    queries = build_queries(signal_types, geo_zones)
    all_results = []
    seen_urls = set()

    for i, q in enumerate(queries):
        if progress_callback:
            progress_callback(i, len(queries), q["query"])

        # Google News RSS en priorité
        results = _search_google_news(q["query"], max_results=max_results_per_query)

        # Fallback DuckDuckGo News si Google News ne retourne rien
        if not results:
            results = _search_ddg_news(q["query"], max_results=max_results_per_query)

        for r in results:
            url = r.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            all_results.append({
                "title": r.get("title", ""),
                "url": url,
                "snippet": r.get("snippet", ""),
                "published": r.get("published", ""),
                "signal_type": q["signal_type"],
                "geo_zone": q["geo"],
                "query_used": q["query"],
            })

        # Pause entre requêtes
        time.sleep(2)

    return all_results
