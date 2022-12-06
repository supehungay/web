from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
app = Flask(__name__)

app.secret_key = 'your secret key'
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'quanlykhachsan'

mysql = MySQL(app)


@app.route('/')
@app.route('/home', methods=['GET'])
def home():

     # username = 'Anonymous'
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        session.permanent = True
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM taikhoan WHERE email = % s ', (email,))
        account = cursor.fetchone()
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['account_id']
            session['username'] = account['user_name']
            session['password'] = account['password']
            session['email'] = account['email']
            session['role_id'] = account['role_id']
            session['fullname'] = account['name']
            msg = 'Logged in successfully !'
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg, title='Login Page')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('home'))


@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    if request.method == 'post' and 'selection' in request.form:
        selection = request.form['selection']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM {selection}')
        data = cursor.fetchall()
        return render_template('dashboard.html',data=data, title=selection)
    return render_template('user.html', msg='Cannot access admin')
@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    
    return render_template('admin.html', title = 'Admin page')
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']
        birthday = request.form['birthday']
        phone = request.form['phone_number']
        fullname = request.form['fullname']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM taikhoan WHERE email = % s', (email, ))
        account = cursor.fetchall()
        if account:
            msg = 'Email already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        elif not (repassword == password):
            msg = 'Invalid password, please try again'
        else:
            password_hash = generate_password_hash(password)
            cursor.execute('INSERT INTO taikhoan VALUES (NULL,%s,%s, %s, %s,%s, %s, 2, 0)', (fullname, phone, email, birthday, username, password_hash, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('register', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/profile', methods=['GET'])
def profile():
    id_account = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'select * from taikhoan where taikhoan.account_id = % s;', (id_account,))
    info = cursor.fetchone()
    mysql.connection.commit()
    return render_template('profile.html', info=info, title='Profile Page')


@app.route('/resetpass', methods=['GET', 'POST'])
def resetpass():
    msg = ''
    if request.method == 'POST' and 'password' in request.form:
        new_password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE taikhoan SET `password` = % s where `email` = % s;', 
                    (generate_password_hash(new_password), email, ))
        msg = 'You have changed password successfully'
        mysql.connection.commit()
        return render_template('login')
    return render_template('reset_password.html', msg=msg, title='Reset Password Page')


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    account_id = session['id']

    if request.method == 'POST' and 'fullname' in request.form and 'identify' in request.form and 'gender' in request.form and 'address' in request.form:
        username = request.form['username']
        name = request.form['fullname']
        identify = request.form['identify']
        gender = request.form['gender']
        address = request.form['address']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DicCursor)
        cursor.execute('select * from khachhang where account_id = % s', (account_id, ))
        data = cursor.fetchall
        if data:
            cursor.execute('UPDATE TABLE khachhang SET customer_name = %s, ')
        msg = 'Update profile successfully'
        mysql.connection.commit()
        return redirect(url_for('user'))
    else: 
        msg = 'Update profile unsuccessfully'

    return render_template('edit_profile.html', msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
