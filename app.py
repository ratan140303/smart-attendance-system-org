from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'Bablu@12345'


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(100))

  def __init__(self, email, password, name):
    self.name = name
    self.email = email
    self.password = self.hash_password(password)

  def hash_password(self, password):
    return bcrypt.hashpw(password.encode('utf-8'),
                         bcrypt.gensalt()).decode('utf-8')

  def check_password(self, password):
    return bcrypt.checkpw(password.encode('utf-8'),
                          self.password.encode('utf-8'))


with app.app_context():
  db.create_all()


class Contactus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(100), nullable=False)
  message = db.Column(db.String(200))

  def __init__(self, name, email, message):
    self.name = name
    self.email = email
    self.message = message


with app.app_context():
  db.create_all()


@app.route('/')
def index():
  return render_template('home.html', active_page='home')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
      flash('Email already exists. Please use different email.', 'error')
      return redirect(
          '/register')  # Redirect back to registration page with flash message

    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash('Registration successful. Please log in.', 'success')
    return redirect('/register')

  return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
      session['email'] = user.email
      return redirect('/dashboard')
    else:
      error = 'Invalid email or password. Please try again.'
      flash(error, 'error')

  return render_template('login.html')


@app.route('/dashboard')
def dashboard():
  if 'email' in session:
    user = User.query.filter_by(email=session['email']).first()
    return render_template('dashboard.html',
                           active_page='dashboard',
                           user=user)
  else:
    flash('You need to login first.', 'error')
    return redirect('/login')


@app.route('/logout')
def logout():
  session.pop('email', None)
  flash('You have been logged out.', 'info')
  return redirect('/login')


@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    new_contact = Contactus(name=name, email=email, message=message)
    db.session.add(new_contact)
    db.session.commit()
    flash('Message Sent Successfully.', 'success')
    return redirect('/contactus')

  return render_template('contactus.html', active_page='contactus')


@app.route('/about')
def about():
  return render_template('about.html', active_page='about')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
