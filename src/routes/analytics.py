# src/routes/analytics.py

from flask import Blueprint, render_template

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/analytics')
def analytics_home():
    """
    A single page with links/buttons to each advanced query report.
    """
    return render_template('analytics_home.html')
