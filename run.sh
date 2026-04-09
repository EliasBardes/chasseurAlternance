#!/bin/bash
# Lance le pipeline puis ouvre le dashboard Streamlit

set -a
source /Users/elias/PROJETS/code/Chasseur_Alternance/.env
set +a

cd /Users/elias/PROJETS/code/Chasseur_Alternance

PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
STREAMLIT=/Library/Frameworks/Python.framework/Versions/3.14/bin/streamlit

echo "🔍 Scraping + analyse en cours..."
$PYTHON daily.py

echo "🌐 Lancement du dashboard..."

# Tuer l'instance Streamlit existante si elle tourne
pkill -f "streamlit run app.py" 2>/dev/null
sleep 1

# Lancer Streamlit en arrière-plan
$STREAMLIT run app.py --server.headless true --server.port 8501 >> daily.log 2>&1 &

sleep 2

# Ouvrir le navigateur
open http://localhost:8501
