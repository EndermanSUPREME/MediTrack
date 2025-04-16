from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt  # Import bcrypt for password hashing

app = Flask(__name__)

# MySQL connection configuration for XAMPP
app.config['MYSQL_HOST'] = '10.37.1.103'  # XAMPP MySQL runs on localhost
app.config['MYSQL_USER'] = 'yoyojesus'       # Default XAMPP MySQL username
app.config['MYSQL_PASSWORD'] = 'veryOkIrTIcA'       # Default XAMPP MySQL password is empty
app.config['MYSQL_DB'] = 'meditrack'    # Replace with your local database name

mysql = MySQL(app)

app.secret_key = '24932781d8d03f8a7ff6fdff8d8780f1'  # seeds hashing function

def is_valid_bcrypt_hash(hash_str):
    """Validate if the given string is a valid bcrypt hash."""
    return hash_str.startswith('$2b$') and len(hash_str) == 60

def redirect_to_dashboard(role):
    """Redirect user to the appropriate dashboard based on their role."""
    if role == 'Doctor':
        return redirect(url_for('doctor_dashboard'))
    elif role == 'Billing Staff':
        return redirect(url_for('billing_dashboard'))  # Ensure this route exists
    elif role == 'Patient':
        return redirect(url_for('patient_dashboard'))  # Ensure this route exists
    elif role == 'Insurance':
        return redirect(url_for('insurance_dashboard'))  # Ensure this route exists
    else:
        flash('Invalid role. Please contact support.')  # Add a fallback for invalid roles
        return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/datacheck')
def show_patients():
    # Fetch patients from the meditrack database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patient")
    patients = cur.fetchall()
    cur.close()

    # Fetch users from the same database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    cur.close()

    # Fetch doctors from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT doctor_id, first_name, last_name, speciality, phone FROM doctor")
    doctors = cur.fetchall()
    cur.close()

    # Fetch insurance providers from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT insurance_id, insurance_name, insurance_type, contact_number FROM insurance_provider")
    insurances = cur.fetchall()
    cur.close()

    return render_template('check.html', patients=patients, users=users, doctors=doctors, insurances=insurances)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Attempting login with username: {username}")  # Debugging log
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, password, role FROM users WHERE username=%s", (username,))
            user = cur.fetchone()
            cur.close()
            print(f"Query result: {user}")  # Debugging log
            if user:
                stored_password = user[1]
                if not is_valid_bcrypt_hash(stored_password):
                    print(f"Invalid bcrypt hash format for user: {username}")  # Debugging log
                    flash('An error occurred. Please contact support.')
                    return render_template('login.html')

                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    session['user_id'] = user[0]
                    session['role'] = user[2]
                    print(f"Login successful for user ID: {user[0]}, role: {user[2]}")  # Debugging log
                    return redirect_to_dashboard(user[2])  # Redirect based on role
                else:
                    flash('Invalid password')  # More specific error message
                    print("Invalid password")  # Debugging log
            else:
                flash('Username not found')  # More specific error message
                print("Username not found")  # Debugging log
        except Exception as e:
            print(f"Error during login: {e}")  # Debugging log
            flash('An error occurred. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Debugging: Log the form data received
        print(f"Form data received: {request.form}")

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Fetch role-specific fields
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
            # Generate bcrypt hash for the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if not hashed_password.startswith('$2b$'):
                raise ValueError("Generated hash is invalid")

            cur = mysql.connection.cursor()

            # Insert into the appropriate table based on the role
            if role == 'Patient':
                cur.execute("""
                    INSERT INTO patient (first_name, last_name, phone, email, address)
                    VALUES (%s, %s, %s, %s, %s)
                """, (first_name, last_name, phone, email, address))
                mysql.connection.commit()
                patient_id = cur.lastrowid  # Get the auto-generated patient_id
                cur.execute("""
                    INSERT INTO users (username, password, role, patient_id)
                    VALUES (%s, %s, %s, %s)
                """, (username, hashed_password, role, patient_id))

            elif role == 'Doctor':
                # Ensure speciality is valid and matches a professions_id
                cur.execute("SELECT professions_id FROM professions WHERE professions_id = %s", (speciality,))
                if not cur.fetchone():
                    flash('Invalid specialty selected.')
                    return render_template('register.html')

                # Debugging: Log the values being inserted into the doctor table
                print(f"Inserting into doctor table: first_name={first_name}, last_name={last_name}, speciality={speciality}, phone={phone}, email={email}")

                # Insert into the doctor table
                cur.execute("""
                    INSERT INTO doctor (first_name, last_name, speciality, phone, email)
                    VALUES (%s, %s, %s, %s, %s)
                """, (first_name, last_name, speciality, phone, email))
                mysql.connection.commit()
                doctor_id = cur.lastrowid  # Get the auto-generated doctor_id

                # Debugging: Log the values being inserted into the users table
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
                mysql.connection.commit()
                insurance_provider_id = cur.lastrowid  # Get the auto-generated insurance_id
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

            mysql.connection.commit()
            cur.close()
            flash('User registered successfully!')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Error during registration: {e}")  # Debugging log
            flash('An error occurred during registration. Please try again.')
            return render_template('register.html')

    else:
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT professions_id, type FROM professions")
            professions = cur.fetchall()
            cur.close()
        except Exception as e:
            print(f"Error fetching professions: {e}")
            professions = []
        return render_template('register.html', professions=professions)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))
    return f"Welcome, {session['role']}! This is a placeholder dashboard."

@app.route('/dashboard/doctor', methods=['GET'])
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'Doctor':
        flash('Unauthorized access. Please log in as a doctor.')
        return redirect(url_for('login'))

    doctor_id = session.get('user_id')

    # Fetch the doctor's name and details
    cur = mysql.connection.cursor()
    cur.execute("SELECT first_name, last_name FROM doctor WHERE doctor_id = %s", (doctor_id,))
    doctor = cur.fetchone()
    cur.close()

    if not doctor:
        flash('Doctor not found. Please contact support.')
        return redirect(url_for('login'))

    doctor_name = f"{doctor[0]} {doctor[1]}"

    filter_date = request.args.get('filter_date')
    filter_hospital = request.args.get('filter_hospital')

    cur = mysql.connection.cursor()

    # Fetch hospitals for the dropdown
    cur.execute("SELECT hospital_id, name FROM hospital")
    hospitals = cur.fetchall()

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

    return render_template('docdash.html', doctor_name=doctor_name, appointments=appointments, 
                           hospitals=hospitals, filter_date=filter_date, filter_hospital=filter_hospital)

@app.route('/dashboard/patient', methods=['GET'])
def patient_dashboard():
    if 'role' not in session or session['role'] != 'Patient':
        flash('Unauthorized access. Please log in as a patient.')
        return redirect(url_for('login'))

    patient_id = session.get('user_id')

    # Fetch the patient's name and details
    cur = mysql.connection.cursor()
    cur.execute("SELECT first_name, last_name FROM patient WHERE patient_id = %s", (patient_id,))
    patient = cur.fetchone()
    cur.close()

    if not patient:
        flash('Patient not found. Please contact support.')
        return redirect(url_for('login'))

    patient_name = f"{patient[0]} {patient[1]}"

    # Fetch the patient's appointments
    cur = mysql.connection.cursor()
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

    return render_template('patientdash.html', patient_name=patient_name, appointments=appointments)

@app.route('/dashboard/insurance', methods=['GET'])
def insurance_dashboard():
    if 'role' not in session or session['role'] != 'Insurance':
        flash('Unauthorized access. Please log in as an insurance provider.')
        return redirect(url_for('login'))

    insurance_provider_id = session.get('user_id')

    # Fetch the insurance provider's name
    cur = mysql.connection.cursor()
    cur.execute("SELECT insurance_name FROM insurance_provider WHERE insurance_id = %s", (insurance_provider_id,))
    insurance_provider = cur.fetchone()
    cur.close()

    if not insurance_provider:
        flash('Insurance provider not found. Please contact support.')
        return redirect(url_for('login'))

    insurance_name = insurance_provider[0]

    # Fetch claims handled by this insurance provider
    cur = mysql.connection.cursor()
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

    return render_template('insurancedash.html', insurance_name=insurance_name, claims=claims)

if __name__ == "__main__":
    app.run(debug=True)
