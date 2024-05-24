from flask import Flask, render_template, redirect, url_for, session, flash,request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL
import requests

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'arbaj_2004'
app.config['MYSQL_DB'] = 'preptracker'
app.secret_key = 'hi i am secreat'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    username = StringField("Username",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self,field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM credentials where email=%s",(field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    # email = StringField("Email",validators=[DataRequired(), Email()])
    email_or_username = StringField("Email or Username", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        name = form.name.data
        email = form.email.data
        password = form.password.data
        
        # Check the API to see if the username exists
        api_url = f'https://alfa-leetcode-api.onrender.com/{username}'
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                api_data = response.json()
                if 'errors' in api_data:
                    # Username does not exist according to the API
                    flash("Username does not exist. Please check your username.")
                    return render_template('register.html', form=form, error="Username does not exist.")
                else:
                    # Proceed with registration as the username does not exist in the API
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                    # Store data into the database
                    cursor = mysql.connection.cursor()
                    cursor.execute("INSERT INTO credentials (name, username, email, password) VALUES (%s, %s, %s, %s)",
                                   (name, username, email, hashed_password))
                    mysql.connection.commit()
                    cursor.close()

                    return redirect(url_for('login'))
            else:
                return render_template('register.html', form=form, error="API error: Could not verify username.")
        except requests.RequestException as e:
            return render_template('register.html', form=form, error=f"API request failed: {str(e)}")

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_or_username = form.email_or_username.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM credentials WHERE email=%s OR username=%s", (email_or_username, email_or_username))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
            session['userId'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email (or username) and password")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'userId' in session:
        userId = session['userId']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM credentials where userId=%s",(userId,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return render_template('dashboard.html',user=user)
            
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('userId', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)


    # dreamyjpl 1234
