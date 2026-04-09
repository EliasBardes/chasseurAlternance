FROM python:3.12-slim-bookworm

# dumb-init pour gerer PID 1 (Render ne supporte pas --init)
RUN apt-get update && apt-get install -y --no-install-recommends \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installe Chromium + toutes ses deps systeme automatiquement
RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8501

ENTRYPOINT ["dumb-init", "--"]
CMD ["sh", "-c", "python daily.py && streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0"]
