from flask import Blueprint, render_template, request, flash
from blueprints.auth import login_required
from services.parser import parse_file
from services.ats_scorer import score_resume

jobseeker_bp = Blueprint('jobseeker', __name__)

@jobseeker_bp.route('/dashboard', methods=['GET'])
@login_required(roles=['jobseeker'])
def dashboard():
    return render_template('jobseeker/dashboard.html')

@jobseeker_bp.route('/upload', methods=['POST'])
@login_required(roles=['jobseeker'])
def upload():
    file = request.files.get('resume')
    jd = request.form.get('job_description', '')
    
    if file and file.filename:
        parsed = parse_file(file, file.filename)
        if 'error' in parsed:
            flash(parsed['error'], 'danger')
            return render_template('jobseeker/dashboard.html')
            
        try:
            result = score_resume(parsed['text'], jd)
            return render_template('jobseeker/dashboard.html', result=result)
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('jobseeker/dashboard.html')