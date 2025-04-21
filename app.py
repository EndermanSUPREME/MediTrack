from flask import Flask, render_template, url_for, session, redirect, flash, request
from flask_mysqldb import MySQL, MySQLdb  # Import MySQLdb for DictCursor
from user_routes import user_routes  # Import the user_routes blueprint
from doctor_routes import doctor_routes  # Import the doctor_routes blueprint
from patient_routes import patient_routes  # Import the patient_routes blueprint
from insurance_routes import insurance_routes  # Import the insurance_routes blueprint
from billing_routes import billing_routes  # Import the billing_routes blueprint
from admin_routes import admin_routes  # Import the admin_routes blueprint
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL connection configuration for XAMPP
app.config['MYSQL_HOST'] = '10.37.1.103'
app.config['MYSQL_USER'] = 'yoyojesus'
app.config['MYSQL_PASSWORD'] = 'veryOkIrTIcA'
app.config['MYSQL_DB'] = 'meditrack'

mysql = MySQL(app)
app.config['mysql'] = mysql

# Enable DictCursor for all queries
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

user_routes.mysql = mysql

app.secret_key = '24932781d8d03f8a7ff6fdff8d8780f1'

# Register the blueprints
app.register_blueprint(user_routes, url_prefix='/user')
app.register_blueprint(doctor_routes)
app.register_blueprint(patient_routes)
app.register_blueprint(insurance_routes, url_prefix='/insurance')  # Ensure the prefix is set to '/insurance'
app.register_blueprint(billing_routes)
app.register_blueprint(admin_routes, url_prefix='/admin')  # Ensure admin_routes uses the /admin prefix

@app.template_filter('format_time_12_hour')
def format_time_12_hour(value):
    """Convert time from 24-hour format (HH:MM:SS) or timedelta to 12-hour format (h:mm AM/PM)."""
    try:
        if isinstance(value, timedelta):
            # Convert timedelta to string in HH:MM:SS format
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            value = f"{hours:02}:{minutes:02}:00"
        time_obj = datetime.strptime(value, '%H:%M:%S')
        return time_obj.strftime('%I:%M %p')
    except (ValueError, TypeError):
        return value

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

if __name__ == "__main__":
    app.run(debug=True)
