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

    return redirect(url_for('billing_routes.billing_dashboard'))

@billing_routes.route('/dashboard/billing/queue', methods=['GET'])
def billing_queue():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()
        query = """
            SELECT b.bill_id AS id, CONCAT(p.first_name, ' ', p.last_name) AS patient_name, 
                   bc.total_amount AS amount, a.notes AS appointment_notes,
                   GROUP_CONCAT(ip.insurance_id, ':', ip.insurance_name, ' (', pt.type, ')') AS insurances
            FROM patient_billing b
            JOIN billing_cost bc ON b.billing_cost_id = bc.billing_cost_id
            JOIN patient p ON b.patient_id = p.patient_id
            LEFT JOIN appointment a ON b.appointment_id = a.appointment_id
            LEFT JOIN patient_insurance pi ON p.patient_id = pi.patient_id
            LEFT JOIN insurance_provider ip ON pi.insurance_id = ip.insurance_id
            LEFT JOIN professions pt ON ip.insurance_type = pt.professions_id
            WHERE bc.payment_status = 'Queued'
            GROUP BY b.bill_id
        """
        cur.execute(query)
        bills = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching queued bills.')
        print(f"Error: {e}")
        bills = []

    return render_template('Billing/queue.html', bills=bills)

@billing_routes.route('/dashboard/billing/queue/update_price/<int:bill_id>', methods=['POST'])
def update_bill_price(bill_id):
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    new_price = request.form.get('price')
    try:
        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("UPDATE billing_cost SET total_amount = %s WHERE billing_cost_id = (SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s)", (new_price, bill_id))
        current_app.config['mysql'].connection.commit()
        cur.close()
        flash('Price updated successfully.')
    except Exception as e:
        flash('An error occurred while updating the price.')
        print(f"Error: {e}")

    return redirect(url_for('billing_routes.billing_queue'))

@billing_routes.route('/dashboard/billing/queue/set_insurance/<int:bill_id>', methods=['POST'])
def set_insurance(bill_id):
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    selected_insurance_id = request.form.get('insurance_id')
    try:
        cur = current_app.config['mysql'].connection.cursor()
        # Update the insurance provider for the bill and set the payment status to 'Insurance'
        cur.execute("""
            UPDATE patient_billing
            SET insurance_provider_id = %s
            WHERE bill_id = %s
        """, (selected_insurance_id, bill_id))
        cur.execute("""
            UPDATE billing_cost
            SET payment_status = 'Insurance'
            WHERE billing_cost_id = (SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s)
        """, (bill_id,))
        current_app.config['mysql'].connection.commit()
        cur.close()
        flash('Bill status set to Insurance and insurance applied successfully.')
    except Exception as e:
        flash('An error occurred while updating the status.')
        print(f"Error: {e}")

    return redirect(url_for('billing_routes.billing_queue'))

@billing_routes.route('/dashboard/billing/records', methods=['GET'])
def billing_records():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    status_filter = request.args.get('status')
    patient_filter = request.args.get('patient')

    try:
        cur = current_app.config['mysql'].connection.cursor()
        query = """
            SELECT b.bill_id AS id, CONCAT(p.first_name, ' ', p.last_name) AS patient_name, 
                   bc.total_amount AS amount, bc.payment_status, a.date AS appointment_date, a.notes
            FROM patient_billing b
            JOIN billing_cost bc ON b.billing_cost_id = bc.billing_cost_id
            JOIN patient p ON b.patient_id = p.patient_id
            LEFT JOIN appointment a ON b.appointment_id = a.appointment_id
            WHERE bc.payment_status IN ('Pending', 'Pending - Denied', 'Paid')
        """
        params = []

        if status_filter:
            query += " AND bc.payment_status = %s"
            params.append(status_filter)
        if patient_filter:
            query += " AND CONCAT(p.first_name, ' ', p.last_name) LIKE %s"
            params.append(f"%{patient_filter}%")

        cur.execute(query, params)
        records = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching billing records.')
        print(f"Error: {e}")
        records = []

    return render_template('Billing/records.html', records=records, status_filter=status_filter, patient_filter=patient_filter)

@billing_routes.route('/dashboard/billing/payment', methods=['GET', 'POST'])
def billing_payment():
    if 'role' not in session or session['role'] != 'Billing Staff':
        flash('Unauthorized access. Please log in as billing staff.')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()
        query = """
            SELECT b.bill_id AS id, CONCAT(p.first_name, ' ', p.last_name) AS patient_name, 
                   bc.total_amount AS amount, bc.payment_status, bc.insurance_covered, a.notes AS appointment_notes
            FROM patient_billing b
            JOIN billing_cost bc ON b.billing_cost_id = bc.billing_cost_id
            JOIN patient p ON b.patient_id = p.patient_id
            LEFT JOIN appointment a ON b.appointment_id = a.appointment_id
            WHERE bc.payment_status IN ('Pending', 'Pending - Denied')
        """
        cur.execute(query)
        bills = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching bills.')
        print(f"Error: {e}")
        bills = []

    if request.method == 'POST':
        bill_id = request.form.get('bill_id')
        if 'set_paid' in request.form:
            try:
                cur = current_app.config['mysql'].connection.cursor()
                cur.execute("""
                    UPDATE billing_cost
                    SET payment_status = 'Paid'
                    WHERE billing_cost_id = (SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s)
                """, (bill_id,))
                current_app.config['mysql'].connection.commit()
                cur.close()
                flash('Bill status set to Paid.')
            except Exception as e:
                flash('An error occurred while updating the status.')
                print(f"Error: {e}")

        return redirect(url_for('billing_routes.billing_payment'))

    return render_template('Billing/payment.html', bills=bills)
