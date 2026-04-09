# Chasseur d'Alternance

Application web de recherche d'alternance automatisee - Elias Bardes @ HETIC

## Fonctionnalites

- **Import CV** : Upload ton CV en PDF, extraction automatique du nom, filiere, competences et profil
- **Recherche multi-sources** : Scraping sur LinkedIn, Indeed et HelloWork avec filtres (contrat, ville, rayon)
- **Dashboard IA** : Pipeline automatique avec analyse LLM (Groq), scoring de pertinence, probabilite d'embauche et emails personnalises
- **Lettre de motivation** : Generation automatique adaptee a chaque offre
- **Base de donnees** : Stockage SQLite des offres pour suivi dans le temps

## Stack technique

- **Frontend** : Streamlit
- **Scraping** : requests + BeautifulSoup
- **LLM** : Groq (Llama 3.1)
- **CV parsing** : pdfplumber
- **Deploiement** : Docker sur Render

## Structure

```
app.py                  # Application Streamlit (2 onglets)
daily.py                # Pipeline quotidien automatique
scraper.py              # Scraper pour le pipeline automatique
company_researcher.py   # Recherche web sur les entreprises
llm_processor.py        # Analyse LLM des offres
email_sender.py         # Envoi d'email quotidien
modules/
  cv_parser.py          # Extraction d'infos du CV
  scraper.py            # Scraper pour la recherche interactive
  cover_letter.py       # Generation de lettres de motivation
  database.py           # Base SQLite
```

## Installation locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Variables d'environnement

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Cle API Groq |
| `GMAIL_USER` | Email Gmail pour l'envoi |
| `GMAIL_APP_PASSWORD` | Mot de passe app Gmail |
| `RECIPIENT_EMAIL` | Email destinataire du rapport |
