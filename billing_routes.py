from flask import Blueprint, render_template, session, redirect, url_for, flash

billing_routes = Blueprint('billing_routes', __name__)

@billing_routes.route('/dashboard/billing', methods=['GET', 'POST'])
def billing_dashboard():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    return render_template('Billing/billdash.html')
