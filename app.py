from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import json

app = Flask(__name__)
app.secret_key = "foodoraa"


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # DONATIONS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food TEXT,
        quantity TEXT,
        serves TEXT,
        location TEXT
    )
    """)

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # DELIVERY TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS deliveries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food TEXT,
        volunteer TEXT,
        location TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users(username, password) VALUES (?,?)",
                        (username, password))
            conn.commit()
            flash("Signup Successful! Please Login")
            return redirect('/login')

        except:
            flash("User already exists!")

        conn.close()

    return render_template('signup.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (username, password))

        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/')
        else:
            flash("Invalid Credentials")

    return render_template('login.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- DONATE ----------------
@app.route('/donate', methods=['GET', 'POST'])
def donate():

    if request.method == 'POST':

        food = request.form['food']
        quantity = request.form['quantity']
        serves = request.form['serves']
        location = request.form['location']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO donations(food, quantity, serves, location)
        VALUES (?, ?, ?, ?)
        """, (food, quantity, serves, location))

        conn.commit()
        conn.close()

        flash("Donation Added Successfully!")

        return redirect('/')

    return render_template('donate.html')


# ---------------- VOLUNTEER ----------------
@app.route('/volunteer')
def volunteer():

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations")
    data = cur.fetchall()

    conn.close()

    return render_template('volunteer.html', data=data)


# ---------------- ACCEPT DELIVERY ----------------
@app.route('/accept/<food>/<location>')
def accept(food, location):

    volunteer = session.get('user', 'guest')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO deliveries(food, volunteer, location, status)
    VALUES (?, ?, ?, ?)
    """, (food, volunteer, location, "Accepted"))

    conn.commit()
    conn.close()

    flash("Delivery Accepted!")

    return redirect('/volunteer')


# ---------------- ADMIN ----------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':

        password = request.form['password']

        if password == "1234":
            session['admin'] = True
            return redirect('/dashboard')
        else:
            flash("Wrong Password")

    return render_template('admin_login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # donations
    cur.execute("SELECT * FROM donations")
    data = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM donations")
    total = cur.fetchone()[0]

    # deliveries
    cur.execute("SELECT * FROM deliveries")
    deliveries = cur.fetchall()

    conn.close()

    # chart data
    chart_labels = [i[1] for i in data]
    chart_values = [1 for i in data]

    return render_template(
        'dashboard.html',
        data=data,
        total=total,
        deliveries=deliveries,
        chart_labels=json.dumps(chart_labels),
        chart_values=json.dumps(chart_values)
    )


# ---------------- ABOUT ----------------
@app.route('/about')
def about():
    return render_template('about.html')


# ---------------- SAVINGS ----------------
@app.route('/savings')
def savings():
    return render_template('savings.html')


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)