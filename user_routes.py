from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import bcrypt
from admin_routes import admin_routes  # Import the admin_routes blueprint

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
            return redirect(url_for('doctor_routes.doctor_dashboard'))  # Updated blueprint reference
        elif role == 'Billing Staff':
            return redirect(url_for('billing_routes.billing_dashboard'))  # Updated blueprint reference
        elif role == 'Patient':
            return redirect(url_for('patient_routes.patient_dashboard'))  # Updated blueprint reference
        elif role == 'Insurance':
            return redirect(url_for('insurance_routes.insurance_dashboard'))  # Updated blueprint reference
        elif role == 'Admin':  # Added case for Admin role
            return redirect(url_for('admin_routes.admin_dashboard'))  # Updated blueprint reference
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
        role = request.form['role']

        if role == 'Patient':
            first_name = request.form.get('patient_first_name')
            last_name = request.form.get('patient_last_name')
            phone = request.form.get('patient_phone')
            email = request.form.get('patient_email')
            address = request.form.get('patient_address')
        elif role == 'Doctor':
            first_name = request.form.get('doctor_first_name')
            last_name = request.form.get('doctor_last_name')
            phone = request.form.get('doctor_phone')
            email = request.form.get('doctor_email')
            speciality = request.form.get('speciality')
        elif role == 'Insurance':
            insurance_name = request.form.get('insurance_name')
            contact_number = request.form.get('contact_number')
            insurance_type = request.form.get('insurance_type')

        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if not hashed_password.startswith('$2b$'):
                raise ValueError("Generated hash is invalid")

            cur = current_app.config['mysql'].connection.cursor()

            if role == 'Patient':
                cur.execute("""
                    INSERT INTO patient (first_name, last_name, phone, email, address)
                    VALUES (%s, %s, %s, %s, %s)
                """, (first_name, last_name, phone, email, address))
                current_app.config['mysql'].connection.commit()
                patient_id = cur.lastrowid
                cur.execute("""
                    INSERT INTO users (username, password, role, patient_id)
                    VALUES (%s, %s, %s, %s)
                """, (username, hashed_password, role, patient_id))

            elif role == 'Doctor':
                cur.execute("SELECT professions_id FROM professions WHERE professions_id = %s", (speciality,))
                if not cur.fetchone():
                    flash('Invalid specialty selected.')
                    return render_template('register.html')

                print(f"Inserting into doctor table: first_name={first_name}, last_name={last_name}, speciality={speciality}, phone={phone}, email={email}")

                cur.execute("""
                    INSERT INTO doctor (first_name, last_name, speciality, phone, email)
                    VALUES (%s, %s, %s, %s, %s)
                """, (first_name, last_name, speciality, phone, email))
                current_app.config['mysql'].connection.commit()
                doctor_id = cur.lastrowid

                print(f"Inserting into users table: username={username}, hashed_password={hashed_password}, role={role}, doctor_id={doctor_id}")

                cur.execute("""
                    INSERT INTO users (username, password, role, doctor_id)
                    VALUES (%s, %s, %s, %s)
                """, (username, hashed_password, role, doctor_id))

            elif role == 'Insurance':
                cur.execute("""
                    INSERT INTO insurance_provider (insurance_name, contact_number, insurance_type)
                    VALUES (%s, %s, %s)
                """, (insurance_name, contact_number, insurance_type))
                current_app.config['mysql'].connection.commit()
                insurance_provider_id = cur.lastrowid
                cur.execute("""
                    INSERT INTO users (username, password, role, insurance_provider_id)
                    VALUES (%s, %s, %s, %s)
                """, (username, hashed_password, role, insurance_provider_id))

            elif role == 'Billing Staff':
                cur.execute("""
                    INSERT INTO users (username, password, role)
                    VALUES (%s, %s, %s)
                """, (username, hashed_password, role))

            else:
                flash('Invalid role or missing required fields.')
                return render_template('register.html')

            current_app.config['mysql'].connection.commit()
            cur.close()
            flash('User registered successfully!')
            return redirect(url_for('user_routes.login'))

        except Exception as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.')
            return render_template('register.html')

    else:
        try:
            cur = current_app.config['mysql'].connection.cursor()
            cur.execute("SELECT professions_id, type FROM professions")
            professions = cur.fetchall()
            cur.close()
        except Exception as e:
            print(f"Error fetching professions: {e}")
            professions = []
        return render_template('register.html', professions=professions)

@user_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_routes.login'))

@user_routes.route('/dashboard/admin', methods=['GET'])
def admin_dashboard():
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))

    return render_template('Admin/dashboard.html')
