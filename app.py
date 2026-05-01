from flask import Flask, redirect, url_for, render_template
from datetime import timedelta
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.recruiter import recruiter_bp
from blueprints.jobseeker import jobseeker_bp
from services.db import init_db, seed_admin

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-dev'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.permanent_session_lifetime = timedelta(hours=2)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
app.register_blueprint(jobseeker_bp, url_prefix='/jobseeker')

@app.route('/')
def index():
    # Show the shiny new landing page instead of forcing a login redirect!
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    seed_admin()
    app.run(debug=True)