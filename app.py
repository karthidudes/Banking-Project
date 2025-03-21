from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists! Choose another one."

        new_user = User(username=username, password=password, balance=0.0)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Retrieve user from database
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user"] = user.username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password"

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    username = session['user']
    
    # Fetch user from the database
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('login'))

    return render_template("dashboard.html", username=username, balance=user.balance)


@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    username = session['user']
    amount = float(request.form['amount'])

    user = User.query.filter_by(username=username).first()
    if user:
        user.balance += amount
        db.session.commit()
        flash(f"Deposited ₹{amount} successfully!", "success")
    
    return redirect(url_for('dashboard'))


@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    username = session['user']
    amount = float(request.form['amount'])

    user = User.query.filter_by(username=username).first()
    
    if user:
        if amount > user.balance:
            flash("Insufficient balance!", "danger")
        else:
            user.balance -= amount
            db.session.commit()
            flash(f"Withdrawn ₹{amount} successfully!", "success")

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
