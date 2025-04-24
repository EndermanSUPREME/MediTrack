from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
import bcrypt

doctor_routes = Blueprint('doctor_routes', 'doctor_routes')

@doctor_routes.route('/dashboard/doctor', methods=['GET', 'POST'])
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    doctor_id = session.get('role_specific_id')

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

@doctor_routes.route('/dashboard/doctor/update_credentials', methods=['POST'])
def update_doctor_credentials():
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    user_id = session.get('user_id')
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

    return redirect(url_for('doctor_routes.doctor_dashboard'))

@doctor_routes.route('/dashboard/doctor/hospital', methods=['GET', 'POST'])
def manage_hospitals():
    """Manage hospitals assigned to the doctor."""
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    doctor_id = session.get('role_specific_id')

    # Fetch assigned hospitals
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("""
        SELECT h.hospital_id AS id, h.name 
        FROM hospital h
        JOIN hospital_doctors hd ON h.hospital_id = hd.hospital_id
        WHERE hd.doctor_id = %s
    """, (doctor_id,))
    assigned_hospitals = cur.fetchall()

    # Fetch available hospitals
    cur.execute("""
        SELECT hospital_id AS id, name 
        FROM hospital
        WHERE hospital_id NOT IN (
            SELECT hospital_id 
            FROM hospital_doctors 
            WHERE doctor_id = %s
        )
    """, (doctor_id,))
    available_hospitals = cur.fetchall()
    cur.close()

    return render_template('Doctor/hospital.html', assigned_hospitals=assigned_hospitals, available_hospitals=available_hospitals)

@doctor_routes.route('/dashboard/doctor/hospitals/add', methods=['POST'])
def add_hospital():
    """Add the doctor to a hospital."""
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    doctor_id = session.get('role_specific_id')
    hospital_id = request.form.get('hospital_id')

    try:
        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("""
            INSERT INTO hospital_doctors (doctor_id, hospital_id)
            VALUES (%s, %s)
        """, (doctor_id, hospital_id))
        current_app.config['mysql'].connection.commit()
        cur.close()
        flash('Successfully added to the hospital.')
    except Exception as e:
        flash('An error occurred while adding the hospital.')
        print(f"Error: {e}")

    return redirect(url_for('doctor_routes.manage_hospitals'))

@doctor_routes.route('/dashboard/doctor/hospitals/remove', methods=['POST'])
def remove_hospital():
    """Remove the doctor from a hospital."""
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    doctor_id = session.get('role_specific_id')
    hospital_id = request.form.get('hospital_id')

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Check if there are scheduled appointments for the doctor at the hospital
        cur.execute("""
            SELECT COUNT(*) AS appointment_count
            FROM appointment
            WHERE doctor_id = %s AND hospital_id = %s AND LOWER(status) = 'scheduled'
        """, (doctor_id, hospital_id))
        result = cur.fetchone()

        if result['appointment_count'] > 0:
            flash('Cannot remove the hospital because there are scheduled appointments.', 'error')
            cur.close()
            return redirect(url_for('doctor_routes.manage_hospitals'))

        # Proceed to remove the doctor from the hospital
        cur.execute("""
            DELETE FROM hospital_doctors
            WHERE doctor_id = %s AND hospital_id = %s
        """, (doctor_id, hospital_id))
        current_app.config['mysql'].connection.commit()

        if cur.rowcount == 0:  # Check if the deletion was successful
            flash('Failed to remove the hospital. Please try again.', 'error')
        else:
            flash('Successfully removed from the hospital.', 'success')

        cur.close()
    except Exception as e:
        flash('An error occurred while removing the hospital.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('doctor_routes.manage_hospitals'))

@doctor_routes.route('/dashboard/doctor/appointment', methods=['GET'])
def view_appointments():
    """View all appointments for the logged-in doctor, excluding completed ones."""
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    doctor_id = session.get('role_specific_id')

    try:
        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("""
            SELECT a.appointment_id AS id, a.date, a.time, a.status, a.notes, 
                   CONCAT(p.first_name, ' ', p.last_name) AS patient_name, p.patient_id,
                   hd.health_status, hd.weight, hd.height, hd.date_of_birth
            FROM appointment a
            JOIN patient p ON a.patient_id = p.patient_id
            LEFT JOIN health_demographics hd ON p.patient_id = hd.patient_id
            WHERE a.doctor_id = %s AND LOWER(a.status) NOT IN ('completed')
        """, (doctor_id,))
        appointments = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching appointments.', 'error')
        print(f"Error: {e}")
        appointments = []

    return render_template('Doctor/appointment.html', appointments=appointments)

@doctor_routes.route('/dashboard/doctor/appointments/complete_and_bill', methods=['POST'])
def complete_and_bill():
    """Mark an appointment as complete, update notes, and create a bill."""
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    appointment_id = request.form.get('appointment_id')
    notes = request.form.get('notes')

    if not appointment_id or not notes:
        flash('Appointment ID or notes are missing.', 'error')
        return redirect(url_for('doctor_routes.view_appointments'))

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch patient_id associated with the appointment
        cur.execute("""
            SELECT patient_id
            FROM appointment
            WHERE appointment_id = %s
        """, (appointment_id,))
        result = cur.fetchone()
        if not result:
            flash('Invalid appointment ID.', 'error')
            return redirect(url_for('doctor_routes.view_appointments'))

        patient_id = result['patient_id']

        # Mark the appointment as complete and update notes
        cur.execute("""
            UPDATE appointment
            SET status = 'Completed', notes = %s
            WHERE appointment_id = %s
        """, (notes, appointment_id))

        # Create a bill with default values
        cur.execute("""
            INSERT INTO billing_cost (total_amount, payment_status, insurance_claimed, insurance_covered)
            VALUES (NULL, 'Queued', 0, 0)
        """)
        billing_cost_id = cur.lastrowid

        # Link the bill to the appointment and patient
        cur.execute("""
            INSERT INTO patient_billing (billing_cost_id, appointment_id, patient_id, insurance_provider_id)
            VALUES (%s, %s, %s, NULL)
        """, (billing_cost_id, appointment_id, patient_id))

        current_app.config['mysql'].connection.commit()
        cur.close()
        flash('Appointment marked as complete and bill created successfully.', 'success')
    except Exception as e:
        flash('An error occurred while completing the appointment and creating the bill.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('doctor_routes.view_appointments'))

@doctor_routes.route('/dashboard/doctor/update_patient_health', methods=['POST'])
def update_patient_health():
    """Allow doctors to update a patient's health information."""
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.', 'error')
        return redirect(url_for('user_routes.login'))

    patient_id = request.form.get('patient_id')
    health_status = request.form.get('health_status')
    weight = request.form.get('weight')
    height = request.form.get('height')

    if not patient_id:
        flash('Patient ID is missing.', 'error')
        return redirect(url_for('doctor_routes.view_appointments'))

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Update the patient's health information
        cur.execute("""
            UPDATE health_demographics
            SET health_status = %s, weight = %s, height = %s, date_recorded = CURDATE()
            WHERE patient_id = %s
        """, (health_status, weight, height, patient_id))
        current_app.config['mysql'].connection.commit()
        cur.close()

        flash('Patient health information updated successfully.', 'success')
    except Exception as e:
        flash('An error occurred while updating patient health information.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('doctor_routes.view_appointments'))