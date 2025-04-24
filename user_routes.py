from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import bcrypt
from admin_routes import admin_routes

user_routes = Blueprint('user_routes', __name__)

def is_valid_bcrypt_hash(hash_str):
    """Validate if the given string is a valid bcrypt hash."""
    try:
        bcrypt.checkpw(b'test', hash_str.encode('utf-8'))
        return True
    except ValueError:
        return False

def redirect_to_dashboard(role):
    """Redirect user to the appropriate dashboard based on their role."""
    try:
        if role == 'Doctor':
            return redirect(url_for('doctor_routes.doctor_dashboard'))
        elif role == 'Billing Staff':
            return redirect(url_for('billing_routes.billing_dashboard'))  
        elif role == 'Patient':
            return redirect(url_for('patient_routes.patient_dashboard'))  
        elif role == 'Insurance':
            return redirect(url_for('insurance_routes.insurance_dashboard')) 
        elif role == 'Admin':  # Added case for Admin role
            return redirect(url_for('admin_routes.admin_dashboard'))
        else:
            flash('Invalid role. Please contact support.')
            return redirect(url_for('user_routes.login'))
    except Exception as e:
        print(f"Error during redirection: {e}")  # Debugging log
        flash('An error occurred during redirection. Please try again.')
        return redirect(url_for('user_routes.login'))

@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Attempting login with username: {username}")  # Debugging log
        try:
            cur = current_app.config['mysql'].connection.cursor()
            cur.execute("""
                SELECT id, password, role, doctor_id, patient_id, insurance_provider_id 
                FROM users 
                WHERE username=%s
            """, (username,))
            user = cur.fetchone()
            cur.close()
            print(f"Query result: {user}")  # Debugging log
            if user:
                stored_password = user['password']
                if not is_valid_bcrypt_hash(stored_password):
                    print(f"Invalid bcrypt hash format for user: {username}")
                    flash('An error occurred. Please contact support.')
                    return render_template('login.html')

                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    # Store the `id` from the `users` table in the session
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    # Store the role-specific ID in the session
                    session['role_specific_id'] = (
                        user['doctor_id'] if user['role'] == 'Doctor' else
                        user['patient_id'] if user['role'] == 'Patient' else
                        user['insurance_provider_id'] if user['role'] == 'Insurance' else
                        None  # No role-specific ID for Billing Staff
                    )
                    print(f"Login successful for user ID: {session['user_id']}, role: {user['role']}, role-specific ID: {session['role_specific_id']}")
                    return redirect_to_dashboard(user['role'])
                else:
                    flash('Invalid password')
                    print("Invalid password")
            else:
                flash('Username not found')
                print("Username not found")
        except Exception as e:
            print(f"Error during login: {e}")
            flash('An error occurred. Please try again.')
    return render_template('login.html')

@user_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print(f"Form data received: {request.form}")

        username = request.form['username']
        password = request.form['password']
        role = 'Patient'  

        first_name = request.form.get('patient_first_name')
        last_name = request.form.get('patient_last_name')
        phone = request.form.get('patient_phone')
        email = request.form.get('patient_email')
        address = request.form.get('patient_address')

        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur = current_app.config['mysql'].connection.cursor()

            # Insert into the `patient` table
            cur.execute("""
                INSERT INTO patient (first_name, last_name, phone, email, address)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, phone, email, address))
            current_app.config['mysql'].connection.commit()
            patient_id = cur.lastrowid

            # Insert into the `users` table
            cur.execute("""
                INSERT INTO users (username, password, role, patient_id)
                VALUES (%s, %s, %s, %s)
            """, (username, hashed_password, role, patient_id))
            current_app.config['mysql'].connection.commit()

            cur.close()
            flash('Patient registered successfully!', 'success')
            return redirect(url_for('user_routes.login'))
        except Exception as e:
            print(f"Error during patient registration: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('user_routes.register'))

    return render_template('register.html')

@user_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_routes.login'))
