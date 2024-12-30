# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from mysql.connector import connect, Error
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    connection = connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return connection

@app.route('/')
def home():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM courses')
    courses = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('home.html', courses=courses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                       (username, email, password))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('login'))
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('profile.html', user=user)

@app.route('/course/<int:course_id>')
def course(course_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM courses WHERE id = %s', (course_id,))
    course = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('course.html', course=course)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle contact form submission (e.g., send email or store in database)
        flash('Thank you for contacting us!', 'success')
        return redirect(url_for('home'))
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
