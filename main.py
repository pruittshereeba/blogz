from flask import Flask, request, redirect, render_template, session, flash

from flask_sqlalchemy import SQLAlchemy
import hashlib
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:buildingblogz1@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'BeTrue2You'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'users', 'page', 'blog_page']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']


        password_hash = hashlib.sha256(str.encode(password)).hexdigest()

        user = User.query.filter_by(username=email).first()

        if user and user.password == password_hash:
            session['email'] = email
            flash("Logged in")
            return render_template('newpost.html')
        elif user and user.password != password_hash:
            flash('User password incorrect', 'error')
            return render_template('login.html')
        else:
            flash('User does not exist, please signup', 'error')
            return render_template('signup.html')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        password_hash = hashlib.sha256(str.encode(password)).hexdigest()
        verify = request.form['verify']

        if len(email) < 3:
            flash('password must be at least 3 characters', 'error')
            return render_template('signup.html')
        if len(password) < 3:
            flash('password must be at least 3 characters', 'error')
            return render_template('signup.html')
        if password != verify:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')

        existing_user = User.query.filter_by(username=email).first()
        if not existing_user:
            new_user = User(email, password_hash)
            db.session.add(new_user)
            db.session.commit()

            session['email'] = email
            return redirect('/')
        else:
            flash('User already exist', 'error')
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    flash('You have successfully logged out')
    return redirect('/')

@app.route('/allblogs', methods=['POST', 'GET'])
def blog_page():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['entry']

        owner_id = User.query.filter_by(username=session['email']).first()

        new_blog = Blog(blog_title, blog_entry, owner_id)
        db.session.add(new_blog)
        db.session.commit()

    users = User.query.all()
    blogs = Blog.query.all()
    return render_template('blog.html', page_title="Welcome to Blogz", blogs=blogs, users=users)


@app.route('/newpost.html', methods=['POST', 'GET'])
def go_to_entry():
    return render_template('newpost.html', page_title="Build a Blog")



@app.route('/page', methods=['GET'])
def page():

    blog_id = request.args.get('id')
    entry = Blog.query.get(blog_id)
    users = User.query.all()
    return render_template('page.html', page_title=blog.title, entry=blog.body, user=users )


@app.route('/enter-data', methods=['POST', 'GET'])
def entry():

    owner_id = User.query.filter_by(username=session['email']).first()

    if request.method == 'POST':
        title = request.form['title']
        entry = request.form['entry']

        if title == '' or entry == '':
            return render_template('newpost.html', title=title, entry=entry, page_title="Build a Blog", owner_id=owner_id)


        new_blog = Blog(title, entry, owner_id)
        db.session.add(new_blog)
        db.session.commit()

    users = User.query.all()
    return render_template('page.html', entry=entry, page_title=title, owner_id=owner_id)  

@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', users=users)

if  __name__ == "__main__":
    app.run()
