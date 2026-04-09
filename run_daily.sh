#!/bin/bash
# Script lancé par cron chaque matin à 7h
set -a
source /Users/elias/PROJETS/code/Chasseur_Alternance/.env
set +a

cd /Users/elias/PROJETS/code/Chasseur_Alternance

PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
STREAMLIT=/Library/Frameworks/Python.framework/Versions/3.14/bin/streamlit

$PYTHON daily.py >> /Users/elias/PROJETS/code/Chasseur_Alternance/daily.log 2>&1

# (Re)démarrer le serveur Streamlit pour avoir les données fraîches
pkill -f "streamlit run app.py" 2>/dev/null
sleep 1
$STREAMLIT run app.py --server.headless true --server.port 8501 >> /Users/elias/PROJETS/code/Chasseur_Alternance/daily.log 2>&1 &
