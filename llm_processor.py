import os
import json
from openai import OpenAI

class LLMProcessor:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("GROQ_API_KEY")
        )
        self.user_profile = {
            "name": "Elias Bardes",
            "age": 21,
            "school": "HETIC",
            "program": "Bachelor Data & AI",
            "skills": ["Python", "SQL", "Design"],
            "achievements": ["Prix 'Best Design' lors d'un hackathon (Data & Web)"]
        }

    def analyze_job(self, job_title, job_company, job_description, posted_date="", company_research=None):
        research_block = ""
        if company_research:
            research_block = f"""
        Données sur l'entreprise (recherche web) :
        - Score alternance data (0-20, plus c'est haut plus ils recrutent) : {company_research.get('alternant_data_score', 0)}
        - Résumé : {company_research.get('summary', '')}
        """

        prompt = f"""
        Tu es un expert en recrutement Data. Analyse cette offre pour Elias Bardes (étudiant HETIC Bachelor Data & AI, expert Python/SQL/Design, prix "Best Design" hackathon).

        Offre : {job_title} chez {job_company}
        Date de publication : {posted_date or "inconnue"}
        Description : {job_description[:2000]}
        {research_block}

        Réponds UNIQUEMENT avec ce JSON (pas de markdown, pas de texte autour) :
        {{
          "company_name": "nom exact",
          "contact_info": "email/nom recruteur ou N/A",
          "key_skills": ["skill1", "skill2", "skill3"],
          "hire_probability": <entier 1-10, probabilité qu'Elias soit pris en tenant compte de la récence et de l'historique alternance de la boite>,
          "relevance_score": <entier 1-10, adéquation profil/offre>,
          "company_alternant_insight": "1 phrase sur l'habitude de la boite à recruter des alternants data",
          "personalized_email": "brouillon ~150 mots, mentionne HETIC, prix Best Design, projets Python, ton pro mais percutant"
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None

if __name__ == "__main__":
    processor = LLMProcessor()
    # Test with a dummy job
    result = processor.analyze_job("Data Analyst Intern", "TechCorp", "We are looking for a data analyst with Python skills and design sensibility.")
    print(json.dumps(result, indent=2))


