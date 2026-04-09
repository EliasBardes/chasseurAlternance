import asyncio
import csv
import json
import logging
from scraper import JobScraper
from llm_processor import LLMProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("Démarrage du pipeline de recherche d'alternance pour Elias Bardes.")
    
    # 1. Scraping
    scraper = JobScraper()
    jobs = await scraper.run()
    logger.info(f"Scraping terminé. {len(jobs)} offres trouvées.")
    
    # 2. Analyse LLM
    processor = LLMProcessor()
    processed_jobs = []
    
    for i, job in enumerate(jobs):
        logger.info(f"Analyse de l'offre {i+1}/{len(jobs)} : {job['title']} chez {job['company']}")
        analysis = processor.analyze_job(job['title'], job['company'], job.get('description', ''))
        
        if analysis:
            # Combine scraped data and LLM analysis
            full_job_data = {
                "source": job['source'],
                "link": job['link'],
                "title": job['title'],
                "company": analysis.get("company_name", job['company']),
                "contact": analysis.get("contact_info", "N/A"),
                "key_skills": ", ".join(analysis.get("key_skills", [])) if isinstance(analysis.get("key_skills"), list) else analysis.get("key_skills", ""),
                "relevance_score": analysis.get("relevance_score", 0),
                "personalized_email": analysis.get("personalized_email", "")
            }
            processed_jobs.append(full_job_data)
        else:
            logger.warning(f"L'analyse a échoué pour {job['title']}")

    # 3. Stockage CSV
    output_file = "opportunites.csv"
    keys = ["title", "company", "relevance_score", "key_skills", "contact", "link", "source", "personalized_email"]
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(processed_jobs)
        logger.info(f"Résultats enregistrés dans {output_file}")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement CSV : {e}")

    logger.info("Pipeline terminé avec succès.")

if __name__ == "__main__":
    asyncio.run(main())