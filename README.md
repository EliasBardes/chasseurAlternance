
Agent d'Automatisation de Recherche d'Alternance - Elias Bardes

Ce script automatise la recherche d'alternance en Data Analysis. Il récupère les offres récentes sur LinkedIn et Welcome to the Jungle, les analyse via une IA (GPT-4) pour évaluer leur pertinence par rapport au profil d'Elias (HETIC, Python, Design) et génère des mails de candidature personnalisés.

Fonctionnalités

•
Scraping Multi-sources : Récupère les offres "Data Analyst" en alternance/stage.

•
Analyse Intelligente : Utilise un LLM pour extraire les compétences, le contact et noter l'offre (1-10).

•
Candidature Personnalisée : Génère un mail mettant en avant la formation à l'HETIC et le prix "Best Design".

•
Export CSV : Sauvegarde tout dans opportunites.csv.

Installation

1.
Installez Python 3.10+.

2.
Installez les dépendances :

Bash


pip install playwright openai
playwright install chromium





3.
Configurez votre clé API OpenAI dans les variables d'environnement :

Bash


export OPENAI_API_KEY='votre_cle_ici'





Utilisation

Lancez simplement le script principal :

Bash


python main.py



Structure du Code

•
main.py : Orchestrateur du pipeline.

•
scraper.py : Logique de scraping avec Playwright.

•
llm_processor.py : Interaction avec l'API OpenAI pour l'analyse et la rédaction.

•
opportunites.csv : Fichier de sortie contenant les résultats.

Gestion des erreurs

Le script inclut des blocs try-except pour gérer les timeouts de page ou les erreurs d'API. Si un site bloque le scraping, le script passera à l'offre suivante ou à la source suivante.
