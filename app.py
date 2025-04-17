from flask import Flask, render_template, url_for, session, redirect, flash, request
from flask_mysqldb import MySQL
from user_routes import user_routes  # Import the user_routes blueprint
from dashboard_routes import dashboard_routes  # Import the dashboard_routes blueprint

app = Flask(__name__)

# MySQL connection configuration for XAMPP
app.config['MYSQL_HOST'] = '10.37.1.103'
app.config['MYSQL_USER'] = 'yoyojesus'
app.config['MYSQL_PASSWORD'] = 'veryOkIrTIcA'
app.config['MYSQL_DB'] = 'meditrack'

mysql = MySQL(app)
app.config['mysql'] = mysql  # Add mysql to app config
user_routes.mysql = mysql  # Pass MySQL instance to user_routes

app.secret_key = '24932781d8d03f8a7ff6fdff8d8780f1'

# Register the blueprints
app.register_blueprint(user_routes, url_prefix='/user')  # Ensure the prefix is '/user'
app.register_blueprint(dashboard_routes, url_prefix='/dashboard')  # Ensure the prefix is '/dashboard'

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
