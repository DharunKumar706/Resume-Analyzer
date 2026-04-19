import re
from typing import Dict, List, Set
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_MODEL = SentenceTransformer(MODEL_NAME)

COMMON_SKILLS = [
    "python", "java", "javascript", "sql", "excel", "power bi", "tableau", "aws", "azure",
    "gcp", "docker", "kubernetes", "linux", "git", "github", "tensorflow", "pytorch",
    "nlp", "machine learning", "deep learning", "computer vision", "data analysis", "data engineering",
    "data science", "business analysis", "project management", "scrum", "agile", "jira",
    "communication", "presentation", "stakeholder management", "problem solving", "cloud", "rest api",
    "api development", "software development", "testing", "automation", "devops", "cybersecurity",
    "sql server", "postgresql", "mongodb", "redis", "spark", "hadoop", "keras", "pandas", "numpy",
    "scikit-learn", "matplotlib", "seaborn", "dashboard", "etl", "apache", "spark", "hive", "airflow",
    "leadership", "teamwork", "adaptability", "time management"
]

SKILL_PATTERN = re.compile(r"[a-zA-Z\d+#\.\-]{2,}(?:\s+[a-zA-Z\d+#\.\-]{2,})*")

def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _extract_skill_matches(text: str, skills: List[str]) -> Set[str]:
    lowered = _normalize_text(text)
    found: Set[str] = set()
    for skill in sorted(skills, key=lambda s: -len(s)):
        if skill in lowered:
            found.add(skill)
    return found


def _extract_relevant_terms(text: str, limit: int = 12) -> List[str]:
    tokens = SKILL_PATTERN.findall(text.lower())
    candidates = [token for token in tokens if len(token) > 3]
    freq = {}
    for token in candidates:
        freq[token] = freq.get(token, 0) + 1
    sorted_tokens = sorted(freq.items(), key=lambda item: (-item[1], len(item[0])),)
    return [token for token, _ in sorted_tokens[:limit]]


def _cosine_score(text_a: str, text_b: str) -> float:
    embeddings = EMBEDDING_MODEL.encode([text_a, text_b], convert_to_tensor=False, normalize_embeddings=True)
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(score)


def _generate_strengths(resume_text: str, matched_skills: Set[str]) -> List[str]:
    strengths = []
    if matched_skills:
        strengths.append(f"Relevant skills identified: {', '.join(sorted(matched_skills))}.")
    if len(resume_text.split()) > 400:
        strengths.append("Resume contains good detail and project context.")
    if "lead" in resume_text.lower() or "managed" in resume_text.lower():
        strengths.append("Leadership and ownership language is present.")
    if not strengths:
        strengths.append("Resume has a clear professional layout and concise sections.")
    return strengths


def _generate_improvement_recommendations(resume_text: str, jd_text: str, missing_skills: Set[str], short_resume: bool, short_jd: bool) -> List[str]:
    recommendations = []
    if short_resume:
        recommendations.append("Expand your resume with measurable project outcomes and achievements.")
    if missing_skills:
        sample = ", ".join(sorted(list(missing_skills))[:5])
        recommendations.append(f"Add or emphasize these missing skills: {sample}.")
    if "python" not in resume_text.lower() and "python" in jd_text.lower():
        recommendations.append("If you have Python experience, mention it clearly in the summary or skills section.")
    if short_jd:
        recommendations.append("Job description is short or vague; ask the recruiter for more details or clarify expected skills.")
    if not recommendations:
        recommendations.append("Consider adding more quantifiable achievements and domain-specific examples.")
    return recommendations

def analyze_resume_description(resume_text: str, jd_text: str) -> Dict[str, object]:
    """Analyze resume + job description content for match score and skill gaps."""
    resume_clean = _normalize_text(resume_text)
    jd_clean = _normalize_text(jd_text)

    if not resume_clean:
        raise ValueError("Resume text is empty.")
    if not jd_clean:
        raise ValueError("Job description text is empty.")

    resume_words = len(resume_clean.split())
    jd_words = len(jd_clean.split())
    short_resume = resume_words < 60
    short_jd = jd_words < 40

    similarity = _cosine_score(resume_clean, jd_clean)
    resume_skills = _extract_skill_matches(resume_clean, COMMON_SKILLS)
    jd_skills = _extract_skill_matches(jd_clean, COMMON_SKILLS)
    matched_skills = resume_skills & jd_skills
    missing_skills = jd_skills - resume_skills

    if jd_skills:
        coverage = len(matched_skills) / max(1, len(jd_skills))
    else:
        coverage = min(1.0, len(_extract_relevant_terms(resume_clean, limit=6)) / 6)

    length_balance = min(1.0, resume_words / max(60, jd_words))
    raw_score = similarity * 0.72 + coverage * 0.18 + length_balance * 0.10
    match_score = round(max(0.0, min(raw_score * 100, 100.0)), 1)

    strengths = _generate_strengths(resume_text, matched_skills)
    improvements = _generate_improvement_recommendations(resume_text, jd_text, missing_skills, short_resume, short_jd)

    analysis = {
        "match_score": match_score,
        "similarity": round(similarity, 3),
        "coverage_ratio": round(coverage, 3),
        "resume_length_words": resume_words,
        "job_description_length_words": jd_words,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "strengths": strengths,
        "improvements": improvements,
        "resume_summary": resume_text[:1200].strip(),
        "job_description_summary": jd_text[:1200].strip(),
        "notes": []
    }

    if short_resume:
        analysis["notes"].append("Resume is very short and may not include enough detail for the role.")
    if short_jd:
        analysis["notes"].append("Job description is very short; scoring relies more on keyword matching than role context.")
    if resume_words > 1800:
        analysis["notes"].append("Resume is very long; consider consolidating older experience and focusing on the most relevant sections.")

    return analysis