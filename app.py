from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from time import sleep

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
app.config['SECRET_KEY'] = '!secret!'
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Initialize CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:4000"}})

# UserModel
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        
        login_user = User.query.filter_by(username=uname, password=passw).first()
        if login_user is not None:
            session['username'] = uname  # Store username in session
            session['email'] = login_user.email  # Store email in session
            return redirect(url_for("home"))
        else:
            flash('Invalid username or password', 'error')
    return render_template("login.html")

# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        new_user = User(username=uname, email=mail, password=passw)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")

# Welcome page
@app.route("/home")
def home():
    if 'username' in session:
        username = session['username']
        email = session['email']
        return render_template("home.html", username=username, email=email)
    else:
        return redirect(url_for("login"))

# WebSocket
@socketio.on('message')
def handle_message(message):
    for i in range(1, 6):
        sleep(1)
        emit('notification', f'your message : {message} {i}', broadcast=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
