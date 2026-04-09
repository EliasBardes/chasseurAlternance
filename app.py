import streamlit as st
import pandas as pd
import ast
import html as html_lib
import os
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

  .job-card {
    background:rgba(13,22,38,0.8); border:1px solid rgba(99,179,237,0.1);
    border-radius:14px; padding:1.5rem; margin-bottom:1rem;
    transition:border-color 0.2s, box-shadow 0.2s; backdrop-filter:blur(8px);
  }
  .job-card:hover { border-color:rgba(99,179,237,0.35); box-shadow:0 0 24px rgba(99,179,237,0.07); }
  .job-title { font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:600; color:#E2E8F0; }
  .job-company { font-size:0.85rem; color:#63B3ED; font-weight:500; }
  .badge { display:inline-block; padding:0.2rem 0.7rem; border-radius:999px; font-size:0.78rem; font-weight:600; font-family:'Space Grotesk',sans-serif; }
  .badge-green { background:rgba(72,187,120,0.15); color:#68D391; border:1px solid rgba(72,187,120,0.3); }
  .badge-yellow { background:rgba(236,201,75,0.12); color:#ECC94B; border:1px solid rgba(236,201,75,0.25); }
  .badge-red { background:rgba(252,129,74,0.12); color:#FC8181; border:1px solid rgba(252,129,74,0.25); }
  .badge-purple { background:rgba(159,122,234,0.12); color:#B794F4; border:1px solid rgba(159,122,234,0.25); }
  .badge-blue { background:rgba(99,179,237,0.1); border:1px solid rgba(99,179,237,0.2); color:#90CDF4; }
  .tag { display:inline-block; background:rgba(99,179,237,0.08); border:1px solid rgba(99,179,237,0.18); border-radius:6px; padding:0.15rem 0.6rem; font-size:0.75rem; color:#90CDF4; margin:0.15rem; }
  .label { font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:#4A5568; margin-bottom:0.4rem; margin-top:0.9rem; }
  .insight-box { background:rgba(159,122,234,0.06); border:1px solid rgba(159,122,234,0.15); border-radius:8px; padding:0.6rem 0.9rem; font-size:0.8rem; color:#B794F4; font-style:italic; margin-top:0.5rem; }
  .email-box { background:rgba(8,11,20,0.7); border:1px solid rgba(99,179,237,0.1); border-radius:10px; padding:1rem; font-size:0.82rem; color:#A0AEC0; line-height:1.65; white-space:pre-wrap; max-height:220px; overflow-y:auto; }
  .score-row { display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap; margin-top:0.4rem; }
  .divider { border:none; border-top:1px solid rgba(99,179,237,0.07); margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)


def safe(val, default=""):
    if pd.isna(val):
        return default
    return html_lib.escape(str(val).strip())


def safe_float(val, default=0):
    try:
        v = float(val)
        return default if pd.isna(v) else v
    except (ValueError, TypeError):
        return default


def parse_email(raw):
    raw = str(raw)
    if raw in ("nan", "None", ""):
        return ""
    if raw.startswith("{"):
        try:
            data = ast.literal_eval(raw)
            for k in ["corps", "contenu", " contenu", "body", "personalized_email"]:
                if k in data:
                    return str(data[k])
        except Exception:
            pass
    return raw


# --- Hero ---
st.markdown("""
<div class="hero">
  <div class="hero-title">Chasseur d'Alternance</div>
  <div class="hero-sub">Pipeline IA - Scraping multi-sources + Analyse LLM + Import CV - Elias Bardes @ HETIC</div>
</div>
""", unsafe_allow_html=True)

# === ONGLETS ===
tab_dashboard, tab_search = st.tabs(["Dashboard IA", "Recherche + CV"])

# ==========================================
# ONGLET 1 : Dashboard pipeline automatique
# ==========================================
with tab_dashboard:
    csv_path = "opportunites.csv"
    if not os.path.exists(csv_path):
        st.info("Le pipeline est en cours... Rechargez la page dans quelques minutes.")
    else:
        df = pd.read_csv(csv_path)
        df = df[df["title"] != "N/A"].dropna(subset=["title"])
        sort_col = "final_score" if "final_score" in df.columns else "relevance_score"
        df = df.sort_values(sort_col, ascending=False).reset_index(drop=True)

        # Metriques
        cols = st.columns(5)
        avg_score = df[sort_col].mean()
        top_hire = df["hire_probability"].mean() if "hire_probability" in df.columns else 0
        fresh = df[df["posted_date"] >= df["posted_date"].max()].shape[0] if "posted_date" in df.columns else 0
        for col, val, label in zip(cols,
            [len(df), f"{avg_score:.1f}/10", f"{top_hire:.1f}/10", fresh, df["source"].nunique()],
            ["Offres analysees", "Score moyen", "Proba embauche moy.", "Nouvelles aujourd'hui", "Sources"]
        ):
            col.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Offres
        for _, row in df.iterrows():
            final = safe_float(row.get("final_score", row.get("relevance_score", 0)))
            relev = safe_float(row.get("relevance_score", 0))
            hire = safe_float(row.get("hire_probability", 0))
            bonus = safe_float(row.get("recency_bonus", 0))
            posted = safe(row.get("posted_date", ""))
            insight = safe(row.get("company_insight", ""))
            alt_score = safe_float(row.get("alternant_data_score", 0))

            badge_cls = "badge-green" if final >= 7 else "badge-yellow" if final >= 5 else "badge-red"

            skills_raw = str(row.get("key_skills", ""))
            skills_html = "".join(
                f'<span class="tag">{html_lib.escape(s.strip())}</span>'
                for s in skills_raw.split(",") if s.strip() and s.strip() != "nan"
            )

            email_text = html_lib.escape(parse_email(row.get("personalized_email", "")))

            link = str(row.get("link", ""))
            has_link = link.startswith("http")
            title_safe = safe(row.get("title", ""))
            company_safe = safe(row.get("company", ""))
            contact_safe = safe(row.get("contact", "N/A"), "N/A")
            source_safe = safe(row.get("source", ""))

            title_html = (
                f'<a href="{link}" target="_blank" style="text-decoration:none;">'
                f'<div class="job-title" style="cursor:pointer;">{title_safe} &#8599;</div></a>'
                if has_link else f'<div class="job-title">{title_safe}</div>'
            )
            link_btn = (
                f'<a href="{link}" target="_blank" style="display:inline-flex;align-items:center;gap:6px;background:linear-gradient(135deg,#1d4ed8,#6d28d9);color:white;padding:7px 16px;border-radius:8px;font-size:0.8rem;font-weight:600;text-decoration:none;">Voir l\'offre &#8599;</a>'
                if has_link else ""
            )
            insight_html = f'<div class="insight-box">{insight}</div>' if insight else ""
            recent_badge = '<span class="badge badge-green">Recent</span>' if bonus >= 2 else ''

            st.markdown(f"""
            <div class="job-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.7rem;">
                <div style="flex:1;min-width:0;">
                  {title_html}
                  <div class="job-company">{company_safe}</div>
                </div>
                <div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.5rem;flex-shrink:0;">
                  {link_btn}
                  <div class="score-row" style="justify-content:flex-end;">
                    <span class="badge {badge_cls}">Score {final}/10</span>
                    <span class="badge badge-purple">Embauche {hire}/10</span>
                    <span class="badge badge-blue">{source_safe}</span>
                    {recent_badge}
                    <span style="color:#4A5568;font-size:0.75rem;">Publie {posted}</span>
                  </div>
                </div>
              </div>
              {insight_html}
              <div class="label">Competences cles</div>
              <div>{skills_html or '<span style="color:#4A5568;font-size:0.8rem">N/A</span>'}</div>
              <div style="display:flex;gap:2rem;margin-top:0.8rem;flex-wrap:wrap;">
                <div><div class="label">Pertinence profil</div><span style="color:#63B3ED;font-weight:600;">{relev}/10</span></div>
                <div><div class="label">Alternants data (web)</div><span style="color:#B794F4;font-weight:600;">{int(alt_score)}/20</span></div>
                <div><div class="label">Contact</div><span style="color:#718096;font-size:0.82rem;">{contact_safe}</span></div>
              </div>
              <div class="label">Email personnalise</div>
              <div class="email-box">{email_text}</div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# ONGLET 2 : Recherche interactive + CV
# ==========================================
with tab_search:
    st.markdown("### Recherche personnalisee")

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

    # Bouton recherche
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

    # Liste des offres de la DB
    jobs = get_jobs(
        contract_type=st.session_state.get("contract_type"),
        city=st.session_state.get("city") or None,
    )

    # Stats
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

    # Offres
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
