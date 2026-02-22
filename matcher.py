from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match(resume_skills, job_skills):
    if not job_skills:
        return 0.0

    matched = set(resume_skills) & set(job_skills)
    score = (len(matched) / len(job_skills)) * 100

    return round(score, 2)

