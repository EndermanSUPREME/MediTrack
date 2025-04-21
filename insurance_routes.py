from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
import bcrypt

insurance_routes = Blueprint('insurance_routes', __name__)

@insurance_routes.route('/index', methods=['GET'])
def insurance_index():
    """Render the insurance index page."""
    return render_template('Insurance/index.html')

@insurance_routes.route('/register', methods=['GET', 'POST'])
def insurance_register():
    """Handle insurance provider registration."""
    if request.method == 'POST':
        insurance_name = request.form.get('insurance_name')
        contact_number = request.form.get('contact_number')
        insurance_type = request.form.get('insurance_type')
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur = current_app.config['mysql'].connection.cursor()

            # Insert into the `insurance_provider` table
            cur.execute("""
                INSERT INTO insurance_provider (insurance_name, contact_number, insurance_type)
                VALUES (%s, %s, %s)
            """, (insurance_name, contact_number, insurance_type))
            current_app.config['mysql'].connection.commit()
            insurance_provider_id = cur.lastrowid

            # Insert into the `users` table
            cur.execute("""
                INSERT INTO users (username, password, role, insurance_provider_id)
                VALUES (%s, %s, %s, %s)
            """, (username, hashed_password, 'Insurance', insurance_provider_id))
            current_app.config['mysql'].connection.commit()

            cur.close()
            flash('Insurance provider registered successfully!', 'success')
            return redirect(url_for('insurance_routes.insurance_login'))  # Redirect to the insurance login page
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'error')
            print(f"Error during insurance registration: {e}")
            return redirect(url_for('insurance_routes.insurance_register'))

    return render_template('Insurance/register.html')

@insurance_routes.route('/login', methods=['GET', 'POST'])
def insurance_login():
    """Handle login for insurance providers."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            cur = current_app.config['mysql'].connection.cursor()
            cur.execute("""
                SELECT id, password, role, insurance_provider_id
                FROM users
                WHERE username = %s AND role = 'Insurance'
            """, (username,))
            user = cur.fetchone()
            cur.close()

            if user:
                stored_password = user['password']
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    session['role_specific_id'] = user['insurance_provider_id']
                    flash('Login successful!', 'success')
                    return redirect(url_for('insurance_routes.insurance_dashboard'))
                else:
                    flash('Invalid password.', 'error')
            else:
                flash('Username not found or not an insurance provider.', 'error')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')
            print(f"Error during insurance login: {e}")

    return render_template('Insurance/login.html')

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
def manage_claims():
    if 'role' not in session or session['role'] != 'Insurance':
        flash('Unauthorized access. Please log in as an insurance.')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()

        if request.method == 'POST':
            bill_id = request.form.get('bill_id')
            if 'approve_claim' in request.form:
                insurance_covered = request.form.get('insurance_covered')
                if not insurance_covered:
                    flash('Please enter a coverage amount to approve the claim.', 'danger')
                else:
                    try:
                        cur.execute("""
                            UPDATE billing_cost
                            SET payment_status = 'Pending', insurance_covered = %s, insurance_claimed = 1
                            WHERE billing_cost_id = (
                                SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s
                            )
                        """, (insurance_covered, bill_id))
                        current_app.config['mysql'].connection.commit()
                        flash('Claim approved successfully.', 'success')
                    except Exception as e:
                        flash('An error occurred while approving the claim.', 'danger')
                        print(f"Error: {e}")
            elif 'deny_claim' in request.form:
                try:
                    cur.execute("""
                        UPDATE billing_cost
                        SET payment_status = 'Pending - Denied', 
                            insurance_covered = 0, 
                            insurance_claimed = 0
                        WHERE billing_cost_id = (
                            SELECT billing_cost_id FROM patient_billing WHERE bill_id = %s
                        )
                    """, (bill_id,))
                    current_app.config['mysql'].connection.commit()
                    flash('Claim denied successfully.', 'success')
                except Exception as e:
                    flash('An error occurred while denying the claim.', 'danger')
                    print(f"Error: {e}")

        # Fetch claims with patient name and appointment notes
        query = """
            SELECT pb.bill_id, CONCAT(p.first_name, ' ', p.last_name) AS patient_name, 
                   bc.total_amount, bc.payment_status, a.date, a.notes
            FROM patient_billing pb
            JOIN billing_cost bc ON pb.billing_cost_id = bc.billing_cost_id
            JOIN patient p ON pb.patient_id = p.patient_id
            JOIN appointment a ON pb.appointment_id = a.appointment_id
            WHERE bc.payment_status = 'Insurance'
        """
        cur.execute(query)
        claims = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching claims.', 'danger')
        print(f"Error: {e}")
        claims = []

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
