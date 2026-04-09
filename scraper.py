import asyncio
from playwright.async_api import async_playwright
import json
import logging
from datetime import datetime, timedelta
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LINKEDIN_KEYWORDS = [
    "alternant Data Analyst",
    "alternance Data Analyst",
    "Data Analyst alternance",
]

def parse_linkedin_date(text: str) -> str:
    """Convertit le texte relatif LinkedIn en date ISO."""
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
            return (now - timedelta(days=n*30)).strftime("%Y-%m-%d")
    except Exception:
        pass
    return now.strftime("%Y-%m-%d")

class JobScraper:
    def __init__(self):
        self.results = []
        self._seen_links = set()

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

    async def scrape_linkedin(self, page, keyword, limit=4):
        import urllib.parse
        encoded = urllib.parse.quote(keyword)
        url = f"https://www.linkedin.com/jobs/search?keywords={encoded}&location=France&f_TPR=r604800&f_JT=I&sortBy=DD"
        logger.info(f"Scraping LinkedIn [{keyword}]")
        try:
            await page.goto(url)
            await page.wait_for_selector(".base-card", timeout=12000)
            jobs = await page.query_selector_all(".base-card")
            count = 0
            for job in jobs:
                if count >= limit:
                    break
                try:
                    title_el   = await job.query_selector(".base-search-card__title")
                    company_el = await job.query_selector(".base-search-card__subtitle")
                    link_el    = await job.query_selector("a.base-card__full-link")
                    date_el    = await job.query_selector("time")
                    title   = (await title_el.inner_text()).strip()   if title_el   else "N/A"
                    company = (await company_el.inner_text()).strip() if company_el else "N/A"
                    link    = await link_el.get_attribute("href")     if link_el    else ""
                    date_txt = await date_el.inner_text()             if date_el    else ""
                    posted  = parse_linkedin_date(date_txt)
                    if title != "N/A":
                        self._add("LinkedIn", title, company, link, posted)
                        count += 1
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn job: {e}")
        except Exception as e:
            logger.error(f"LinkedIn scrape failed [{keyword}]: {e}")

    async def scrape_wttj(self, page, limit=4):
        url = "https://www.welcometothejungle.com/fr/jobs?query=alternant+Data+Analyst&refinementList%5Bcontract_type%5D%5B%5D=alternance&aroundQuery=France&sortBy=published_at"
        logger.info("Scraping Welcome to the Jungle")
        try:
            await page.goto(url)
            await page.wait_for_selector("li article", timeout=12000)
            jobs = await page.query_selector_all("li article")
            count = 0
            for job in jobs:
                if count >= limit:
                    break
                try:
                    title_el   = await job.query_selector("h4")
                    company_el = await job.query_selector("span")
                    link_el    = await job.query_selector("a")
                    date_el    = await job.query_selector("time")
                    title   = (await title_el.inner_text()).strip()   if title_el   else "N/A"
                    company = (await company_el.inner_text()).strip() if company_el else "N/A"
                    link    = await link_el.get_attribute("href")     if link_el    else ""
                    posted  = await date_el.get_attribute("datetime") if date_el    else ""
                    if posted:
                        posted = posted[:10]
                    else:
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

    async def scrape_hellowork(self, page, limit=4):
        url = "https://www.hellowork.com/fr-fr/emploi/recherche.html?k=alternant+data+analyst&c=Alternance&l=France&tri=date"
        logger.info("Scraping HelloWork")
        try:
            await page.goto(url)
            await page.wait_for_selector("[data-cy='offerList'] li, article", timeout=12000)
            jobs = await page.query_selector_all("[data-cy='offerList'] li")
            if not jobs:
                jobs = await page.query_selector_all("article.job-card, li[class*='job']")
            count = 0
            for job in jobs:
                if count >= limit:
                    break
                try:
                    title_el   = await job.query_selector("h2, h3, [data-cy='offerTitle']")
                    company_el = await job.query_selector("[class*='company'], [data-cy='offerCompany']")
                    link_el    = await job.query_selector("a")
                    date_el    = await job.query_selector("time, [class*='date']")
                    title   = (await title_el.inner_text()).strip()   if title_el   else "N/A"
                    company = (await company_el.inner_text()).strip() if company_el else "N/A"
                    link    = await link_el.get_attribute("href")     if link_el    else ""
                    posted  = await date_el.inner_text()              if date_el    else ""
                    posted  = parse_linkedin_date(posted) if posted else datetime.now().strftime("%Y-%m-%d")
                    if link and not link.startswith("http"):
                        link = "https://www.hellowork.com" + link
                    if title != "N/A":
                        self._add("HelloWork", title, company, link, posted)
                        count += 1
                except Exception as e:
                    logger.error(f"Error parsing HelloWork job: {e}")
        except Exception as e:
            logger.error(f"HelloWork scrape failed: {e}")

    async def get_job_description(self, page, job):
        url = job.get("link", "")
        if not url or not url.startswith("http"):
            return
        try:
            await page.goto(url)
            desc = ""
            if "linkedin.com" in url:
                el = await page.query_selector(".description__text")
                if el: desc = await el.inner_text()
            elif "welcometothejungle.com" in url:
                el = await page.query_selector("main")
                if el: desc = await el.inner_text()
            elif "hellowork.com" in url:
                el = await page.query_selector("[class*='description'], main")
                if el: desc = await el.inner_text()
            job["description"] = desc.strip()
        except Exception as e:
            logger.error(f"Error getting description for {url}: {e}")

    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers({"Accept-Language": "fr-FR,fr;q=0.9"})

            for keyword in LINKEDIN_KEYWORDS:
                await self.scrape_linkedin(page, keyword, limit=4)
            await self.scrape_wttj(page, limit=4)
            await self.scrape_hellowork(page, limit=4)

            for job in self.results:
                logger.info(f"Description: {job['title']} @ {job['company']}")
                await self.get_job_description(page, job)

            await browser.close()

        # Trier par date décroissante
        self.results.sort(key=lambda j: j.get("posted_date", ""), reverse=True)
        return self.results[:20]
