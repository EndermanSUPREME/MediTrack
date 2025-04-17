from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/dashboard/doctor', methods=['GET', 'POST'])
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

@dashboard_routes.route('/dashboard/patient', methods=['GET', 'POST'])
def patient_dashboard():
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('user_routes.login'))

    patient_id = session.get('user_id')

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

@dashboard_routes.route('/dashboard/insurance', methods=['GET', 'POST'])
def insurance_dashboard():
    if 'role' not in session or session['role'] != 'Insurance':
        flash('Unauthorized access. Please log in as an insurance provider.')
        return redirect(url_for('user_routes.login'))

    insurance_provider_id = session.get('user_id')

    if request.method == 'POST':
        # Update insurance provider information
        insurance_name = request.form.get('insurance_name')
        contact_number = request.form.get('contact_number')
        try:
            cur = current_app.config['mysql'].connection.cursor()
            cur.execute("""
                UPDATE insurance_provider
                SET insurance_name = %s, contact_number = %s
                WHERE insurance_id = %s
            """, (insurance_name, contact_number, insurance_provider_id))
            current_app.config['mysql'].connection.commit()
            cur.close()
            flash('Information updated successfully.')
        except Exception as e:
            flash('An error occurred while updating information.')
            print(f"Error: {e}")

    # Fetch the insurance provider's current information
    cur = current_app.config['mysql'].connection.cursor()
    cur.execute("SELECT insurance_name, contact_number FROM insurance_provider WHERE insurance_id = %s", (insurance_provider_id,))
    insurance_provider = cur.fetchone()
    cur.close()

    return render_template('Insurance/insurdash.html', insurance_provider=insurance_provider)

@dashboard_routes.route('/dashboard/billing', methods=['GET', 'POST'])
def billing_dashboard():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    return render_template('Billing/billdash.html')
