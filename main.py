import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import AnonymousUserMixin, LoginManager, login_user, current_user, login_required, logout_user, \
    UserMixin
from flask_sqlalchemy import SQLAlchemy

import forms

app = Flask(__name__)


class MyAnonymousUserMixin(AnonymousUserMixin):
    is_admin = False


login_manager = LoginManager(app)

login_manager.login_view = 'sign_in'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'
login_manager.anonymous_user = MyAnonymousUserMixin

admin = Admin(app)

bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite?check_same_thread=False')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '(/("ZOHDAJK)()kafau029)ÖÄ:ÄÖ:"OI§)"Z$()&"()!§(=")/$'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Integer, nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class MyTable(db.Model):
    __tablename__ = 'my_table'
    id = db.Column(db.Integer, primary_key=True)
    my_column = db.Column(db.String(100), nullable=False)


class Books(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User")
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    author = db.relationship("Author")
    review = db.relationship('Review', backref='books')

    def __repr__(self):
        return f'<Books {self.book_name}>'


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("review.id"))
    review = db.relationship("Review")


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    books_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book_name = db.relationship("Books")


    def __repr__(self):
        return f'<Review "{self.content[:20]}...">'


db.create_all()


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(MyTable, db.session))


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = forms.AddNewReviewForm()
    try:
        reviews = Review.query.all()
    except:
        reviews = []
    return render_template('home.html', reviews=reviews, form=form)


# @app.route('/available_books', methods=['POST', 'GET'])
# @login_required
# def available_books():
#     try:
#         all_books = Books.query.all()
#     except:
#         all_books = []
#     return render_template("available_books.html", all_books=all_books)


@app.route('/edit_category', methods=['POST', 'GET'])
@login_required
def available_books():
    try:
        all_books = Books.query.all()
    except:
        all_books = []
    return render_template("edit_category.html", all_books=all_books)


@app.route('/my_books', methods=['POST', 'GET'])
@login_required
def my_books():
    try:
        my_books = Books.query.all()
    except:
        my_books = []
    return render_template("my_books.html", my_books=my_books)


@app.route('/borrow/<int:id>')
@login_required
def borrow(id):
    books = Books.query.get(id)
    books.user_id = current_user.id
    db.session.commit()
    return redirect(url_for('available_books'))


@app.route('/return/<int:id>')
@login_required
def return_book(id):
    books = Books.query.get(id)
    books.user_id = None
    db.session.commit()
    return redirect(url_for('my_books'))


@app.route('/read_review')
@login_required
def read_review():
    try:
        reviews = Review.query.all()
    except:
        reviews = []
    return render_template("read_review.html", reviews=reviews)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode()
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {current_user.first_name}', 'success')
        return redirect(url_for('home'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome, {current_user.first_name}', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash(f'User or password does not match', 'danger')
        return render_template('sign_in.html', form=form)
    return render_template('sign_in.html', form=form)


@app.route('/update_account_information', methods=['GET', 'POST'])
def update_account_information():
    form = forms.UpdateAccountInformationForm()
    if request.method == 'GET':
        form.email_address.data = current_user.email_address
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    if form.validate_on_submit():
        current_user.email_address = form.email_address.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('User information updated', 'success')
        return redirect(url_for('update_account_information'))
    return render_template('update_account_information.html', form=form)


@app.route('/add_new_book', methods=['GET', 'POST'])
def add_new_book():
    form = forms.AddNewBookForm()
    if form.validate_on_submit():
        add_new_book = Books(book_name=form.book_name.data)
        db.session.add(add_new_book)
        db.session.commit()
        flash('Success, new category added')
        return redirect(url_for('add_new_book'))
    return render_template('add_new_book.html', form=form)


@app.route('/sign_out')
def sign_out():
    logout_user()
    flash('Goodbye, see you next time', 'success')
    return redirect(url_for('home'))


@app.route("/review", methods=['GET', 'POST'])
@login_required
def review():
    form = forms.AddNewReviewForm()
    if form.validate_on_submit():
        review = Review(books_id=form.book_name.data.id, content=form.content.data, user_id=current_user.id)
        db.session.add(review)
        db.session.commit()
        flash('Success, new review added')
        return redirect(url_for('review'))
    return render_template('add_new_review.html', form=form)


@app.route('/read_review/delete/<int:id>')
@login_required
def delete_review(id):
    review_to_delete = Review.query.get_or_404(id)
    try:
        db.session.delete(review_to_delete)
        db.session.commit()
        flash("Note Was Deleted!")
        review = Review.query.order_by(Review.date_posted)
        return render_template("read_review.html", review=review)
    except:
        flash("Whoops! There was a problem deleting note, try again...")
        review = Review.query.order_by(Review.date_posted)
        return render_template("read_review.html", review=review)


@app.route('/review/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    review = Review.query.get_or_404(id)
    form = forms.AddNewReviewForm()
    if form.validate_on_submit():
        review.book_name = form.book_name.data
        review.content = form.content.data
        db.session.add(review)
        db.session.commit()
        flash("Note Has Been Updated!")
        return redirect(url_for('read_review', id=review.id))

    else:
        form.book_name.data = review.books_id
        form.content.data = review.content
        return render_template('edit_review.html', form=form)


    # review = Review.query.get_or_404(id)
    # form = forms.AddNewReviewForm()
    # if request.method == 'GET':
    #     form.book_name.data = review.books_id
    #     form.content.data = review.content
    # if form.validate_on_submit():
    #     review.book_name = form.book_name.data
    #     review.content = form.content.data
    #     db.session.add(review)
    #     db.session.commit()
    #     flash('Note information updated', 'success')
    # return render_template('edit_review.html', form=form)


@app.route('/<int:books_id>/')
def book(books_id):
    book = Books.query.get_or_404(books_id)
    return render_template('book.html', books=book)


if __name__ == '__main__':
    app.run(debug=True)
