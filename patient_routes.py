from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app, jsonify
import bcrypt
from datetime import datetime

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

@patient_routes.route('/dashboard/patient/insurance', methods=['GET', 'POST'])
def patient_insurance():
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('user_id')  # This corresponds to the `patient_id` in the `patient` table

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch current insurance for the patient
        query_current_insurance = """
            SELECT ip.insurance_id, ip.insurance_name, pt.type AS insurance_type
            FROM patient_insurance pi
            JOIN insurance_provider ip ON pi.insurance_id = ip.insurance_id
            JOIN professions pt ON ip.insurance_type = pt.professions_id
            WHERE pi.patient_id = %s
        """
        cur.execute(query_current_insurance, (patient_id,))
        current_insurance = cur.fetchall()

        # Fetch all available insurance providers
        query_available_insurance = """
            SELECT ip.insurance_id, ip.insurance_name, pt.type AS insurance_type
            FROM insurance_provider ip
            JOIN professions pt ON ip.insurance_type = pt.professions_id
            WHERE ip.insurance_id NOT IN (
                SELECT insurance_id
                FROM patient_insurance
                WHERE patient_id = %s
            )
        """
        cur.execute(query_available_insurance, (patient_id,))
        available_insurance = cur.fetchall()

        # Handle adding new insurance
        if request.method == 'POST':
            if 'add_insurance' in request.form:
                selected_insurance_id = request.form.get('insurance_id')
                if selected_insurance_id:
                    try:
                        cur.execute("""
                            INSERT INTO patient_insurance (patient_id, insurance_id)
                            VALUES (%s, %s)
                        """, (patient_id, selected_insurance_id))
                        current_app.config['mysql'].connection.commit()
                        flash('Insurance added successfully.')
                        return redirect(url_for('patient_routes.patient_insurance'))
                    except Exception as e:
                        flash('An error occurred while adding insurance.')
                        print(f"Error: {e}")
            elif 'remove_insurance' in request.form:
                insurance_id_to_remove = request.form.get('insurance_id')
                if insurance_id_to_remove:
                    try:
                        cur.execute("""
                            DELETE FROM patient_insurance
                            WHERE patient_id = %s AND insurance_id = %s
                        """, (patient_id, insurance_id_to_remove))
                        current_app.config['mysql'].connection.commit()
                        flash('Insurance removed successfully.')
                        return redirect(url_for('patient_routes.patient_insurance'))
                    except Exception as e:
                        flash('An error occurred while removing insurance.')
                        print(f"Error: {e}")

        cur.close()
    except Exception as e:
        flash('An error occurred while fetching insurance data.')
        print(f"Error: {e}")
        current_insurance = []
        available_insurance = []

    return render_template('Patient/insurance.html', current_insurance=current_insurance, available_insurance=available_insurance)

@patient_routes.route('/dashboard/patient/bills', methods=['GET'])
def patient_bills():
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('user_id')  # This corresponds to the `patient_id` in the `patient` table

    try:
        cur = current_app.config['mysql'].connection.cursor()
        query = """
            SELECT pb.bill_id, bc.total_amount, bc.payment_status, 
                   bc.insurance_claimed, bc.insurance_covered
            FROM patient_billing pb
            JOIN billing_cost bc ON pb.billing_cost_id = bc.billing_cost_id
            WHERE pb.patient_id = %s AND bc.payment_status IN ('Paid', 'Pending', 'Pending - Denied')
        """
        cur.execute(query, (patient_id,))
        bills = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching your bills.')
        print(f"Error: {e}")
        bills = []

    return render_template('Patient/bills.html', bills=bills)

@patient_routes.route('/dashboard/patient/health', methods=['GET', 'POST'])
def update_health_demographics():
    """Update health demographics for the logged-in patient."""
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.', 'error')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('role_specific_id')

    if request.method == 'POST':
        date_of_birth = request.form.get('date_of_birth')
        weight = request.form.get('weight')
        height = request.form.get('height')

        try:
            cur = current_app.config['mysql'].connection.cursor()

            # Update the date_of_birth, weight, and height fields
            cur.execute("""
                UPDATE health_demographics
                SET date_of_birth = %s, weight = %s, height = %s, date_recorded = CURDATE()
                WHERE patient_id = %s
            """, (date_of_birth, weight, height, patient_id))
            
            # Commit the transaction
            current_app.config['mysql'].connection.commit()
            cur.close()

            flash('Health demographics updated successfully.', 'success')
        except Exception as e:
            flash('An error occurred while updating health demographics.', 'error')
            print(f"Error: {e}")

        return redirect(url_for('patient_routes.update_health_demographics'))

    # Fetch the current health demographics
    try:
        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("""
            SELECT patient_id, date_recorded, date_of_birth, weight, height, health_status
            FROM health_demographics
            WHERE patient_id = %s
        """, (patient_id,))
        health_data = cur.fetchone()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching health demographics.', 'error')
        print(f"Error: {e}")
        health_data = None

    return render_template('Patient/health.html', health_data=health_data)

@patient_routes.route('/api/hospitals/<int:hospital_id>/doctors', methods=['GET'])
def get_doctors_by_hospital(hospital_id):
    try:
        cur = current_app.config['mysql'].connection.cursor()
        query = """
            SELECT d.doctor_id, d.first_name, d.last_name
            FROM hospital_doctors hd
            JOIN doctor d ON hd.doctor_id = d.doctor_id
            WHERE hd.hospital_id = %s
        """
        cur.execute(query, (hospital_id,))
        doctors = cur.fetchall()
        cur.close()
        return jsonify(doctors)
    except Exception as e:
        print(f"Error fetching doctors for hospital {hospital_id}: {e}")
        return jsonify([]), 500

@patient_routes.route('/api/doctors/<int:doctor_id>/available-times', methods=['GET'])
def get_available_times(doctor_id):
    date = request.args.get('date')
    hospital_id = request.args.get('hospital_id')  # Pass the hospital ID from the frontend
    if not date or not hospital_id:
        return jsonify([]), 400

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch the hospital's operating hours
        query_hospital_hours = """
            SELECT operating_hours
            FROM hospital
            WHERE hospital_id = %s
        """
        cur.execute(query_hospital_hours, (hospital_id,))
        hospital = cur.fetchone()
        if not hospital or not hospital['operating_hours']:
            return jsonify([]), 400

        # Parse operating hours (e.g., "9:00 AM - 6:00 PM")
        operating_hours = hospital['operating_hours']
        start_time, end_time = operating_hours.split(' - ')
        start_time = convert_to_24_hour(start_time.strip())
        end_time = convert_to_24_hour(end_time.strip())

        # Fetch times already booked for the doctor on the given date
        query_booked_times = """
            SELECT time
            FROM appointment
            WHERE doctor_id = %s AND date = %s AND status = 'Scheduled'
        """
        cur.execute(query_booked_times, (doctor_id, date))
        booked_times = [row['time'] for row in cur.fetchall()]

        # Generate all possible times within operating hours in 30-minute intervals
        all_times = generate_time_slots(start_time, end_time)

        # Filter out booked times
        available_times = [time for time in all_times if time not in booked_times]

        # Convert available times to 12-hour format
        available_times_12_hour = [convert_to_12_hour(time) for time in available_times]

        cur.close()
        return jsonify(available_times_12_hour)
    except Exception as e:
        print(f"Error fetching available times for doctor {doctor_id} on {date}: {e}")
        return jsonify([]), 500

def convert_to_24_hour(time_str):
    """Convert time from 12-hour format (e.g., '9:00 AM') to 24-hour format (e.g., '09:00:00')."""
    from datetime import datetime
    return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M:%S')

def convert_to_12_hour(time_str):
    """Convert time from 24-hour format (e.g., '09:00:00') to 12-hour format (e.g., '9:00 AM')."""
    from datetime import datetime
    return datetime.strptime(time_str, '%H:%M:%S').strftime('%I:%M %p')

def generate_time_slots(start_time, end_time):
    """Generate 30-minute time slots between start_time and end_time."""
    from datetime import datetime, timedelta
    slots = []
    current_time = datetime.strptime(start_time, '%H:%M:%S')
    end_time = datetime.strptime(end_time, '%H:%M:%S')
    while current_time < end_time:
        slots.append(current_time.strftime('%H:%M:%S'))
        current_time += timedelta(minutes=30)
    return slots

@patient_routes.route('/dashboard/patient/appointments', methods=['POST'])
def schedule_appointment():
    """Handle scheduling a new appointment."""
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('role_specific_id')
    hospital_id = request.form.get('hospital_id')
    doctor_id = request.form.get('doctor_id')
    date = request.form.get('date')
    time = request.form.get('time')  # Time in 12-hour format (e.g., '04:30 PM')
    notes = request.form.get('notes')

    try:
        # Convert time to 24-hour format
        time_24_hour = datetime.strptime(time, '%I:%M %p').strftime('%H:%M:%S')

        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("""
            INSERT INTO appointment (date, time, status, notes, patient_id, doctor_id, hospital_id)
            VALUES (%s, %s, 'Scheduled', %s, %s, %s, %s)
        """, (date, time_24_hour, notes, patient_id, doctor_id, hospital_id))
        current_app.config['mysql'].connection.commit()
        cur.close()

        flash('Appointment scheduled successfully!', 'success')
    except Exception as e:
        flash('An error occurred while scheduling the appointment.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('patient_routes.view_appointments'))

@patient_routes.route('/dashboard/patient/appointments', methods=['GET'])
def view_appointments():
    """View all appointments for the logged-in patient."""
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('role_specific_id')

    try:
        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("""
            SELECT a.appointment_id, a.date, a.time, a.status, a.notes, 
                   CONCAT(d.first_name, ' ', d.last_name) AS doctor_name, 
                   h.name AS hospital_name
            FROM appointment a
            JOIN doctor d ON a.doctor_id = d.doctor_id
            JOIN hospital h ON a.hospital_id = h.hospital_id
            WHERE a.patient_id = %s AND LOWER(a.status) = 'scheduled'
        """, (patient_id,))
        scheduled_appointments = cur.fetchall()

        cur.execute("SELECT hospital_id, name FROM hospital")
        hospitals = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching appointments.', 'error')
        print(f"Error: {e}")
        scheduled_appointments = []
        hospitals = []

    return render_template('Patient/appointments.html', scheduled_appointments=scheduled_appointments, hospitals=hospitals)

@patient_routes.route('/dashboard/patient/appointments/cancel', methods=['POST'])
def cancel_appointment():
    """Cancel an appointment by setting its status to 'Canceled'."""
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.', 'error')
        return redirect(url_for('user_routes.login'))

    appointment_id = request.form.get('appointment_id')

    if not appointment_id:
        flash('Appointment ID is missing.', 'error')
        return redirect(url_for('patient_routes.view_appointments'))

    try:
        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("""
            UPDATE appointment
            SET status = 'Canceled'
            WHERE appointment_id = %s
        """, (appointment_id,))
        current_app.config['mysql'].connection.commit()
        cur.close()

        flash('Appointment canceled successfully.', 'success')
    except Exception as e:
        flash('An error occurred while canceling the appointment.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('patient_routes.view_appointments'))
