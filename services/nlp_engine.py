import spacy

nlp = spacy.load("en_core_web_sm")

SKILLS_LIST = {
    'python', 'java', 'javascript', 'c++', 'sql', 'r', 'scala', 'kotlin', 'swift',
    'django', 'flask', 'react', 'angular', 'spring', 'tensorflow', 'pytorch', 'keras',
    'git', 'docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'jira', 'tableau', 'powerbi',
    'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
    'machine learning', 'deep learning', 'nlp', 'data analysis', 'data visualization'
}

def extract_keywords(text):
    doc = nlp(text.lower())
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and len(token.text) > 1]
    return list(set(keywords))[:30]

def extract_skills(text, job_description=None):
    text_lower = text.lower()
    resume_skills = [skill for skill in SKILLS_LIST if skill in text_lower]
    
    if job_description:
        jd_lower = job_description.lower()
        jd_skills = [skill for skill in SKILLS_LIST if skill in jd_lower]
        matched = [s for s in jd_skills if s in resume_skills]
        return {"matched_skills": matched, "all_resume_skills": resume_skills, "jd_skills": jd_skills}
    
    return {"matched_skills": resume_skills, "all_resume_skills": resume_skills, "jd_skills": []}