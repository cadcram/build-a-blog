from flask import Flask, request, redirect, render_template, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    pub_date = db.Column(db.DateTime)
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, pub_date, owner_id):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.owner_id = owner_id
    
    def __repr__(self):
        return '<Post %r>' % self.title

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Post %r>' % self.email

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = user.email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')
        
    return render_template('login.html', session=False)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/register')
        # TODO 1: validate that form value of 'verify' matches password
        if matches(email, verify) == True:
            flash('Uh-Oh! Your password and password verification do not match')
            return redirect('/register')
        # TODO 2: validate that there is no user with that email already
        if unique_user(email) == False:
            flash('Uh-Oh! That E-Mail login already exists!')
            return redirect('/register')

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = user.email
        return redirect("/blog")
    else:
        return render_template('register.html')

def unique_user(email):
    if User.query.filter_by(email=email).first():
        return False
    else:
        return True

def matches(email, verify):
    email = email
    verify = verify
    if email == verify:
        return True
    else:
        return False

def is_email(string):
    # for our purposes, an email string has an '@' followed by a '.'
    # there is an embedded language called 'regular expression' that would crunch this implementation down
    # to a one-liner, but we'll keep it simple:
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present
@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/')
def index():
    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(owner=owner).order_by(Blog.pub_date.desc()).all()

    return render_template('blog.html', title="Build-a-Blog!", blogs=blogs)
    

@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':

        title = request.form['title']
        pub_date = datetime.utcnow()
        body = request.form['blog']
        user = User.query.filter_by(email=session['email']).first()
        owner_id = user.id
        new_blog = Blog(title=title, body=body, pub_date=pub_date, owner_id=owner_id)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/single?id=' + str(new_blog.id))


    return render_template('new-post.html')

@app.route('/single', methods=['POST', 'GET'])
def single_blog():
    id = request.args.get('id')
    blog = Blog.query.get(id)
    return render_template('single.html', blog=blog)

if __name__ == '__main__':
    app.run()