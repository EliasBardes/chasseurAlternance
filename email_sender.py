import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

APP_URL = "http://localhost:8501"

def send_daily_link(top10: list, to_email: str):
    from_email = os.environ["GMAIL_USER"]
    password   = os.environ["GMAIL_APP_PASSWORD"]
    today      = date.today().strftime("%d/%m/%Y")

    # Résumé des 10 meilleures offres pour l'aperçu dans l'email
    rows = ""
    for i, j in enumerate(top10, 1):
        score      = j.get("final_score", 0)
        hire       = j.get("hire_probability", "?")
        posted     = j.get("posted_date", "")
        insight    = j.get("company_insight", "")
        color      = "#22c55e" if score >= 7 else "#eab308" if score >= 5 else "#ef4444"

        rows += f"""
        <tr style="border-bottom:1px solid #1e293b;">
          <td style="padding:10px 8px;color:#64748b;font-size:13px;font-weight:600;">{i}</td>
          <td style="padding:10px 8px;">
            <div style="font-weight:600;color:#e2e8f0;font-size:14px;">{j.get('title','')}</div>
            <div style="color:#60a5fa;font-size:12px;margin-top:2px;">{j.get('company','')}</div>
            <div style="color:#475569;font-size:11px;margin-top:3px;font-style:italic;">{insight[:80]}{'…' if len(insight)>80 else ''}</div>
          </td>
          <td style="padding:10px 8px;text-align:center;">
            <span style="background:#1e293b;color:#94a3b8;padding:2px 7px;border-radius:4px;font-size:11px;">{posted}</span>
          </td>
          <td style="padding:10px 8px;text-align:center;">
            <span style="background:{color}22;color:{color};padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;">{score}/10</span>
          </td>
          <td style="padding:10px 8px;text-align:center;color:#a78bfa;font-weight:600;font-size:13px;">{hire}/10</td>
          <td style="padding:10px 8px;">
            <span style="background:#1e3a5f;color:#93c5fd;padding:2px 7px;border-radius:4px;font-size:11px;">{j.get('source','')}</span>
          </td>
        </tr>"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#0f172a;font-family:Inter,Arial,sans-serif;">
      <div style="max-width:800px;margin:0 auto;padding:32px 16px;">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#1e3a5f 0%,#1e1b4b 100%);border-radius:16px;padding:32px;margin-bottom:24px;position:relative;overflow:hidden;">
          <div style="font-size:24px;font-weight:700;color:white;font-family:'Space Grotesk',Arial,sans-serif;">⚡ Chasseur d'Alternance</div>
          <div style="color:#94a3b8;font-size:13px;margin-top:6px;">Rapport du {today} · {len(top10)} offres sélectionnées par l'IA</div>
          <div style="margin-top:20px;">
            <a href="{APP_URL}" style="display:inline-block;background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;padding:12px 28px;border-radius:10px;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:0.02em;">
              🚀 Ouvrir le dashboard →
            </a>
          </div>
          <div style="margin-top:10px;color:#475569;font-size:11px;">Emails personnalisés, scores, offres complètes — tout est sur l'app</div>
        </div>

        <!-- Table aperçu -->
        <div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;overflow:hidden;margin-bottom:24px;">
          <div style="padding:16px 20px;border-bottom:1px solid #1e293b;">
            <span style="color:#e2e8f0;font-weight:600;font-size:15px;">Top 10 du jour</span>
            <span style="color:#475569;font-size:12px;margin-left:8px;">trié par score IA (récence + pertinence + probabilité)</span>
          </div>
          <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
            <thead>
              <tr style="background:#1e293b;">
                <th style="padding:10px 8px;color:#475569;font-size:11px;text-align:left;">#</th>
                <th style="padding:10px 8px;color:#475569;font-size:11px;text-align:left;">Poste · Entreprise</th>
                <th style="padding:10px 8px;color:#475569;font-size:11px;text-align:center;">Publié</th>
                <th style="padding:10px 8px;color:#475569;font-size:11px;text-align:center;">Score</th>
                <th style="padding:10px 8px;color:#475569;font-size:11px;text-align:center;">Proba embauche</th>
                <th style="padding:10px 8px;color:#475569;font-size:11px;text-align:left;">Source</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>

        <!-- CTA -->
        <div style="text-align:center;padding:20px;background:#0f172a;border:1px solid #1e293b;border-radius:12px;">
          <div style="color:#94a3b8;font-size:13px;margin-bottom:12px;">Pour voir les emails personnalisés et les détails complets :</div>
          <a href="{APP_URL}" style="display:inline-block;background:#1e293b;color:#60a5fa;padding:10px 24px;border-radius:8px;font-size:13px;text-decoration:none;border:1px solid #334155;">
            {APP_URL}
          </a>
        </div>

        <div style="text-align:center;color:#334155;font-size:11px;margin-top:20px;">
          Pipeline IA automatique · Elias Bardes @ HETIC · {today}
        </div>
      </div>
    </body>
    </html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚡ {len(top10)} offres alternance Data — {today}"
    msg["From"]    = from_email
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

    print(f"Email envoyé à {to_email}")
