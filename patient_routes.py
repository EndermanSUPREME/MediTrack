from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
import bcrypt

patient_routes = Blueprint('patient_routes', __name__)

@patient_routes.route('/dashboard/patient', methods=['GET', 'POST'])
def patient_dashboard():
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('role_specific_id')  # Use the role-specific ID for patient operations

    if request.method == 'POST':
        # Update patient information
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        try:
            cur = current_app.config['mysql'].connection.cursor()
            cur.execute("""
                UPDATE patient
                SET first_name = %s, last_name = %s, phone = %s, email = %s, address = %s
                WHERE patient_id = %s
            """, (first_name, last_name, phone, email, address, patient_id))
            current_app.config['mysql'].connection.commit()
            cur.close()
            flash('Information updated successfully.')
        except Exception as e:
            flash('An error occurred while updating information.')
            print(f"Error: {e}")

    # Fetch the patient's current information
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("SELECT first_name, last_name, phone, email, address FROM patient WHERE patient_id = %s", (patient_id,))
    patient = cur.fetchone()
    cur.close()

    return render_template('Patient/patdash.html', patient=patient)

@patient_routes.route('/dashboard/patient/update_credentials', methods=['POST'])
def update_patient_credentials():
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    user_id = session.get('user_id')  # This now corresponds to the `id` in the `users` table
    print("User ID (from users table): ", user_id)
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

    return redirect(url_for('patient_routes.patient_dashboard'))
