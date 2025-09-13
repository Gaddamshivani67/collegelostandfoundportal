from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lostfound.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -------------------- MODELS --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rollno = db.Column(db.String(50), unique=True)
    branch = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String(50))   # Lost or Found
    item_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    student_name = db.Column(db.String(100))
    rollno = db.Column(db.String(50))
    branch = db.Column(db.String(50))

# -------------------- LOGIN MANAGER --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- ROUTES --------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        rollno = request.form["rollno"]
        branch = request.form["branch"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"], method='pbkdf2:sha256')

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("signup"))

        new_user = User(name=name, rollno=rollno, branch=branch, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/post_item", methods=["GET", "POST"])
@login_required
def post_item():
    if request.method == "POST":
        item_type = request.form["item_type"]
        item_name = request.form["item_name"]
        description = request.form["description"]

        new_item = Item(item_type=item_type, item_name=item_name, description=description,
                        student_name=current_user.name, rollno=current_user.rollno, branch=current_user.branch)

        db.session.add(new_item)
        db.session.commit()
        flash("Item posted successfully!", "success")
        return redirect(url_for("view_items"))

    return render_template("post_item.html")

@app.route("/view_items")
def view_items():
    items = Item.query.all()
    return render_template("view_items.html", items=items)

# -------------------- MAIN --------------------
if __name__ == "__main__":
    if not os.path.exists("lostfound.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)

