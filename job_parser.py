from resume_parser import load_skills

SKILL_DB = load_skills()

def extract_job_skills(job_text):
    lines = job_text.lower().split("\n")

    skills_lines = []
    capture = False

    for line in lines:
        if "required skills" in line:
            capture = True
            continue

        if capture and any(word in line for word in ["experience", "good to have"]):
            break

        if capture:
            skills_lines.append(line)

    skills_text = " ".join(skills_lines)

    skills = []
    for skill in SKILL_DB:
        if skill in skills_text:
            skills.append(skill)

    return list(set(skills))

import re

def extract_required_experience(job_text):
    job_text = job_text.lower()
    matches = re.findall(r'(\d+)\s*\+?\s*(years|yrs)', job_text)

    if matches:
        return int(matches[0][0])
    return 0

import PyPDF2

def extract_job_text_from_file(file_path):
    text = ""

    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    elif file_path.endswith(".pdf"):
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""

    return text.lower()




