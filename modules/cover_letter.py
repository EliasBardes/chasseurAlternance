from datetime import date

MOIS = [
    "", "janvier", "fevrier", "mars", "avril", "mai", "juin",
    "juillet", "aout", "septembre", "octobre", "novembre", "decembre",
]


def generate_cover_letter(
    prenom: str,
    nom: str,
    filiere: str,
    skills: list[str],
    job_title: str,
    company: str,
    contract_type: str,
) -> str:
    today = date.today()
    date_str = f"{today.day} {MOIS[today.month]} {today.year}"

    full_name = f"{prenom} {nom}".strip() or "Candidat"
    filiere_text = filiere or "mon domaine d'etudes"
    company = company or "votre entreprise"

    contract_labels = {
        "Alternance": "un contrat en alternance",
        "CDI": "un poste en CDI",
        "CDD": "un poste en CDD",
        "Stage": "un stage",
    }
    contract_text = contract_labels.get(contract_type, "un poste")

    letter = f"""# Lettre de motivation

**{full_name}**

*Date : {date_str}*

---

**Objet :** Candidature pour le poste de **{job_title}** — {contract_type}

---

Madame, Monsieur,

Actuellement en formation en **{filiere_text}**, je me permets de vous adresser ma candidature pour {contract_text} en tant que **{job_title}** au sein de **{company}**.

Votre offre a retenu toute mon attention car elle correspond parfaitement a mon projet professionnel et aux competences que je developpe au cours de ma formation. Je suis convaincu(e) que **{company}** represente un environnement stimulant ou je pourrai mettre en pratique mes connaissances tout en continuant a progresser.

Au fil de mon parcours, j'ai acquis des competences solides en :

{chr(10).join('- ' + s for s in (skills[:5] if skills else ['mes competences techniques']))}

Ces experiences m'ont permis de developper une approche rigoureuse et une capacite d'adaptation qui, je le crois, seraient des atouts pour votre equipe.

Je serais ravi(e) de pouvoir echanger avec vous sur ma candidature et sur la maniere dont je pourrais contribuer aux projets de **{company}**. Je reste a votre entiere disposition pour un entretien a votre convenance.

Dans l'attente de votre retour, je vous prie d'agreer, Madame, Monsieur, l'expression de mes salutations distinguees.

**{full_name}**"""

    return letter
