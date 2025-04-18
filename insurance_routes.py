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

    insurance_provider_id = session.get('role_specific_id')  # Ensure this matches the insurance provider's ID
    cur = current_app.config['mysql'].connection.cursor()

    # Fetch claims with payment_status = 'Insurance'
    query = """
        SELECT pb.bill_id, bc.total_amount, bc.payment_status, a.date
        FROM patient_billing pb
        JOIN billing_cost bc ON pb.billing_cost_id = bc.billing_cost_id
        JOIN appointment a ON pb.appointment_id = a.appointment_id
        WHERE pb.insurance_provider_id = %s AND bc.payment_status = 'Insurance'
    """
    params = [insurance_provider_id]

    try:
        cur.execute(query, params)
        claims = cur.fetchall()
    except Exception as e:
        flash('An error occurred while fetching claims.')
        print(f"Error: {e}")
        claims = []

    # Handle updates to claims
    if request.method == 'POST':
        bill_id = request.form.get('bill_id')
        try:
            if 'approve_claim' in request.form:
                # Approve the claim by setting insurance_covered and insurance_claimed
                insurance_covered = request.form.get('insurance_covered')
                cur.execute("""
                    UPDATE billing_cost
                    SET insurance_covered = %s, insurance_claimed = 1, payment_status = 'Pending'
                    WHERE billing_cost_id = (SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s)
                """, (insurance_covered, bill_id))
                current_app.config['mysql'].connection.commit()
                flash('Claim approved successfully.')
            elif 'deny_claim' in request.form:
                # Deny the claim by setting insurance_claimed to 0 and updating the status
                cur.execute("""
                    UPDATE billing_cost
                    SET insurance_claimed = 0, payment_status = 'Pending - Denied'
                    WHERE billing_cost_id = (SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s)
                """, (bill_id,))
                current_app.config['mysql'].connection.commit()
                flash('Claim denied successfully.')
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred while processing your request.')

        # Redirect back to refresh the page and remove the processed claim
        return redirect(url_for('insurance_routes.insurance_claims'))

    cur.close()

    return render_template('Insurance/claims.html', claims=claims)

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
