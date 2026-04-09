import streamlit as st
from pathlib import Path

from modules.database import init_db, get_jobs, insert_jobs
from modules.cv_parser import parse_cv
from modules.scraper import scrape_all
from modules.cover_letter import generate_cover_letter

st.set_page_config(page_title="Chasseur d'Alternance", page_icon="⚡", layout="wide")
init_db()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CONTRACT_TYPES = ["Alternance", "CDI", "CDD", "Stage"]
RADIUS_OPTIONS = {"5 km": 5, "10 km": 10, "20 km": 20, "50 km": 50, "100 km": 100}
VILLES = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Lille",
    "Nantes", "Strasbourg", "Rennes", "Montpellier", "Nice", "Grenoble",
    "Rouen", "Toulon", "Dijon", "Angers", "Reims", "Le Havre",
    "Saint-Etienne", "Brest", "Clermont-Ferrand", "Tours", "Metz",
    "Aix-en-Provence", "Versailles", "Caen",
]

# --- CSS ---
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #080B14;
    color: #E2E8F0;
  }
  .stApp { background: radial-gradient(ellipse at 20% 0%, #0f1f3d 0%, #080B14 60%); }
  h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem; padding-bottom: 2rem; }

  .hero {
    background: linear-gradient(135deg, #0f1f3d 0%, #0d1626 100%);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 16px; padding: 2.5rem 3rem; margin-bottom: 2rem;
    position: relative; overflow: hidden;
  }
  .hero::before {
    content:''; position:absolute; top:-60px; right:-60px;
    width:200px; height:200px;
    background:radial-gradient(circle, rgba(99,179,237,0.12) 0%, transparent 70%);
    border-radius:50%;
  }
  .hero-title {
    font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700;
    background:linear-gradient(90deg,#63B3ED,#9F7AEA,#63B3ED);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-size:200% auto; animation:shine 4s linear infinite;
  }
  @keyframes shine { to { background-position:200% center; } }
  .hero-sub { color:#718096; font-size:0.9rem; margin-top:0.3rem; font-weight:300; }

  .metric-card {
    background:rgba(15,31,61,0.6); border:1px solid rgba(99,179,237,0.12);
    border-radius:12px; padding:1.2rem 1.5rem; text-align:center;
    backdrop-filter:blur(10px);
  }
  .metric-value { font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; color:#63B3ED; }
  .metric-label { font-size:0.75rem; color:#4A5568; text-transform:uppercase; letter-spacing:0.1em; margin-top:0.2rem; }
</style>
""", unsafe_allow_html=True)

# --- Hero ---
st.markdown("""
<div class="hero">
  <div class="hero-title">Chasseur d'Alternance</div>
  <div class="hero-sub">Importe ton CV, lance une recherche et genere des lettres de motivation</div>
</div>
""", unsafe_allow_html=True)

# --- Barre de recherche ---
st.markdown("### Recherche")

col_cv, col_contrat, col_ville, col_rayon = st.columns([3, 1.5, 1.5, 1])

with col_cv:
    uploaded_file = st.file_uploader("Importe ton CV (PDF)", type=["pdf"])
    if uploaded_file:
        save_path = UPLOAD_DIR / uploaded_file.name
        save_path.write_bytes(uploaded_file.getvalue())
        st.session_state["cv_path"] = str(save_path)
        with st.spinner("Analyse du CV..."):
            result = parse_cv(str(save_path))
        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state["cv_data"] = result

with col_contrat:
    contract = st.selectbox("Contrat", CONTRACT_TYPES)
    st.session_state["contract_type"] = contract

with col_ville:
    city = st.selectbox("Ville", ["Toute la France"] + VILLES)
    st.session_state["city"] = "" if city == "Toute la France" else city

with col_rayon:
    radius_label = st.selectbox("Rayon", list(RADIUS_OPTIONS.keys()), index=2)
    st.session_state["radius_km"] = RADIUS_OPTIONS[radius_label]

# Infos CV
if "cv_data" in st.session_state:
    cv = st.session_state["cv_data"]
    chips = []
    if cv["prenom"] or cv["nom"]:
        chips.append(f"**{cv['prenom']} {cv['nom']}**")
    if cv["filiere"]:
        chips.append(f"Filiere : {cv['filiere']}")
    if cv["job_title"]:
        chips.append(f"Profil : {cv['job_title']}")
    if cv["skills"]:
        chips.append(f"Skills : {', '.join(cv['skills'][:8])}")
    if chips:
        st.markdown(" | ".join(chips))

st.divider()

# --- Bouton recherche ---
if st.button("Lancer la recherche", type="primary", use_container_width=True):
    if "cv_data" not in st.session_state:
        st.error("Importe d'abord ton CV.")
    else:
        cv = st.session_state["cv_data"]
        title = cv["job_title"] or cv.get("filiere") or "Developpeur"
        ctype = st.session_state["contract_type"]
        city_val = st.session_state.get("city", "")
        radius = st.session_state.get("radius_km", 20)

        progress_bar = st.progress(0)
        status_text = st.empty()

        def on_progress(site_label, site_index, total_sites, jobs_count):
            pct = site_index / total_sites
            progress_bar.progress(pct, text=f"{site_label} termine - {jobs_count} offre(s) trouvee(s)")

        status_text.info(f"Recherche : **{title}** en **{ctype}** - {city_val or 'France entiere'} ({radius_label})")

        jobs_found = scrape_all(
            job_title=title,
            contract_type=ctype,
            city=city_val,
            radius_km=radius,
            on_progress=on_progress,
        )
        new_count = insert_jobs(jobs_found)
        progress_bar.progress(1.0, text="Termine !")
        status_text.success(f"{len(jobs_found)} offres trouvees, {new_count} nouvelles ajoutees.")

# --- Stats ---
jobs = get_jobs(
    contract_type=st.session_state.get("contract_type"),
    city=st.session_state.get("city") or None,
)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(jobs)}</div><div class="metric-label">Offres totales</div></div>', unsafe_allow_html=True)
with col_s2:
    sources = len(set(j["source"] for j in jobs)) if jobs else 0
    st.markdown(f'<div class="metric-card"><div class="metric-value">{sources}</div><div class="metric-label">Sources</div></div>', unsafe_allow_html=True)
with col_s3:
    companies = len(set(j["company"] for j in jobs)) if jobs else 0
    st.markdown(f'<div class="metric-card"><div class="metric-value">{companies}</div><div class="metric-label">Entreprises</div></div>', unsafe_allow_html=True)

st.markdown("")

# --- Liste des offres ---
if jobs:
    for i, job in enumerate(jobs):
        with st.container():
            col_info, col_actions = st.columns([3, 1])
            with col_info:
                st.markdown(f"#### {job['title']}")
                parts = [f"**{job['company']}**"]
                if job.get("location"):
                    parts.append(job["location"])
                parts.append(f"_{job['source']}_")
                if job.get("date_posted"):
                    parts.append(job["date_posted"])
                st.markdown(" | ".join(parts))

            with col_actions:
                st.link_button("Consulter l'offre", job["url"], use_container_width=True)
                if "cv_data" in st.session_state:
                    if st.button("Generer lettre", key=f"btn_letter_{i}", use_container_width=True):
                        cv = st.session_state["cv_data"]
                        letter = generate_cover_letter(
                            prenom=cv["prenom"], nom=cv["nom"],
                            filiere=cv["filiere"], skills=cv["skills"],
                            job_title=job["title"], company=job["company"],
                            contract_type=st.session_state["contract_type"],
                        )
                        st.session_state[f"letter_{i}"] = letter

            if f"letter_{i}" in st.session_state:
                with st.expander("Lettre de motivation", expanded=True):
                    st.markdown(st.session_state[f"letter_{i}"])
                st.download_button(
                    "Telecharger la lettre (.md)",
                    data=st.session_state[f"letter_{i}"],
                    file_name=f"lettre_{job['company'].replace(' ', '_')}.md",
                    mime="text/markdown", key=f"dl_{i}",
                )
            st.divider()
else:
    st.info("Aucune offre. Importe ton CV et lance une recherche.")
