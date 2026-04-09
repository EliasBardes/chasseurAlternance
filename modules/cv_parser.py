import re
import pdfplumber

JOB_TITLES = [
    "developpeur full.?stack", "developpeur front.?end", "developpeur back.?end",
    "developpeur web", "developpeur mobile", "developpeur logiciel",
    "developpeur python", "developpeur java", "developpeur javascript",
    "ingenieur logiciel", "ingenieur devops", "ingenieur donnees",
    "ingenieur cloud", "ingenieur systeme", "ingenieur reseau",
    "data scientist", "data analyst", "data engineer",
    "chef de projet", "chef de projet digital", "chef de projet web",
    "product owner", "product manager", "scrum master",
    "designer ux", "designer ui", "ux.?ui designer",
    "graphiste", "directeur artistique", "webdesigner",
    "community manager", "social media manager",
    "charge de communication", "responsable communication",
    "charge de marketing", "responsable marketing",
    "chef de produit", "traffic manager", "seo manager",
    "assistant rh", "charge de recrutement", "responsable rh",
    "assistant administratif", "assistant de direction",
    "charge de formation", "gestionnaire de paie",
    "commercial", "charge d.?affaires", "business developer",
    "account manager", "responsable commercial",
    "consultant", "analyste", "auditeur", "comptable",
    "juriste", "charge de projet", "coordinateur",
]

SKILLS_PATTERNS = [
    "python", "javascript", "typescript", "java", "c\\+\\+", "c#", "php", "ruby",
    "go", "rust", "swift", "kotlin", "scala", "r\\b",
    "react", "angular", "vue\\.?js", "next\\.?js", "nuxt", "svelte",
    "node\\.?js", "express", "django", "flask", "fastapi", "spring",
    "html", "css", "sass", "tailwind",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
    "git", "ci.?cd", "jenkins", "github actions",
    "figma", "sketch", "adobe", "photoshop", "illustrator",
    "agile", "scrum", "kanban",
    "machine learning", "deep learning", "nlp", "computer vision",
    "power.?bi", "tableau", "excel",
    "seo", "google analytics", "google ads",
    "salesforce", "hubspot", "sap",
]

FILIERES_PATTERNS = [
    r"master\s+[\w\s\-']+",
    r"licence\s+[\w\s\-']+",
    r"bachelor\s+[\w\s\-']+",
    r"bts\s+[\w\s\-']+",
    r"dut\s+[\w\s\-']+",
    r"but\s+[\w\s\-']+",
    r"mba\s+[\w\s\-']+",
    r"diplome\s+d['\s][\w\s\-']+",
    r"ecole\s+[\w\s\-']+",
    r"ingenieur\s+[\w\s\-']+",
    r"informatique",
    r"developpement web",
    r"marketing digital",
    r"communication digitale",
    r"data science",
    r"intelligence artificielle",
    r"cybersecurite",
    r"design graphique",
    r"ux design",
    r"ressources humaines",
    r"commerce international",
    r"gestion de projet",
]


def extract_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def _normalize(text: str) -> str:
    text = text.lower()
    replacements = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a", "ä": "a",
        "î": "i", "ï": "i",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)
    return text


def detect_name(text: str) -> dict:
    lines = text.strip().split("\n")
    for line in lines[:8]:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        match = re.match(r"^([A-ZÀ-Ü][a-zà-ü]+)\s+([A-ZÀ-Ü][A-ZÀ-Üa-zà-ü]+)$", line)
        if match:
            return {"prenom": match.group(1), "nom": match.group(2)}
        match = re.match(r"^([A-ZÀ-Ü]{2,})\s+([A-ZÀ-Ü][a-zà-ü]+)$", line)
        if match:
            return {"prenom": match.group(2), "nom": match.group(1)}
        words = line.split()
        if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words if w):
            if not any(c.isdigit() for c in line) and "@" not in line:
                return {"prenom": words[0], "nom": " ".join(words[1:])}
    return {"prenom": "", "nom": ""}


def detect_filiere(text: str) -> str | None:
    normalized = _normalize(text)
    for pattern in FILIERES_PATTERNS:
        match = re.search(pattern, normalized)
        if match:
            result = match.group(0).strip()[:60].strip()
            return result.title()
    return None


def detect_job_title(text: str) -> str | None:
    normalized = _normalize(text)
    lines = normalized.split("\n")
    header = "\n".join(lines[:15])
    for pattern in JOB_TITLES:
        match = re.search(pattern, header)
        if match:
            return match.group(0).title()
    for pattern in JOB_TITLES:
        match = re.search(pattern, normalized)
        if match:
            return match.group(0).title()
    return None


def detect_skills(text: str) -> list[str]:
    normalized = _normalize(text)
    found = []
    for pattern in SKILLS_PATTERNS:
        if re.search(r"\b" + pattern + r"\b", normalized):
            match = re.search(r"\b" + pattern + r"\b", normalized)
            skill = match.group(0).strip()
            skill_display = skill.upper() if len(skill) <= 4 else skill.title()
            if skill_display not in found:
                found.append(skill_display)
    return found


def parse_cv(pdf_path: str) -> dict:
    text = extract_text(pdf_path)
    if not text.strip():
        return {"error": "Impossible d'extraire du texte de ce PDF."}

    name_info = detect_name(text)
    job_title = detect_job_title(text)
    filiere = detect_filiere(text)
    skills = detect_skills(text)

    return {
        "raw_text": text,
        "prenom": name_info["prenom"],
        "nom": name_info["nom"],
        "filiere": filiere,
        "job_title": job_title,
        "skills": skills,
    }
