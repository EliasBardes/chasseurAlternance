"""
Script lancé chaque matin par cron.
Priorité : offres les plus récentes, puis score mixte récence + probabilité embauche.
"""
import asyncio
import csv
import logging
import os
from datetime import datetime, date
from scraper import JobScraper
from company_researcher import batch_research
from llm_processor import LLMProcessor
from email_sender import send_daily_link

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def recency_bonus(posted_date: str) -> float:
    """Bonus de 0 à 3 selon la fraîcheur de l'offre."""
    try:
        posted = datetime.strptime(posted_date, "%Y-%m-%d").date()
        days_old = (date.today() - posted).days
        if days_old <= 1:  return 3.0
        if days_old <= 3:  return 2.5
        if days_old <= 7:  return 2.0
        if days_old <= 14: return 1.0
        return 0.0
    except Exception:
        return 0.0

async def main():
    logger.info("=== Pipeline quotidien démarré ===")

    # 1. Scraping (déjà trié par date)
    scraper = JobScraper()
    raw_jobs = await scraper.run()
    logger.info(f"{len(raw_jobs)} offres scrapées")

    # 2. Recherche entreprises en parallèle
    companies = list({j["company"] for j in raw_jobs if j["company"] not in ("", "N/A")})
    logger.info(f"Recherche web pour {len(companies)} entreprises...")
    company_data = await batch_research(companies)

    # 3. Analyse LLM
    processor = LLMProcessor()
    processed = []

    for i, job in enumerate(raw_jobs):
        logger.info(f"Analyse {i+1}/{len(raw_jobs)} : {job['title']} @ {job['company']}")
        research = company_data.get(job["company"], {})
        analysis = processor.analyze_job(
            job["title"], job["company"],
            job.get("description", ""),
            job.get("posted_date", ""),
            research
        )
        if not analysis:
            continue

        key_skills = analysis.get("key_skills", [])
        relevance  = analysis.get("relevance_score", 0)
        hire_prob  = analysis.get("hire_probability", 0)
        bonus      = recency_bonus(job.get("posted_date", ""))

        # Score final : 50% pertinence + 30% probabilité embauche + bonus récence
        final_score = round(relevance * 0.5 + hire_prob * 0.3 + bonus, 1)

        processed.append({
            "source":              job["source"],
            "link":                job["link"],
            "title":               job["title"],
            "company":             analysis.get("company_name", job["company"]),
            "posted_date":         job.get("posted_date", ""),
            "contact":             analysis.get("contact_info", "N/A"),
            "key_skills":          ", ".join(key_skills) if isinstance(key_skills, list) else str(key_skills),
            "relevance_score":     relevance,
            "hire_probability":    hire_prob,
            "recency_bonus":       bonus,
            "final_score":         final_score,
            "company_insight":     analysis.get("company_alternant_insight", ""),
            "alternant_data_score": research.get("alternant_data_score", 0),
            "personalized_email":  analysis.get("personalized_email", ""),
        })

    # Tri final : score final décroissant
    processed.sort(key=lambda j: j["final_score"], reverse=True)

    # 4. CSV
    keys = [
        "title", "company", "posted_date", "final_score", "relevance_score",
        "hire_probability", "recency_bonus", "alternant_data_score",
        "key_skills", "company_insight", "contact", "link", "source", "personalized_email"
    ]
    with open("opportunites.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(processed)
    logger.info("CSV sauvegardé : opportunites.csv")

    # 5. Email avec lien de l'app
    recipient = os.environ.get("RECIPIENT_EMAIL")
    if recipient:
        send_daily_link(processed[:10], recipient)
    else:
        logger.warning("RECIPIENT_EMAIL non défini — email non envoyé")

    logger.info("=== Pipeline terminé ===")

if __name__ == "__main__":
    asyncio.run(main())
