from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from services.db import verify_login, register_user

auth_bp = Blueprint('auth', __name__)

def login_required(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            if roles and session.get('role') not in roles:
                flash('Permission denied.', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = verify_login(request.form['email'], request.form['password'])
        if user:
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for(f"{user['role']}.dashboard"))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        if role not in ['recruiter', 'jobseeker']:
            flash('Invalid role selection', 'danger')
            return redirect(url_for('auth.register'))
            
        success, msg = register_user(request.form['username'], request.form['email'], request.form['password'], role)
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        flash(msg, 'danger')
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))