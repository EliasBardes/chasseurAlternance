"""
Recherche la reputation alternance data d'une entreprise via DuckDuckGo.
Retourne un score et un resume utilisable par le LLM.
"""
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}


def research_company(session, company_name: str) -> dict:
    if not company_name or company_name in ("N/A", ""):
        return {"alternant_data_count": 0, "summary": "Entreprise inconnue"}

    query = f"{company_name} alternance data analyst site:linkedin.com OR site:welcometothejungle.com OR site:indeed.fr"
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}&kl=fr-fr"

    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results = soup.select(".result__snippet")
        snippets = []
        for r in results[:5]:
            text = r.get_text(strip=True)
            if text:
                snippets.append(text)

        full_text = " ".join(snippets).lower()
        score = 0
        score += full_text.count("alternant") * 2
        score += full_text.count("alternance") * 2
        score += full_text.count("data analyst") * 3
        score += full_text.count("data science") * 2
        score += full_text.count("recrutement") * 1
        score += full_text.count("stage") * 1

        summary = (" | ".join(snippets[:3]))[:300] if snippets else "Aucun resultat trouve"
        logger.info(f"[{company_name}] score alternance data = {score}")
        return {"alternant_data_score": min(score, 20), "summary": summary}

    except Exception as e:
        logger.warning(f"Recherche echouee pour {company_name}: {e}")
        return {"alternant_data_score": 0, "summary": "Recherche indisponible"}


async def batch_research(companies: list[str]) -> dict:
    session = requests.Session()
    session.headers.update(HEADERS)

    results = {}
    seen = set()
    for company in companies:
        if company in seen or not company or company == "N/A":
            continue
        seen.add(company)
        results[company] = research_company(session, company)

    return results
