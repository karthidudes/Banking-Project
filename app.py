import os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"

USER_FILE = "users.txt"

# Function to save user data
def save_user(username, password, balance):
    with open(USER_FILE, "a") as file:
        file.write(f"{username},{password},{balance}\n")

# Function to read users from the file
def get_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            for line in file:
                username, password, balance = line.strip().split(",")
                users[username] = {"password": password, "balance": float(balance)}
    return users

# Function to update user balance
def update_balance(username, new_balance):
    users = get_users()
    if username in users:
        users[username]['balance'] = new_balance

        with open(USER_FILE, "w") as file:
            for user, data in users.items():
                file.write(f"{user},{data['password']},{data['balance']}\n")

# Function to validate login credentials
def validate_user(username, password):
    users = get_users()
    return username in users and users[username]['password'] == password

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        balance = 0.0  

        new_user = User(username=username, password=password, balance=balance)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if validate_user(username, password):
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials! Try again.", "danger")

    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    username = session['user']
    users = get_users()
    balance = users[username]['balance']
    
    return render_template("dashboard.html", username=username, balance=balance)

@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    username = session['user']
    amount = float(request.form['amount'])

    users = get_users()
    new_balance = users[username]['balance'] + amount
    update_balance(username, new_balance)

    flash(f"Deposited ₹{amount} successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    username = session['user']
    amount = float(request.form['amount'])

    users = get_users()
    
    if amount > users[username]['balance']:
        flash("Insufficient balance!", "danger")
    else:
        new_balance = users[username]['balance'] - amount
        update_balance(username, new_balance)
        flash(f"Withdrawn ₹{amount} successfully!", "success")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
