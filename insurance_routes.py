from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
import bcrypt

insurance_routes = Blueprint('insurance_routes', __name__)

@insurance_routes.route('/dashboard/insurance', methods=['GET', 'POST'])
def insurance_dashboard():
    if 'role' not in session or session['role'] != 'Insurance':
        flash('Unauthorized access. Please log in as an insurance provider.')
        return redirect(url_for('user_routes.login'))

    insurance_provider_id = session.get('role_specific_id')  # Use the role-specific ID for insurance operations

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

    return render_template('Insurance/insurdash.html', insurance_provider=insurance_provider, insurance_name=insurance_provider['insurance_name'])

@insurance_routes.route('/dashboard/insurance/claims', methods=['GET', 'POST'])
def insurance_claims():
    if 'role' not in session or session['role'] != 'Insurance':
        return redirect(url_for('user_routes.login'))

    insurance_provider_id = session.get('user_id')
    cur = current_app.config['mysql'].connection.cursor()

    # Handle filters
    date_filter = request.args.get('date')
    insurance_covered_filter = request.args.get('insurance_covered')

    query = """
        SELECT pb.bill_id, bc.total_amount, bc.payment_status, bc.insurance_claimed, bc.insurance_covered, a.date
        FROM patient_billing pb
        JOIN billing_cost bc ON pb.billing_cost_id = bc.billing_cost_id
        JOIN appointment a ON pb.appointment_id = a.appointment_id
        WHERE pb.insurance_provider_id = %s
    """
    params = [insurance_provider_id]

    if date_filter:
        query += " AND a.date = %s"
        params.append(date_filter)
    if insurance_covered_filter:
        query += " AND bc.insurance_claimed = %s"
        params.append(1 if insurance_covered_filter.lower() == 'y' else 0)

    cur.execute(query, params)
    claims = cur.fetchall()

    # Handle updates to insurance coverage
    alert_message = None
    if request.method == 'POST':
        bill_id = request.form.get('bill_id')
        try:
            if 'update_coverage' in request.form:
                # Update insurance coverage
                insurance_covered = request.form.get('insurance_covered')
                cur.execute("""
                    UPDATE billing_cost
                    SET insurance_covered = %s
                    WHERE billing_cost_id = (SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s)
                """, (insurance_covered, bill_id))
                current_app.config['mysql'].connection.commit()
                alert_message = 'Insurance coverage updated successfully.'
            elif 'toggle_claimed' in request.form:
                # Toggle insurance_claimed status
                cur.execute("""
                    UPDATE billing_cost
                    SET insurance_claimed = NOT insurance_claimed
                    WHERE billing_cost_id = (SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s)
                """, (bill_id,))
                current_app.config['mysql'].connection.commit()
                alert_message = 'Insurance claimed status toggled successfully.'
        except Exception as e:
            print(f"Error: {e}")
            alert_message = 'An error occurred while processing your request.'

    cur.close()

    return render_template('Insurance/claims.html', claims=claims, alert_message=alert_message)

@insurance_routes.route('/dashboard/insurance/update_credentials', methods=['POST'])
def update_insurance_credentials():
    if 'role' not in session or session['role'] != 'Insurance':
        flash('Unauthorized access. Please log in as an insurance provider.')
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

    return redirect(url_for('insurance_routes.insurance_dashboard'))
