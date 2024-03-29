from flask import Flask, render_template, flash, request, redirect, url_for
from models import UsersModel, db, PostModel
from forms import UserForm, PasswordForm, PostForm, LoginForm, RegisterForm, SearchForm
from secret_staff import SECRET_STAFF
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, LoginManager, login_user, logout_user
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid
import os

app = Flask(__name__, template_folder='templates')  # static_folder='static')
ckeditor = CKEditor(app)

# Create a Secret Key
app.config["SECRET_KEY"] = "mySecretKey"

UPLOAD_FOLDER = 'static/imgs/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Sqlite DB
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# My SqlDB
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://username:password@localhost/database_name"
app.config["SQLALCHEMY_DATABASE_URI"] = SECRET_STAFF

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)

migrate = Migrate(app, db)


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 35:
        return render_template('admin.html')
    else:
        flash("You are not the admin to make this page!!")
        return redirect(url_for('all_posts'))


@login_manager.user_loader
def load_user(user_id):
    return UsersModel.query.get(user_id)


@app.route('/add-post', methods=['POST', 'GET'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = PostModel(
            title=form.title.data,
            content=form.content.data,
            poster_id=poster,
            slug=form.slug.data)

        db.session.add(post)
        db.session.commit()

        flash("The post submitted successfully!")
        return redirect('all_posts')

    form.title.data = ''
    form.content.data = ''
    # form.author.data = ''
    form.slug.data = ''

    return render_template('add_post.html', form=form)


@app.route('/update-post/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_post(id):
    post_to_edit = PostModel.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post_to_edit.title = form.title.data
        # post_to_edit.author = form.author.data
        post_to_edit.slug = form.slug.data
        post_to_edit.content = form.content.data

        db.session.add(post_to_edit)
        db.session.commit()
        flash("The post updated successfully!")
        return redirect(url_for("post_details", id=post_to_edit.id))

    form.title.data = post_to_edit.title
    # form.author.data = post_to_edit.author
    form.slug.data = post_to_edit.slug
    form.content.data = post_to_edit.content

    return render_template('edit_post.html', form=form, post_to_edit=post_to_edit)


@app.route('/delete/<int:id>/', methods=['GET', 'POST'])
def delete_post(id):
    post_to_delete = PostModel.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post deleted successfully")
        return redirect(url_for('all_posts'))
    except:
        flash("Error user")

    return redirect(url_for('all_posts'))


@app.route('/user/add', methods=["Post", "Get"])
def add_user():
    name = None
    form = UserForm()

    if form.validate_on_submit():
        user = UsersModel.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password, and it's very important to remove the hashing algorithm "pbkdf2:sha256"
            hashed_pass = generate_password_hash(form.password_hash.data)

            # put data into database
            user = UsersModel(name=form.name.data,
                              username=form.username.data,
                              email=form.email.data,
                              password_hash=hashed_pass)
            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        # form.hashed_pass.data = ''
        flash("User added")

    all_users = UsersModel.query.order_by(UsersModel.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           all_users=all_users)


@app.route('/')
def all_users():
    get_users = UsersModel.query.all()
    return render_template("index.html", all_users=get_users)


@app.route('/all_posts')
def all_posts():
    get_posts = PostModel.query.all()
    return render_template("all_posts.html", get_posts=get_posts)


@app.route('/post_detail/<int:id>', methods=['POST', 'GET'])
def post_details(id):
    post_to_see = db.session.get(PostModel, id)
    return render_template('post_details.html', post_to_see=post_to_see)


@app.route('/user/<name>/')
def user(name):
    name = name
    return render_template("user.html", name=name)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("The form submitted successfully!", "info")

    return render_template('name.html', name=name, form=form)


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update_user(id):
    form = UserForm(request.form)
    user_to_update = UsersModel.query.get_or_404(id)

    if request.method == 'POST':
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.username = request.form['username']
        user_to_update.about_me = request.form['about_me']
        # user_to_update.password = request.form['password']

        if 'profile_img' in request.files:
            file = request.files['profile_img']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user_to_update.profile_img = filename

        try:
            db.session.commit()
            flash("User updated successfully!")
            return redirect(url_for('dashboard'))
        except:
            flash("Error updating user")
            return render_template("update_user.html",
                                   form=form,
                                   id=id,
                                   user_to_update=user_to_update)
    else:
        form.name.data = user_to_update.name
        form.email.data = user_to_update.email
        form.username.data = user_to_update.username
        form.about_me.data = user_to_update.about_me
        # form.password_hash.data = user_to_update.password
        return render_template("update_user.html",
                               form=form,
                               id=id,
                               user_to_update=user_to_update)

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    if id == current_user.id:
        user_to_delete = UsersModel.query.get_or_404(id)
        name = None
        our_users = None
        form = UserForm()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully!!")

            our_users = UsersModel.query.order_by(UsersModel.date_added)
            return render_template("add_user.html",
                                   form=form,
                                   name=name,
                                   our_users=our_users)

        except:
            flash("Whoops! There was a problem deleting user, try again...")
            return render_template("add_user.html",
                                   form=form, name=name, our_users=our_users)
    else:
        flash("Sorry, you can't delete that user! ")
        return redirect(url_for('dashboard'))


# Password Test
@app.route('/test_pass', methods=['GET', 'POST'])
def test_password():
    email = None
    password = None
    password_to_check = None
    passed = None
    form = PasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ''
        form.password_hash.data = ''

        password_to_check = UsersModel.query.filter_by(email=email).first()
        passed = check_password_hash(password_to_check.password_hash, password)
        flash("The hash is correct!", "info")

        print(f"password_to_check {password_to_check.password_hash}")
        print(f"password {password}")

    return render_template('test_password.html',
                           form=form,
                           email=email,
                           password=password,
                           password_to_check=password_to_check,
                           passed=passed
                           )


login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return UsersModel.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UsersModel.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")

    return render_template('members/login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    current_user_info = UsersModel.query.get(current_user.id)
    about_author = current_user_info.about_me
    return render_template('members/dashboard.html', about_author=about_author)


# pass any variable to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search_for', methods=["POST"])
def search_for():
    form = SearchForm()
    posts = PostModel.query

    if form.validate_on_submit():
        post_searched = form.searched.data
        posts = posts.filter(PostModel.title.like("%" + post_searched + "%"))
        posts = posts.order_by(PostModel.title).all()

        return render_template('search.html',
                               form=form,
                               searched=post_searched,
                               posts=posts)
