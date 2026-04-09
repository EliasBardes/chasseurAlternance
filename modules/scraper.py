"""
Scraper multi-sites pour recherche interactive.
Mode requests + BeautifulSoup uniquement (compatible Render free tier).
"""
import logging
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTRACT_MAP = {
    "indeed": {"Alternance": "apprenticeship", "CDI": "permanent", "CDD": "contract", "Stage": "internship"},
    "wttj": {"Alternance": "apprenticeship", "CDI": "full-time", "CDD": "temporary", "Stage": "internship"},
    "hellowork": {"Alternance": "alternance", "CDI": "cdi", "CDD": "cdd", "Stage": "stage"},
    "linkedin": {"Alternance": "I", "CDI": "F", "CDD": "C", "Stage": "I"},
}

RADIUS_MAP = {5: "5", 10: "10", 20: "20", 50: "50", 100: "100"}

SITE_LABELS = {
    "indeed": "Indeed",
    "wttj": "Welcome to the Jungle",
    "hellowork": "HelloWork",
    "linkedin": "LinkedIn",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}


def _build_urls(job_title, contract_type, city="", radius_km=20):
    q = quote_plus(job_title)
    location = quote_plus(city) if city else "France"
    radius = RADIUS_MAP.get(radius_km, "20")

    return {
        "indeed": (
            f"https://fr.indeed.com/jobs?q={q}&l={location}&radius={radius}&fromage=7"
            + (f"&sc=0kf%3Ajt%28{CONTRACT_MAP['indeed'].get(contract_type, '')}%29%3B" if CONTRACT_MAP["indeed"].get(contract_type) else "")
        ),
        "wttj": (
            f"https://www.welcometothejungle.com/fr/jobs?query={q}"
            f"&refinementList%5Bcontract_type%5D%5B%5D={CONTRACT_MAP['wttj'].get(contract_type, '')}"
            + (f"&aroundQuery={quote_plus(city)}&aroundRadius={radius_km}" if city else "")
        ),
        "hellowork": (
            f"https://www.hellowork.com/fr-fr/emploi/recherche.html"
            f"?k={q}&l={location}&c={CONTRACT_MAP['hellowork'].get(contract_type, '')}&ray={radius}"
        ),
        "linkedin": (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={q}&location={location}&f_TPR=r604800&f_JT={CONTRACT_MAP['linkedin'].get(contract_type, 'F')}"
            f"&distance={radius}"
        ),
    }


def _scrape_linkedin(url, contract_type):
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select("div.base-card, div.job-search-card")[:20]:
            try:
                title_el = card.select_one("h3.base-search-card__title, h3")
                company_el = card.select_one("h4.base-search-card__subtitle, a.hidden-nested-link")
                location_el = card.select_one("span.job-search-card__location")
                link_el = card.select_one("a.base-card__full-link, a[href*='linkedin.com/jobs']")
                date_el = card.select_one("time")
                title = title_el.get_text(strip=True) if title_el else None
                if not title:
                    continue
                href = link_el["href"] if link_el and link_el.has_attr("href") else ""
                jobs.append({
                    "title": title,
                    "company": company_el.get_text(strip=True) if company_el else "N/A",
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "url": href or url,
                    "source": "LinkedIn",
                    "contract_type": contract_type,
                    "date_posted": date_el["datetime"] if date_el and date_el.has_attr("datetime") else None,
                })
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"LinkedIn scraping error: {e}")
    return jobs


def _scrape_indeed(url, contract_type):
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select("div.job_seen_beacon, div.resultContent, [data-jk]")[:20]:
            try:
                title_el = card.select_one("h2 a, h2 span")
                company_el = card.select_one("[data-testid='company-name'], span.css-1h7lukg")
                location_el = card.select_one("[data-testid='text-location'], div.css-1restlb")
                link_el = card.select_one("h2 a, a.jcs-JobTitle")
                title = title_el.get_text(strip=True) if title_el else None
                if not title:
                    continue
                href = link_el["href"] if link_el and link_el.has_attr("href") else ""
                if href and not href.startswith("http"):
                    href = "https://fr.indeed.com" + href
                jobs.append({
                    "title": title,
                    "company": company_el.get_text(strip=True) if company_el else "N/A",
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "url": href or url,
                    "source": "Indeed",
                    "contract_type": contract_type,
                    "date_posted": None,
                })
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"Indeed scraping error: {e}")
    return jobs


def _scrape_hellowork(url, contract_type):
    jobs = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select("li[class*='searchResult'], div[data-cy='search-results'] > div, a[href*='/fr-fr/emploi/']")[:20]:
            try:
                link_el = card.select_one("a[href*='/emploi/']")
                if not link_el and card.name == "a" and "/emploi/" in card.get("href", ""):
                    link_el = card
                if not link_el:
                    continue
                title_el = card.select_one("h3, h2, [class*='title']")
                company_el = card.select_one("[class*='company']")
                location_el = card.select_one("[class*='location'], [class*='city']")
                date_el = card.select_one("time, [class*='date']")
                title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
                if not title or len(title) < 3:
                    continue
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = "https://www.hellowork.com" + href
                jobs.append({
                    "title": title,
                    "company": company_el.get_text(strip=True) if company_el else "N/A",
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "url": href,
                    "source": "HelloWork",
                    "contract_type": contract_type,
                    "date_posted": date_el.get_text(strip=True) if date_el else None,
                })
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"HelloWork scraping error: {e}")
    return jobs


SCRAPERS = {
    "indeed": _scrape_indeed,
    "hellowork": _scrape_hellowork,
    "linkedin": _scrape_linkedin,
}


def scrape_all(job_title, contract_type, city="", radius_km=20, sites=None, on_progress=None):
    if not sites:
        sites = list(SCRAPERS.keys())
    urls = _build_urls(job_title, contract_type, city, radius_km)
    all_jobs = []
    total = len(sites)

    for i, site in enumerate(sites):
        if site not in SCRAPERS:
            if on_progress:
                on_progress(SITE_LABELS.get(site, site), i + 1, total, len(all_jobs))
            continue
        logger.info(f"Scraping {site} pour '{job_title}' ({contract_type})...")
        site_jobs = SCRAPERS[site](urls[site], contract_type)
        logger.info(f"  -> {len(site_jobs)} offres trouvees sur {site}")
        all_jobs.extend(site_jobs)
        if on_progress:
            on_progress(SITE_LABELS.get(site, site), i + 1, total, len(all_jobs))

    all_jobs = [
        j for j in all_jobs
        if "openclassroom" not in j.get("title", "").lower()
        and "openclassroom" not in j.get("company", "").lower()
    ]
    return all_jobs
