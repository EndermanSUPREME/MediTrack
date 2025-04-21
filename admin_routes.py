from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
import bcrypt

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/dashboard', methods=['GET'])
def admin_dashboard():
    """Render the admin dashboard."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))
    return render_template('admin/dashboard.html')

@admin_routes.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    """Manage users in the system."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch all users
        cur.execute("""
            SELECT u.id, u.username, u.role, 
                   d.first_name AS doctor_first_name, d.last_name AS doctor_last_name,
                   p.first_name AS patient_first_name, p.last_name AS patient_last_name,
                   i.insurance_name AS insurance_name
            FROM users u
            LEFT JOIN doctor d ON u.doctor_id = d.doctor_id
            LEFT JOIN patient p ON u.patient_id = p.patient_id
            LEFT JOIN insurance_provider i ON u.insurance_provider_id = i.insurance_id
        """)
        users = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching user data.', 'error')
        print(f"Error: {e}")
        users = []

    return render_template('admin/manage_users.html', users=users)

@admin_routes.route('/manage_users/delete', methods=['POST'])
def delete_user():
    """Delete a user and their respective entry from the system."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))

    user_id = request.form.get('user_id')

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch the user's role and role-specific IDs
        cur.execute("""
            SELECT role, doctor_id, patient_id, insurance_provider_id
            FROM users
            WHERE id = %s
        """, (user_id,))
        user = cur.fetchone()

        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_routes.manage_users'))

        if user['role'] == 'Admin':
            flash('Admin accounts cannot be deleted.', 'error')
            return redirect(url_for('admin_routes.manage_users'))

        # Check for related constraints before deletion
        if user['role'] == 'Doctor' and user['doctor_id']:
            cur.execute("""
                SELECT COUNT(*) AS appointment_count
                FROM appointment
                WHERE doctor_id = %s AND LOWER(status) = 'scheduled'
            """, (user['doctor_id'],))
            result = cur.fetchone()
            if result['appointment_count'] > 0:
                flash('Cannot delete the doctor because there are scheduled appointments.', 'error')
                return redirect(url_for('admin_routes.manage_users'))

        elif user['role'] == 'Patient' and user['patient_id']:
            cur.execute("""
                SELECT COUNT(*) AS appointment_count
                FROM appointment
                WHERE patient_id = %s AND LOWER(status) = 'scheduled'
            """, (user['patient_id'],))
            result = cur.fetchone()
            if result['appointment_count'] > 0:
                flash('Cannot delete the patient because there are scheduled appointments.', 'error')
                return redirect(url_for('admin_routes.manage_users'))

        elif user['role'] == 'Insurance' and user['insurance_provider_id']:
            cur.execute("""
                SELECT COUNT(*) AS billing_count
                FROM patient_billing
                WHERE insurance_provider_id = %s
            """, (user['insurance_provider_id'],))
            result = cur.fetchone()
            if result['billing_count'] > 0:
                flash('Cannot delete the insurance provider because there are associated bills.', 'error')
                return redirect(url_for('admin_routes.manage_users'))

        # Verify role-specific entry exists before deletion
        if user['role'] == 'Doctor' and user['doctor_id']:
            cur.execute("DELETE FROM doctor WHERE doctor_id = %s", (user['doctor_id'],))
        elif user['role'] == 'Patient' and user['patient_id']:
            cur.execute("DELETE FROM patient WHERE patient_id = %s", (user['patient_id'],))
        elif user['role'] == 'Insurance' and user['insurance_provider_id']:
            cur.execute("DELETE FROM insurance_provider WHERE insurance_id = %s", (user['insurance_provider_id'],))

        # Delete the user from the `users` table
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        current_app.config['mysql'].connection.commit()

        # Display success message
        flash('User and their respective entry deleted successfully.', 'success')

        cur.close()
    except Exception as e:
        flash('An error occurred while deleting the user.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('admin_routes.manage_users'))

@admin_routes.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Allow admins to change their password."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'error')
            return redirect(url_for('admin_routes.change_password'))

        try:
            cur = current_app.config['mysql'].connection.cursor()

            # Fetch the current password hash for the logged-in admin
            cur.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
            user = cur.fetchone()

            if not user or not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('admin_routes.change_password'))

            # Update the password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, session['user_id']))
            current_app.config['mysql'].connection.commit()
            cur.close()

            flash('Password changed successfully.', 'success')
        except Exception as e:
            flash('An error occurred while changing the password.', 'error')
            print(f"Error: {e}")

        return redirect(url_for('admin_routes.admin_dashboard'))

    return render_template('admin/change_password.html')

@admin_routes.route('/manage_users/change_password/<int:user_id>', methods=['GET', 'POST'])
def change_user_password(user_id):
    """Allow admin to change the password for a specific user."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch the username for the user
        cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_routes.manage_users'))

        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'error')
                return redirect(url_for('admin_routes.change_user_password', user_id=user_id))

            # Update the password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
            current_app.config['mysql'].connection.commit()
            cur.close()

            flash('Password changed successfully.', 'success')
            return redirect(url_for('admin_routes.manage_users'))

        cur.close()
    except Exception as e:
        flash('An error occurred while changing the password.', 'error')
        print(f"Error: {e}")

    return render_template('admin/change_user_password.html', username=user['username'], user_id=user_id)

@admin_routes.route('/view_reports', methods=['GET'])
def view_reports():
    """Generate and display reports for hospitals, doctors, patients, billing, and insurance."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch hospital reports
        cur.execute("""
            SELECT h.name, h.location, p.type AS care_type, 
                   COUNT(DISTINCT a.appointment_id) AS total_appointments,
                   COUNT(DISTINCT hd.doctor_id) AS total_doctors
            FROM hospital h
            LEFT JOIN appointment a ON h.hospital_id = a.hospital_id
            LEFT JOIN hospital_doctors hd ON h.hospital_id = hd.hospital_id
            LEFT JOIN professions p ON h.care_type = p.professions_id
            GROUP BY h.hospital_id
        """)
        hospital_reports = cur.fetchall()

        # Fetch doctor reports
        cur.execute("""
            SELECT CONCAT(d.first_name, ' ', d.last_name) AS name, p.type AS speciality,
                   COUNT(DISTINCT a.appointment_id) AS total_appointments,
                   GROUP_CONCAT(DISTINCT h.name SEPARATOR ', ') AS hospitals_assigned
            FROM doctor d
            LEFT JOIN appointment a ON d.doctor_id = a.doctor_id
            LEFT JOIN hospital_doctors hd ON d.doctor_id = hd.doctor_id
            LEFT JOIN hospital h ON hd.hospital_id = h.hospital_id
            LEFT JOIN professions p ON d.speciality = p.professions_id
            GROUP BY d.doctor_id
        """)
        doctor_reports = cur.fetchall()

        # Fetch patient reports
        cur.execute("""
            SELECT CONCAT(p.first_name, ' ', p.last_name) AS name,
                   COUNT(DISTINCT a.appointment_id) AS total_appointments,
                   COUNT(DISTINCT pb.bill_id) AS total_bills,
                   COALESCE((
                       SELECT SUM(bc.total_amount)
                       FROM billing_cost bc
                       JOIN patient_billing pb2 ON bc.billing_cost_id = pb2.billing_cost_id
                       WHERE pb2.patient_id = p.patient_id AND bc.payment_status = 'Paid'
                   ), 0) AS total_paid,
                   COALESCE((
                       SELECT SUM(bc.total_amount)
                       FROM billing_cost bc
                       JOIN patient_billing pb2 ON bc.billing_cost_id = pb2.billing_cost_id
                       WHERE pb2.patient_id = p.patient_id AND bc.payment_status != 'Paid'
                   ), 0) AS total_unpaid
            FROM patient p
            LEFT JOIN appointment a ON p.patient_id = a.patient_id
            LEFT JOIN patient_billing pb ON p.patient_id = pb.patient_id
            GROUP BY p.patient_id
        """)
        patient_reports = cur.fetchall()

        # Fetch billing reports
        cur.execute("""
            SELECT bc.billing_cost_id AS billing_id,
                   COALESCE(bc.total_amount, 0) AS total_amount,
                   bc.payment_status,
                   COALESCE(bc.insurance_covered, 0) AS insurance_covered
            FROM billing_cost bc
        """)
        billing_reports = cur.fetchall()

        # Fetch insurance reports
        cur.execute("""
            SELECT ip.insurance_id, ip.insurance_name, ip.contact_number, p.type AS insurance_type,
                   COUNT(DISTINCT pb.patient_id) AS total_patients,
                   COALESCE(SUM(bc.total_amount), 0) AS total_billed,
                   COALESCE(SUM(bc.insurance_covered), 0) AS total_covered
            FROM insurance_provider ip
            LEFT JOIN patient_billing pb ON ip.insurance_id = pb.insurance_provider_id
            LEFT JOIN billing_cost bc ON pb.billing_cost_id = bc.billing_cost_id
            LEFT JOIN professions p ON ip.insurance_type = p.professions_id
            GROUP BY ip.insurance_id
        """)
        insurance_reports = cur.fetchall()

        cur.close()
    except Exception as e:
        flash('An error occurred while generating reports.', 'error')
        print(f"Error: {e}")
        hospital_reports = []
        doctor_reports = []
        patient_reports = []
        billing_reports = []
        insurance_reports = []

    return render_template(
        'admin/view_reports.html',
        hospital_reports=hospital_reports,
        doctor_reports=doctor_reports,
        patient_reports=patient_reports,
        billing_reports=billing_reports,
        insurance_reports=insurance_reports
    )

@admin_routes.route('/manage_hospitals', methods=['GET'])
def manage_hospitals():
    """Display the manage hospitals page."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Fetch all hospitals
        cur.execute("""
            SELECT h.hospital_id, h.name, h.location, h.operating_hours, p.type AS care_type
            FROM hospital h
            JOIN professions p ON h.care_type = p.professions_id
        """)
        hospitals = cur.fetchall()

        # Fetch all care types
        cur.execute("SELECT professions_id, type FROM professions")
        professions = cur.fetchall()

        cur.close()
    except Exception as e:
        flash('An error occurred while fetching hospital data.', 'error')
        print(f"Error: {e}")
        hospitals = []
        professions = []

    return render_template('admin/manage_hospitals.html', hospitals=hospitals, professions=professions)

@admin_routes.route('/manage_hospitals/add', methods=['POST'])
def add_hospital():
    """Add a new hospital."""
    name = request.form.get('name')
    location = request.form.get('location')
    start_hour = request.form.get('start_hour').zfill(2)
    start_minute = request.form.get('start_minute').zfill(2)
    start_period = request.form.get('start_period')
    end_hour = request.form.get('end_hour').zfill(2)
    end_minute = request.form.get('end_minute').zfill(2)
    end_period = request.form.get('end_period')
    operating_hours = f"{start_hour}:{start_minute} {start_period} - {end_hour}:{end_minute} {end_period}"
    care_type = request.form.get('care_type')

    try:
        cur = current_app.config['mysql'].connection.cursor()
        cur.execute("""
            INSERT INTO hospital (name, location, operating_hours, care_type)
            VALUES (%s, %s, %s, %s)
        """, (name, location, operating_hours, care_type))
        current_app.config['mysql'].connection.commit()
        cur.close()
        flash('Hospital added successfully.', 'success')
    except Exception as e:
        flash('An error occurred while adding the hospital.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('admin_routes.manage_hospitals'))

@admin_routes.route('/manage_hospitals/remove', methods=['POST'])
def remove_hospital():
    """Remove a hospital if no appointments are scheduled."""
    hospital_id = request.form.get('hospital_id')

    try:
        cur = current_app.config['mysql'].connection.cursor()

        # Check if the hospital has scheduled appointments
        cur.execute("""
            SELECT COUNT(*) AS appointment_count
            FROM appointment
            WHERE hospital_id = %s AND LOWER(status) = 'scheduled'
        """, (hospital_id,))
        result = cur.fetchone()

        if result['appointment_count'] > 0:
            flash('Cannot remove the hospital because there are scheduled appointments.', 'error')
        else:
            # Remove doctors assigned to the hospital
            cur.execute("DELETE FROM hospital_doctors WHERE hospital_id = %s", (hospital_id,))

            # Remove the hospital
            cur.execute("DELETE FROM hospital WHERE hospital_id = %s", (hospital_id,))
            current_app.config['mysql'].connection.commit()
            flash('Hospital removed successfully.', 'success')

        cur.close()
    except Exception as e:
        flash('An error occurred while removing the hospital.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('admin_routes.manage_hospitals'))

@admin_routes.route('/create_doctor', methods=['POST'])
def create_doctor():
    """Create a new doctor."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.', 'error')
        return redirect(url_for('user_routes.login'))

    first_name = request.form.get('doctor_first_name')
    last_name = request.form.get('doctor_last_name')
    phone = request.form.get('doctor_phone')
    email = request.form.get('doctor_email')
    speciality = request.form.get('speciality')
    username = request.form.get('username')
    password = request.form.get('password')

    if not speciality:
        flash('Speciality is required for doctors.', 'error')
        return redirect(url_for('admin_routes.staff'))

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur = current_app.config['mysql'].connection.cursor()

        # Validate the speciality exists in the `professions` table
        cur.execute("SELECT professions_id FROM professions WHERE professions_id = %s", (speciality,))
        if not cur.fetchone():
            flash('Invalid speciality selected.', 'error')
            return redirect(url_for('admin_routes.staff'))

        # Insert into the `doctor` table
        cur.execute("""
            INSERT INTO doctor (first_name, last_name, speciality, phone, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, speciality, phone, email))
        current_app.config['mysql'].connection.commit()
        doctor_id = cur.lastrowid

        # Insert into the `users` table
        cur.execute("""
            INSERT INTO users (username, password, role, doctor_id)
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_password, 'Doctor', doctor_id))
        current_app.config['mysql'].connection.commit()

        cur.close()
        flash('Doctor created successfully.', 'success')
    except Exception as e:
        flash('An error occurred while creating the doctor.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('admin_routes.staff'))

@admin_routes.route('/create_billing_staff', methods=['POST'])
def create_billing_staff():
    """Create a new billing staff member."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.', 'error')
        return redirect(url_for('user_routes.login'))

    username = request.form.get('username')
    password = request.form.get('password')

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur = current_app.config['mysql'].connection.cursor()

        # Insert into the `users` table
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
        """, (username, hashed_password, 'Billing Staff'))
        current_app.config['mysql'].connection.commit()

        cur.close()
        flash('Billing staff created successfully.', 'success')
    except Exception as e:
        flash('An error occurred while creating the billing staff.', 'error')
        print(f"Error: {e}")

    return redirect(url_for('admin_routes.staff'))

@admin_routes.route('/staff', methods=['GET'])
def staff():
    """Render the Manage Staff page."""
    if 'role' not in session or session['role'] != 'Admin':
        flash('Unauthorized access. Please log in as an admin.', 'error')
        return redirect(url_for('user_routes.login'))

    try:
        cur = current_app.config['mysql'].connection.cursor()
        # Fetch all professions for the speciality dropdown
        cur.execute("SELECT professions_id, type FROM professions")
        professions = cur.fetchall()
        cur.close()
    except Exception as e:
        flash('An error occurred while fetching professions.', 'error')
        print(f"Error: {e}")
        professions = []

    return render_template('admin/staff.html', professions=professions)
