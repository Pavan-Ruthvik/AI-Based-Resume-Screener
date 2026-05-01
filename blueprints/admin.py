from flask import Blueprint, render_template, flash
from blueprints.auth import login_required
import json
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required(roles=['admin'])
def dashboard():
    if not os.path.exists('models/model_metrics.json'):
        flash('Models not trained yet. Run train_model.py', 'danger')
        return render_template('admin/dashboard.html', metrics=None)
        
    with open('models/model_metrics.json', 'r') as f:
        metrics = json.load(f)
    return render_template('admin/dashboard.html', metrics=metrics)