from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__,static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    university = db.Column(db.String(100), nullable=False)  # New field
    branch = db.Column(db.String(50), nullable=False)       # New field
    year = db.Column(db.String(10), nullable=False)         # New field

    def __init__(self, email, password, name, university, branch, year):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.university = university
        self.branch = branch
        self.year = year

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Exagram</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
        <style>
            /* Full-width GIF background */
            .gif-background {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1; /* Set behind other content */
                object-fit: cover; /* Cover entire area */
            }

            /* Center button over the GIF */
            .content {
                position: relative;
                z-index: 1; /* Bring content in front */
                text-align: center;
                color: white; /* White text for contrast */
                margin-top: 50%; /* Center the button vertically */
                transform: translateY(-50%); /* Adjust for perfect centering */
            }

            /* Button Styles */
            .get-started-btn {
                background-color: rgba(0, 123, 255, 0.8); /* Slightly transparent blue */
                border: none;
                padding: 15px 30px; /* Increased padding for a larger button */
                font-size: 18px; /* Larger font size */
            }
        </style>
    </head>
    <body>
        <!-- GIF Background -->
        <img src="{{ url_for('static', filename='EXAGRAM.gif') }}" alt="EXAGRAM Background" class="gif-background">

        <!-- Content Overlay -->
        <div class="container content">
            <a href="/register" class="btn get-started-btn">Get Started</a>
        </div>
    </body>
    </html>
    '''




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        university = request.form['university']
        branch = request.form['branch']
        year = request.form['year']

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error="Email already registered. Please use a different email.")

        # If email is not registered, create a new user
        new_user = User(name=name, email=email, password=password, university=university, branch=branch, year=year)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            session['name'] = user.name
            session['email'] = user.email
            session['university'] = user.university  # Store university in session
            session['branch'] = user.branch          # Store branch in session
            session['year'] = user.year              # Store year in session
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'name' in session:
        return render_template('dashboard.html', 
                               name=session['name'],
                               university=session['university'],
                               branch=session['branch'],
                               year=session['year'])
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect('/login')  # Redirect to the login page after logout


@app.route('/exabuddy')
def exabuddy():
    session.clear()  # Clear session data
    return redirect('/login') 

if __name__ == '__main__':
    app.run(debug=True)
