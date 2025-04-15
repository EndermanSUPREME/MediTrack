from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt  # Import bcrypt for password hashing

app = Flask(__name__)

# MySQL connection configuration for XAMPP
app.config['MYSQL_HOST'] = 'localhost'  # XAMPP MySQL runs on localhost
app.config['MYSQL_USER'] = 'root'       # Default XAMPP MySQL username
app.config['MYSQL_PASSWORD'] = ''       # Default XAMPP MySQL password is empty
app.config['MYSQL_DB'] = 'meditrack'    # Replace with your local database name

mysql = MySQL(app)

app.secret_key = '24932781d8d03f8a7ff6fdff8d8780f1'  # Replace with your generated key

def is_valid_bcrypt_hash(hash_str):
    """Validate if the given string is a valid bcrypt hash."""
    return hash_str.startswith('$2b$') and len(hash_str) == 60

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

    return render_template('check.html', patients=patients, users=users)

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
                    return redirect(url_for('dashboard'))
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
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        try:
            # Generate bcrypt hash and validate it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if not hashed_password.startswith('$2b$'):
                raise ValueError("Generated hash is invalid")  # Ensure hash is in bcrypt format

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                        (username, hashed_password, role))
            mysql.connection.commit()
            cur.close()
            flash('User registered successfully!')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during registration: {e}")  # Debugging log
            flash('An error occurred during registration. Please try again.')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))
    return f"Welcome, {session['role']}! This is a placeholder dashboard."

if __name__ == "__main__":
    app.run(debug=True)
