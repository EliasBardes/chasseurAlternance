import streamlit as st
import pandas as pd
import ast

st.set_page_config(page_title="Chasseur d'Alternance", page_icon="⚡", layout="wide")

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
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content:''; position:absolute; top:-60px; right:-60px;
    width:200px; height:200px;
    background:radial-gradient(circle, rgba(99,179,237,0.12) 0%, transparent 70%);
    border-radius:50%;
  }
  .hero-title {
    font-family:'Space Grotesk',sans-serif;
    font-size:2rem; font-weight:700;
    background:linear-gradient(90deg,#63B3ED,#9F7AEA,#63B3ED);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-size:200% auto;
    animation:shine 4s linear infinite;
  }
  @keyframes shine { to { background-position:200% center; } }
  .hero-sub { color:#718096; font-size:0.9rem; margin-top:0.3rem; font-weight:300; }

  .metric-card {
    background:rgba(15,31,61,0.6);
    border:1px solid rgba(99,179,237,0.12);
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

  .badge {
    display:inline-block; padding:0.2rem 0.7rem; border-radius:999px;
    font-size:0.78rem; font-weight:600; font-family:'Space Grotesk',sans-serif;
  }
  .badge-green { background:rgba(72,187,120,0.15); color:#68D391; border:1px solid rgba(72,187,120,0.3); }
  .badge-yellow { background:rgba(236,201,75,0.12); color:#ECC94B; border:1px solid rgba(236,201,75,0.25); }
  .badge-red { background:rgba(252,129,74,0.12); color:#FC8181; border:1px solid rgba(252,129,74,0.25); }
  .badge-purple { background:rgba(159,122,234,0.12); color:#B794F4; border:1px solid rgba(159,122,234,0.25); }
  .badge-blue { background:rgba(99,179,237,0.1); border:1px solid rgba(99,179,237,0.2); color:#90CDF4; }

  .tag {
    display:inline-block; background:rgba(99,179,237,0.08);
    border:1px solid rgba(99,179,237,0.18); border-radius:6px;
    padding:0.15rem 0.6rem; font-size:0.75rem; color:#90CDF4; margin:0.15rem;
  }
  .label { font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:#4A5568; margin-bottom:0.4rem; margin-top:0.9rem; }
  .insight-box {
    background:rgba(159,122,234,0.06); border:1px solid rgba(159,122,234,0.15);
    border-radius:8px; padding:0.6rem 0.9rem; font-size:0.8rem; color:#B794F4;
    font-style:italic; margin-top:0.5rem;
  }
  .email-box {
    background:rgba(8,11,20,0.7); border:1px solid rgba(99,179,237,0.1);
    border-radius:10px; padding:1rem; font-size:0.82rem; color:#A0AEC0;
    line-height:1.65; white-space:pre-wrap; max-height:220px; overflow-y:auto;
  }
  .score-row { display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap; margin-top:0.4rem; }
  .divider { border:none; border-top:1px solid rgba(99,179,237,0.07); margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- Données ---
df = pd.read_csv("opportunites.csv")
df = df[df["title"] != "N/A"].dropna(subset=["title"])
sort_col = "final_score" if "final_score" in df.columns else "relevance_score"
df = df.sort_values(sort_col, ascending=False).reset_index(drop=True)

def parse_email(raw):
    raw = str(raw)
    if raw.startswith("{"):
        try:
            data = ast.literal_eval(raw)
            for k in ["corps", "contenu", " contenu", "body", "personalized_email"]:
                if k in data: return str(data[k])
        except Exception:
            pass
    return raw

def badge(val, label, cls="badge-blue"):
    return f'<span class="badge {cls}">{label} {val}</span>'

# --- Hero ---
today = df["posted_date"].max() if "posted_date" in df.columns else ""
st.markdown(f"""
<div class="hero">
  <div class="hero-title">⚡ Chasseur d'Alternance</div>
  <div class="hero-sub">Pipeline IA · Scraping multi-sources + Analyse LLM · Elias Bardes @ HETIC · Dernière mise à jour : {today}</div>
</div>
""", unsafe_allow_html=True)

# --- Métriques ---
cols = st.columns(5)
avg_score = df[sort_col].mean()
top_hire = df["hire_probability"].mean() if "hire_probability" in df.columns else 0
fresh = df[df["posted_date"] >= df["posted_date"].max()].shape[0] if "posted_date" in df.columns else 0
for col, val, label in zip(cols,
    [len(df), f"{avg_score:.1f}/10", f"{top_hire:.1f}/10", fresh, df["source"].nunique()],
    ["Offres analysées", "Score moyen", "Proba embauche moy.", "Nouvelles aujourd'hui", "Sources"]
):
    col.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# --- Offres ---
for _, row in df.iterrows():
    final  = row.get("final_score", row.get("relevance_score", 0))
    relev  = row.get("relevance_score", 0)
    hire   = row.get("hire_probability", "?")
    bonus  = row.get("recency_bonus", 0)
    posted = row.get("posted_date", "")
    insight = str(row.get("company_insight", ""))
    alt_score = row.get("alternant_data_score", 0)

    fc = float(final)
    badge_cls = "badge-green" if fc >= 7 else "badge-yellow" if fc >= 5 else "badge-red"

    skills_html = "".join(
        f'<span class="tag">{s.strip()}</span>'
        for s in str(row.get("key_skills", "")).split(",")
        if s.strip() and s.strip() != "nan"
    )

    email_text = parse_email(row.get("personalized_email", ""))

    has_link = pd.notna(row.get("link")) and str(row.get("link", "")).startswith("http")
    link_url = row["link"] if has_link else "#"

    title_html = (
        f'<a href="{link_url}" target="_blank" style="text-decoration:none;">'
        f'<div class="job-title" style="cursor:pointer;">{row["title"]} <span style="font-size:0.75rem;color:#4A5568;">↗</span></div></a>'
        if has_link else f'<div class="job-title">{row["title"]}</div>'
    )

    link_btn_top = (
        f'<a href="{link_url}" target="_blank" style="display:inline-flex;align-items:center;gap:6px;background:linear-gradient(135deg,#1d4ed8,#6d28d9);color:white;padding:7px 16px;border-radius:8px;font-size:0.8rem;font-weight:600;text-decoration:none;white-space:nowrap;">Voir l\'offre ↗</a>'
        if has_link else ""
    )

    insight_html = f'<div class="insight-box">🔍 {insight}</div>' if insight and insight != "nan" else ""

    st.markdown(f"""
    <div class="job-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.7rem;">
        <div style="flex:1;min-width:0;">
          {title_html}
          <div class="job-company">{row['company']}</div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.5rem;flex-shrink:0;">
          {link_btn_top}
          <div class="score-row" style="justify-content:flex-end;">
            <span class="badge {badge_cls}">Score {final}/10</span>
            <span class="badge badge-purple">Embauche {hire}/10</span>
            <span class="badge badge-blue">{row.get('source','')}</span>
            {'<span class="badge badge-green">🔥 Récent</span>' if bonus and float(bonus) >= 2 else ''}
            <span style="color:#4A5568;font-size:0.75rem;">Publié {posted}</span>
          </div>
        </div>
      </div>

      {insight_html}

      <div class="label">Compétences clés</div>
      <div>{skills_html or '<span style="color:#4A5568;font-size:0.8rem">N/A</span>'}</div>

      <div style="display:flex;gap:2rem;margin-top:0.8rem;flex-wrap:wrap;">
        <div>
          <div class="label">Pertinence profil</div>
          <span style="color:#63B3ED;font-weight:600;">{relev}/10</span>
        </div>
        <div>
          <div class="label">Alternants data (web)</div>
          <span style="color:#B794F4;font-weight:600;">{int(alt_score) if alt_score == alt_score else 0}/20</span>
        </div>
        <div>
          <div class="label">Contact</div>
          <span style="color:#718096;font-size:0.82rem;">{row.get('contact','N/A')}</span>
        </div>
      </div>

      <div class="label">Email personnalisé</div>
      <div class="email-box">{email_text}</div>
    </div>
    """, unsafe_allow_html=True)
