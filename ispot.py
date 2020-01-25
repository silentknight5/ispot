from flask import Flask, render_template , flash , request, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField , SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from passlib.hash import sha256_crypt
import yaml
from functools import wraps


app = Flask(__name__)

db = yaml.load(open('data.yaml'))

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/forget')
def forget():
    return render_template('forget.html')

@app.route('/small_computing')
def small_computing():

    blog_type = 'Small_Computing'

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE blog_type = %s",[blog_type])

    blogs = cur.fetchall()

    if result > 0:
        return render_template('main_computing.html', blogs = blogs)
    else:
        flash("No Blog Found",'info')
        return render_template('main_computing.html')

    cur.close()

@app.route('/Software')
def Software():

    blog_type = 'Software'

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE blog_type = %s",[blog_type])

    blogs = cur.fetchall()

    if result > 0:
        return render_template('main_computing.html', blogs = blogs)
    else:
        flash("No Blog Found",'info')
        return render_template('main_computing.html')

    cur.close()

@app.route('/Electronic')
def Electronic():

    blog_type = 'Electronics'

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE blog_type = %s",[blog_type])

    blogs = cur.fetchall()

    if result > 0:
        return render_template('main_computing.html', blogs = blogs)
    else:
        flash("No Blog Found",'info')
        return render_template('main_computing.html')

    cur.close()

@app.route('/Current_Affair')
def Current_Affair():

    blog_type = 'Current_Affair'

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE blog_type = %s",[blog_type])

    blogs = cur.fetchall()

    if result > 0:
        return render_template('main_computing.html', blogs = blogs)
    else:
        flash("No Blog Found",'info')
        return render_template('main_computing.html')

    cur.close()

@app.route('/A.I.')
def a_i():

    blog_type = 'A.I.'

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE blog_type = %s",[blog_type])

    blogs = cur.fetchall()

    if result > 0:
        return render_template('main_computing.html', blogs = blogs)
    else:
        flash("No Blog Found",'info')
        return render_template('main_computing.html')

    cur.close()

@app.route('/privacy-policies')
def privacy():
    return render_template('Privacy_Policy.html')

@app.route('/why_choose_us')
def why_choose():
    return render_template('why_choose.html')

@app.route('/article/<string:id>/')
def article(id):

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE id = %s",[id])

    article = cur.fetchone()

    return render_template('small_computing.html',article = article)

@app.route('/article_search/<string:title>/')
def article_s(title):

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE title = %s",[title])

    article = cur.fetchone()

    if result > 0:

        return render_template('search.html',article = article)

    else:

        flash("No Blog Found",'info')
        return render_template('search.html',article = article)

@app.route('/search/<string:id>', methods = ['POST','GET'])
def search(id):
    if request.method == 'POST':

        search = request.form['search']

        return redirect(url_for('article_s', title = search))

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=100)])
    username =  StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
                validators.DataRequired(),
                validators.EqualTo('confirm', message = 'Password Do Not Match')
    ])
    confirm = PasswordField('Confirm Password', [
                validators.DataRequired(),
                validators.EqualTo('password', message = 'Password Do Not Match')
                ])

@app.route('/register', methods = ['POST','GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #reading Cursor

        cur = mysql.connection.cursor()

        #Check if database exists or not
        cur.execute("CREATE DATABASE IF NOT EXISTS ispot")

        #Check if table exists or not
        cur.execute("CREATE TABLE IF NOT EXISTS users (userid INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL, username VARCHAR(50) NOT NULL, password VARCHAR(100) NOT NULL, reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

        #Check if blog table craete or not
        cur.execute("CREATE TABLE IF NOT EXISTS blogs (blogid INT PRIMARY KEY AUTO_INCREMENT, title VARCHAR(255) NOT NULL, author VARCHAR(100) NOT NULL, body TEXT NOT NULL, blog_type varchar(50) NOT NULL, reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

        find1 = cur.execute("SELECT username FROM users WHERE username=%s",[username])
        find2 = cur.execute("SELECT email FROM users WHERE email=%s",[email])
        if find1 > 0:
            flash('User Already Exists','danger')
            return redirect(url_for('register'))
        elif find2 > 0:
            flash('Email Id Exists','danger')
            return redirect(url_for('register'))
        else:
            cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s, %s, %s, %s)",(name,email,username,password))

        #commit db

        mysql.connection.commit()

        #close connection

        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form = form)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kargs):
        if 'logged_in' in session:
            return f(*args, **kargs)
        else:
            flash('Unauthorized Access, Please Login','danger')
            return redirect(url_for('login'))
    return wrap

class LoginForm(Form):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

@app.route('/login', methods = ['POST','GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password_d = request.form['password']


        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s",[username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_d,password):
                session['logged_in'] = True
                session['username'] = username
                if session['username'] == 'admin':
                    flash('You Are Log In Now','success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('You Are Log In Now','success')
                    return redirect(url_for('main'))
            else:
                flash('''Please Enter The Correct Detail''','warning')
                return render_template('login.html' ,form=form )
        else:
            flash('Invalid Login','warning')
            return render_template('login.html' , form=form)

    return render_template('login.html',form = form )


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("You Are Now Logged Out!",'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    if session['username'] == 'admin':
        # Creating Cursor

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM blogs")

        blogs = cur.fetchall()

        if result > 0:
            return render_template('dashboard.html', blogs = blogs)
        else:
            msg = "No Blog Found"
            return render_template('dashboard.html', msg = msg)
    else:
        flash('Unauthorized Access','danger')
        return redirect(url_for('main'))

    cur.close()

@app.route('/account')
@is_logged_in
def account():
    # Creating Cursor

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE author = %s",[session['username']])

    blogs = cur.fetchall()

    if result > 0:
        return render_template('account.html', blogs = blogs)
    else:
        msg = "No Blog Found"
        return render_template('account.html', msg = msg)

    cur.close()

class ArticleForm(Form):
    choice = [('Electronics','Electronics'),('Software','Software'),('A.I.','A.I.'),('Small_Computing','Small Computing'),('Current_Affair','Current Affair')]
    title = StringField('Name', [validators.Length(min=4, max=200)])
    body =  TextAreaField('Body', [validators.Length(min=40)])
    blog_type = SelectField('Article Type',choices = choice)

@app.route('/add_blog', methods = ['POST','GET'])
@is_logged_in
def add_blog():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        blog_type = form.blog_type.data

        # Create Cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO blogs(title,body,author,blog_type) VALUES(%s, %s, %s, %s)",(title,body,{session['username']},blog_type))

        #commit db

        mysql.connection.commit()

        #close connection

        cur.close()

        if session['username'] == 'admin':
            flash('Article Created Successfully', 'success')

            return redirect(url_for('dashboard'))
        else:
            flash('Article Created Successfully', 'success')

            return redirect(url_for('account'))
    return render_template('add_blog.html', form = form)

@app.route('/edit_blog/<string:id>', methods = ['POST','GET'])
@is_logged_in
def edit_blog(id):

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM blogs WHERE id=%s",[id])

    article = cur.fetchone()

    # Get Form

    form = ArticleForm(request.form)

    # Populate Article From Fields

    form.title.data = article['title']
    form.body.data = article['body']
    # form.blog_type.data = article['blog_type']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        blog_type = request.form['blog_type']

        # Create Cursor
        cur = mysql.connection.cursor()

        cur.execute("UPDATE blogs SET title = %s , blog_type = %s , body = %s WHERE id = %s",(title,blog_type,body,id))

        #commit db

        mysql.connection.commit()

        #close connection

        cur.close()

        if session['username'] == 'admin':
            flash('Article Update Successfully', 'success')

            return redirect(url_for('dashboard'))
        else:
            flash('Article Update Successfully', 'success')

            return redirect(url_for('account'))

    return render_template('edit_blog.html', form = form)

@app.route('/delete_blog/<string:id>', methods = ['POST'])
@is_logged_in
def delete_blog(id):
    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM blogs WHERE id=%s",[id])

    mysql.connection.commit()

    cur.close()

    if session['username'] == 'admin':
        flash('Article Delete Successfully', 'success')

        return redirect(url_for('dashboard'))
    else:
        flash('Article Delete Successfully', 'success')

        return redirect(url_for('account'))

    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.secret_key='S!LENT@KN!GHT'
    app.run(debug = True)
