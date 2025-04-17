from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
import bcrypt

billing_routes = Blueprint('billing_routes', __name__)

@billing_routes.route('/dashboard/billing', methods=['GET', 'POST'])
def billing_dashboard():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    return render_template('Billing/billdash.html')

@billing_routes.route('/dashboard/billing/update_credentials', methods=['POST'])
def update_billing_credentials():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    user_id = session.get('user_id')  # This corresponds to the `id` in the `users` table
    new_username = request.form.get('username')
    new_password = request.form.get('password')

    try:
        cur = current_app.config['mysql'].connection.cursor()
        if new_username:
            cur.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
        current_app.config['mysql'].connection.commit()
        cur.close()
        flash('Credentials updated successfully.')
    except Exception as e:
        flash('An error occurred while updating credentials.')
        print(f"Error: {e}")

    return redirect(url_for('billing_routes.billing_dashboard'))
