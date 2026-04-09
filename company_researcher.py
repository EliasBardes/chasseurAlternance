"""
Recherche la réputation alternance data d'une entreprise via DuckDuckGo.
Retourne un score et un résumé utilisable par le LLM.
"""
import asyncio
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

async def research_company(page, company_name: str) -> dict:
    """Cherche sur DuckDuckGo combien d'alternants data cette boite recrute."""
    if not company_name or company_name in ("N/A", ""):
        return {"alternant_data_count": 0, "summary": "Entreprise inconnue"}

    query = f"{company_name} alternance data analyst site:linkedin.com OR site:welcometothejungle.com OR site:indeed.fr"
    url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&kl=fr-fr"

    try:
        await page.goto(url, timeout=15000)
        await page.wait_for_selector("[data-result='web'], .result", timeout=8000)

        results = await page.query_selector_all("[data-result='web'], .result")
        snippets = []
        for r in results[:5]:
            try:
                text_el = await r.query_selector(".result__snippet, [class*='snippet'], span")
                if text_el:
                    snippets.append((await text_el.inner_text()).strip())
            except Exception:
                pass

        # Compte les occurrences de mots-clés positifs
        full_text = " ".join(snippets).lower()
        score = 0
        score += full_text.count("alternant") * 2
        score += full_text.count("alternance") * 2
        score += full_text.count("data analyst") * 3
        score += full_text.count("data science") * 2
        score += full_text.count("recrutement") * 1
        score += full_text.count("stage") * 1

        summary = (" | ".join(snippets[:3]))[:300] if snippets else "Aucun résultat trouvé"
        logger.info(f"[{company_name}] score alternance data = {score}")
        return {"alternant_data_score": min(score, 20), "summary": summary}

    except Exception as e:
        logger.warning(f"Recherche échouée pour {company_name}: {e}")
        return {"alternant_data_score": 0, "summary": "Recherche indisponible"}


async def batch_research(companies: list[str]) -> dict:
    """Recherche en lot, une seule instance Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )
        page = await browser.new_page()
        await page.set_extra_http_headers({"Accept-Language": "fr-FR,fr;q=0.9"})

        results = {}
        seen = set()
        for company in companies:
            if company in seen or not company or company == "N/A":
                continue
            seen.add(company)
            results[company] = await research_company(page, company)

        await browser.close()
    return results
