from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/dashboard/doctor', methods=['GET'])  # Ensure the route matches the expected URL
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('user_routes.login'))

    doctor_id = session.get('user_id')

    # Fetch the doctor's name and details
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("SELECT first_name, last_name FROM doctor WHERE doctor_id = %s", (doctor_id,))
    doctor = cur.fetchone()
    cur.close()

    if not doctor:
        flash('Doctor not found. Please contact support.')
        return redirect(url_for('user_routes.login'))

    doctor_name = f"{doctor[0]} {doctor[1]}"

    filter_date = request.args.get('filter_date')
    filter_hospital = request.args.get('filter_hospital')

    cur = current_app.config['mysql'].connection.cursor()

    # Fetch hospital IDs associated with the doctor
    cur.execute("SELECT hospital_id FROM hospital_doctors WHERE doctor_id = %s", (doctor_id,))
    hospital_ids = [row[0] for row in cur.fetchall()]

    # Fetch hospital details for the dropdown
    hospitals = []
    if hospital_ids:
        cur.execute("SELECT hospital_id, name FROM hospital WHERE hospital_id IN %s", (tuple(hospital_ids),))
        hospitals = [{'hospital_id': str(row[0]), 'name': row[1]} for row in cur.fetchall()]

    # Fetch appointments based on filters
    query = """
        SELECT a.date, a.time, p.first_name AS patient_first_name, p.last_name AS patient_last_name, 
               a.status, h.name AS hospital_name
        FROM appointment a
        JOIN patient p ON a.patient_id = p.patient_id
        JOIN hospital h ON a.hospital_id = h.hospital_id
        WHERE a.doctor_id = %s
    """
    params = [doctor_id]

    if filter_date:
        query += " AND a.date = %s"
        params.append(filter_date)
    if filter_hospital:
        query += " AND a.hospital_id = %s"
        params.append(filter_hospital)

    query += " ORDER BY a.date, a.time"
    cur.execute(query, params)
    appointments = cur.fetchall()
    cur.close()

    return render_template('Doctor/docdash.html', doctor_name=doctor_name, appointments=appointments, 
                           hospitals=hospitals, filter_date=filter_date, filter_hospital=filter_hospital)

@dashboard_routes.route('/dashboard/patient', methods=['GET'])
def patient_dashboard():
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('user_id')

    # Fetch the patient's name and details
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("SELECT first_name, last_name FROM patient WHERE patient_id = %s", (patient_id,))
    patient = cur.fetchone()
    cur.close()

    if not patient:
        flash('Patient not found. Please contact support.')
        return redirect(url_for('user_routes.login'))

    patient_name = f"{patient[0]} {patient[1]}"

    # Fetch the patient's appointments
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("""
        SELECT a.date, a.time, d.first_name AS doctor_first_name, d.last_name AS doctor_last_name, 
               a.status, h.name AS hospital_name
        FROM appointment a
        JOIN doctor d ON a.doctor_id = d.doctor_id
        JOIN hospital h ON a.hospital_id = h.hospital_id
        WHERE a.patient_id = %s
        ORDER BY a.date, a.time
    """, (patient_id,))
    appointments = cur.fetchall()
    cur.close()

    return render_template('Patient/patdash.html', patient_name=patient_name, appointments=appointments)

@dashboard_routes.route('/dashboard/insurance', methods=['GET'])
def insurance_dashboard():
    if 'role' not in session or session['role'] != 'Insurance':
        flash('Unauthorized access. Please log in as an insurance provider.')
        return redirect(url_for('user_routes.login'))

    insurance_provider_id = session.get('user_id')

    # Fetch the insurance provider's name
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("SELECT insurance_name FROM insurance_provider WHERE insurance_id = %s", (insurance_provider_id,))
    insurance_provider = cur.fetchone()
    cur.close()

    if not insurance_provider:
        flash('Insurance provider not found. Please contact support.')
        return redirect(url_for('user_routes.login'))

    insurance_name = insurance_provider[0]

    # Fetch claims handled by this insurance provider
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("""
        SELECT bc.billing_cost_id, bc.total_amount, bc.insurance_covered, bc.payment_status, 
               p.first_name AS patient_first_name, p.last_name AS patient_last_name
        FROM billing_cost bc
        JOIN patient_billing pb ON bc.billing_cost_id = pb.billing_cost_id
        JOIN patient p ON pb.patient_id = p.patient_id
        WHERE pb.insurance_provider_id = %s
    """, (insurance_provider_id,))
    claims = cur.fetchall()
    cur.close()

    return render_template('Insurance/insurdash.html', insurance_name=insurance_name, claims=claims)

@dashboard_routes.route('/dashboard/billing', methods=['GET'])
def billing_dashboard():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    # Fetch billing records
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("""
        SELECT pb.bill_id, bc.total_amount, bc.payment_status, bc.insurance_covered, 
               p.first_name AS patient_first_name, p.last_name AS patient_last_name
        FROM patient_billing pb
        JOIN billing_cost bc ON pb.billing_cost_id = bc.billing_cost_id
        JOIN patient p ON pb.patient_id = p.patient_id
    """)
    billing_records = cur.fetchall()
    cur.close()

    return render_template('Billing/billdash.html', billing_records=billing_records)
