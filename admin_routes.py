from flask import Blueprint, render_template, session, redirect, url_for, flash

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/dashboard', methods=['GET'])
def admin_dashboard():
    """Render the admin dashboard."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))
    return render_template('Admin/dashboard.html')

@admin_routes.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    """Admin functionality to manage users."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))
    # Add logic to fetch and manage users
    return render_template('Admin/manage_users.html')

@admin_routes.route('/view_reports', methods=['GET'])
def view_reports():
    """Admin functionality to view reports."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))
    # Add logic to fetch and display reports
    return render_template('Admin/view_reports.html')
