import logging
import re
import urllib.parse
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LINKEDIN_KEYWORDS = [
    "alternant Data Analyst",
    "alternance Data Analyst",
    "Data Analyst alternance",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def parse_linkedin_date(text: str) -> str:
    text = text.lower().strip()
    now = datetime.now()
    try:
        if "heure" in text or "hour" in text:
            n = int(re.search(r'\d+', text).group())
            return (now - timedelta(hours=n)).strftime("%Y-%m-%d")
        if "jour" in text or "day" in text:
            n = int(re.search(r'\d+', text).group())
            return (now - timedelta(days=n)).strftime("%Y-%m-%d")
        if "semaine" in text or "week" in text:
            n = int(re.search(r'\d+', text).group())
            return (now - timedelta(weeks=n)).strftime("%Y-%m-%d")
        if "mois" in text or "month" in text:
            n = int(re.search(r'\d+', text).group())
            return (now - timedelta(days=n * 30)).strftime("%Y-%m-%d")
    except Exception:
        pass
    return now.strftime("%Y-%m-%d")


class JobScraper:
    def __init__(self):
        self.results = []
        self._seen_links = set()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _add(self, source, title, company, link, posted_date=""):
        if link and link in self._seen_links:
            return
        self._seen_links.add(link)
        self.results.append({
            "source": source,
            "title": title,
            "company": company,
            "link": link,
            "description": "",
            "posted_date": posted_date or datetime.now().strftime("%Y-%m-%d"),
        })

    def scrape_linkedin(self, keyword, limit=4):
        encoded = urllib.parse.quote(keyword)
        url = f"https://www.linkedin.com/jobs/search?keywords={encoded}&location=France&f_TPR=r604800&f_JT=I&sortBy=DD"
        logger.info(f"Scraping LinkedIn [{keyword}]")
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = soup.select(".base-card")
            count = 0
            for job in jobs:
                if count >= limit:
                    break
                try:
                    title_el = job.select_one(".base-search-card__title")
                    company_el = job.select_one(".base-search-card__subtitle")
                    link_el = job.select_one("a.base-card__full-link")
                    date_el = job.select_one("time")
                    title = title_el.get_text(strip=True) if title_el else "N/A"
                    company = company_el.get_text(strip=True) if company_el else "N/A"
                    link = link_el["href"] if link_el and link_el.has_attr("href") else ""
                    date_txt = date_el.get_text(strip=True) if date_el else ""
                    posted = parse_linkedin_date(date_txt)
                    if title != "N/A":
                        self._add("LinkedIn", title, company, link, posted)
                        count += 1
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn job: {e}")
        except Exception as e:
            logger.error(f"LinkedIn scrape failed [{keyword}]: {e}")

    def scrape_wttj(self, limit=4):
        url = "https://www.welcometothejungle.com/fr/jobs?query=alternant+Data+Analyst&refinementList%5Bcontract_type%5D%5B%5D=alternance&aroundQuery=France&sortBy=published_at"
        logger.info("Scraping Welcome to the Jungle")
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = soup.select("li article")
            count = 0
            for job in jobs:
                if count >= limit:
                    break
                try:
                    title_el = job.select_one("h4")
                    company_el = job.select_one("span")
                    link_el = job.select_one("a")
                    date_el = job.select_one("time")
                    title = title_el.get_text(strip=True) if title_el else "N/A"
                    company = company_el.get_text(strip=True) if company_el else "N/A"
                    link = link_el["href"] if link_el and link_el.has_attr("href") else ""
                    posted = date_el["datetime"][:10] if date_el and date_el.has_attr("datetime") else ""
                    if not posted:
                        posted = datetime.now().strftime("%Y-%m-%d")
                    if link and not link.startswith("http"):
                        link = "https://www.welcometothejungle.com" + link
                    if title != "N/A":
                        self._add("WTTJ", title, company, link, posted)
                        count += 1
                except Exception as e:
                    logger.error(f"Error parsing WTTJ job: {e}")
        except Exception as e:
            logger.error(f"WTTJ scrape failed: {e}")

    def scrape_hellowork(self, limit=4):
        url = "https://www.hellowork.com/fr-fr/emploi/recherche.html?k=alternant+data+analyst&c=Alternance&l=France&tri=date"
        logger.info("Scraping HelloWork")
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = soup.select("[data-cy='offerList'] li")
            if not jobs:
                jobs = soup.select("article.job-card, li[class*='job']")
            count = 0
            for job in jobs:
                if count >= limit:
                    break
                try:
                    title_el = job.select_one("h2, h3, [data-cy='offerTitle']")
                    company_el = job.select_one("[class*='company'], [data-cy='offerCompany']")
                    link_el = job.select_one("a")
                    date_el = job.select_one("time, [class*='date']")
                    title = title_el.get_text(strip=True) if title_el else "N/A"
                    company = company_el.get_text(strip=True) if company_el else "N/A"
                    link = link_el["href"] if link_el and link_el.has_attr("href") else ""
                    posted = date_el.get_text(strip=True) if date_el else ""
                    posted = parse_linkedin_date(posted) if posted else datetime.now().strftime("%Y-%m-%d")
                    if link and not link.startswith("http"):
                        link = "https://www.hellowork.com" + link
                    if title != "N/A":
                        self._add("HelloWork", title, company, link, posted)
                        count += 1
                except Exception as e:
                    logger.error(f"Error parsing HelloWork job: {e}")
        except Exception as e:
            logger.error(f"HelloWork scrape failed: {e}")

    def get_job_description(self, job):
        url = job.get("link", "")
        if not url or not url.startswith("http"):
            return
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            desc = ""
            if "linkedin.com" in url:
                el = soup.select_one(".description__text")
                if el:
                    desc = el.get_text(strip=True)
            elif "welcometothejungle.com" in url:
                el = soup.select_one("main")
                if el:
                    desc = el.get_text(strip=True)
            elif "hellowork.com" in url:
                el = soup.select_one("[class*='description'], main")
                if el:
                    desc = el.get_text(strip=True)
            job["description"] = desc.strip()
        except Exception as e:
            logger.error(f"Error getting description for {url}: {e}")

    async def run(self):
        for keyword in LINKEDIN_KEYWORDS:
            self.scrape_linkedin(keyword, limit=4)
        self.scrape_wttj(limit=4)
        self.scrape_hellowork(limit=4)

        for job in self.results:
            logger.info(f"Description: {job['title']} @ {job['company']}")
            self.get_job_description(job)

        self.results.sort(key=lambda j: j.get("posted_date", ""), reverse=True)
        return self.results[:20]
