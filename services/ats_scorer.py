import joblib
import os
from services.nlp_engine import extract_keywords, extract_skills
from train_model import clean_text

try:
    model = joblib.load('models/svm_model.pkl')
    vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    le = joblib.load('models/label_encoder.pkl')
except FileNotFoundError:
    model, vectorizer, le = None, None, None

def score_resume(text, job_description=None):
    if not model:
        raise RuntimeError("Models not found. Please run train_model.py first.")

    cleaned = clean_text(text)
    vec_text = vectorizer.transform([cleaned])
    
    probs = model.predict_proba(vec_text)[0]
    top_3_idx = probs.argsort()[-3:][::-1]
    top_matches = [{"category": le.classes_[i], "score": round(probs[i]*100, 1)} for i in top_3_idx]
    
    pred_cat = top_matches[0]['category']
    confidence = probs[top_3_idx[0]]
    
    skills_data = extract_skills(text, job_description)
    matched_skills = skills_data['matched_skills']
    all_resume_skills = skills_data['all_resume_skills']
    
    keywords = extract_keywords(text)
    kw_count = len(keywords)
    word_count = len(cleaned.split())
    
    # Calculate Score
    if job_description and skills_data['jd_skills']:
        skill_score = (len(matched_skills) / len(skills_data['jd_skills'])) * 40
    else:
        skill_score = min(len(all_resume_skills) / 15, 1) * 40
        
    conf_score = confidence * 30
    kw_score = min(kw_count / 30, 1) * 20
    len_score = min(word_count / 300, 1) * 10
    ats_score = int(skill_score + conf_score + kw_score + len_score)
    
    missing = [s for s in skills_data['jd_skills'] if s not in matched_skills] if job_description else []
    
    recs = []
    if missing: recs.append(f"Add missing JD skills: {', '.join(missing[:3])}")
    if kw_count < 20: recs.append("Increase keyword density with industry-specific nouns.")
    if word_count < 200: recs.append("Your resume is quite short. Add more detail to your experiences.")
    if not recs: recs.append("Great resume! Keep tailoring it to specific roles.")

    return {
        "ats_score": ats_score,
        "predicted_category": pred_cat,
        "confidence": confidence,
        "matched_skills": matched_skills,
        "all_skills": all_resume_skills,
        "missing_skills": missing,
        "keyword_count": kw_count,
        "recommendations": recs,
        "top_job_matches": top_matches
    }

def score_batch(resumes_list, job_description=None):
    results = []
    for res in resumes_list:
        if 'error' in res:
            results.append(res)
            continue
        score_data = score_resume(res['text'], job_description)
        results.append({**res, **score_data})
    return sorted([r for r in results if 'ats_score' in r], key=lambda x: x['ats_score'], reverse=True)