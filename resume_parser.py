import spacy
import PyPDF2
import docx
import re

nlp = spacy.load("en_core_web_sm")

def load_skills():
    with open("skills.txt", "r") as f:
        skills = [line.strip().lower() for line in f if line.strip()]
    return skills

SKILL_DB = load_skills()


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).lower()

def extract_skills(text):
    lines = text.lower().split("\n")

    skills_lines = []
    capture = False

    for line in lines:
        if "skills" in line:
            capture = True
            continue

        # stop when next section starts
        if capture and any(word in line for word in ["experience", "education", "project", "profile"]):
            break

        if capture:
            skills_lines.append(line)

    skills_text = " ".join(skills_lines)

    found_skills = []
    for skill in SKILL_DB:
        if skill in skills_text:
            found_skills.append(skill)

    return list(set(found_skills))

def extract_experience(text):
    text = text.lower()
    matches = re.findall(r'(\d+)\s*\+?\s*(years|yrs)', text)

    if matches:
        years = [int(m[0]) for m in matches]
        return max(years)
    return 0


