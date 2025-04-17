from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app

doctor_routes = Blueprint('doctor_routes', __name__)

@doctor_routes.route('/dashboard/doctor', methods=['GET', 'POST'])
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    doctor_id = session.get('user_id')

    if request.method == 'POST':
        # Update doctor information
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        try:
            cur = current_app.config['mysql'].connection.cursor()
            cur.execute("""
                UPDATE doctor
                SET first_name = %s, last_name = %s, phone = %s, email = %s
                WHERE doctor_id = %s
            """, (first_name, last_name, phone, email, doctor_id))
            current_app.config['mysql'].connection.commit()
            cur.close()
            flash('Information updated successfully.')
        except Exception as e:
            flash('An error occurred while updating information.')
            print(f"Error: {e}")

    # Fetch the doctor's current information
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("SELECT first_name, last_name, phone, email FROM doctor WHERE doctor_id = %s", (doctor_id,))
    doctor = cur.fetchone()
    cur.close()

    return render_template('Doctor/docdash.html', doctor=doctor)