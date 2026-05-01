from flask import Blueprint, render_template, request, flash
from blueprints.auth import login_required
from services.parser import parse_file
from services.ats_scorer import score_batch

recruiter_bp = Blueprint('recruiter', __name__)

@recruiter_bp.route('/dashboard')
@login_required(roles=['recruiter'])
def dashboard():
    return render_template('recruiter/dashboard.html')

@recruiter_bp.route('/upload', methods=['POST'])
@login_required(roles=['recruiter'])
def upload():
    files = request.files.getlist('resumes')
    jd = request.form.get('job_description', '')
    
    parsed_resumes = []
    for file in files:
        if file.filename:
            res = parse_file(file, file.filename)
            if isinstance(res, list): parsed_resumes.extend(res)
            else: parsed_resumes.append(res)
            
    scored = score_batch(parsed_resumes, jd)
    if not scored:
        flash('No valid resumes processed.', 'warning')
        return render_template('recruiter/dashboard.html')
        
    return render_template('recruiter/results.html', results=scored)