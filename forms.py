from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_login import current_user
import main


def review_query():
    return main.Review.query.all()


def author_query():
    return main.Author.query.all()


def books_query():
    return main.Books.query.all()


class AddNewBookForm(FlaskForm):
    book_name = StringField('Category name', [DataRequired()])
    submit = SubmitField('Add New Category')

    def validate_book_name(self, book_name):
        books = main.Books.query.filter_by(book_name=self.book_name.data).first()
        if books:
            raise ValidationError('Book exists. Add another one, please.')


class AddNewReviewForm(FlaskForm):
    book_name = QuerySelectField(query_factory=books_query, allow_blank=True, get_label="book_name",
                                 get_pk=lambda obj: str(obj))
    content = StringField('Note text', [DataRequired()])
    submit = SubmitField('Submit')


class SignUpForm(FlaskForm):
    email_address = StringField('Email Address', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name')
    password1 = PasswordField('Password', [DataRequired()])
    password2 = PasswordField('Password confirm', [DataRequired(), EqualTo('password1', 'Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_email_address(self, email_address):
        user = main.User.query.filter_by(email_address=self.email_address.data).first()
        if user:
            raise ValidationError('Email already exists. Sign in or use another email address.')


class SignInForm(FlaskForm):
    email_address = StringField('Email Address', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Sign In')


class UpdateAccountInformationForm(FlaskForm):
    email_address = StringField('Email Address', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name')
    submit = SubmitField('Update Info')

    def validate_email_address(self, email_address):
        if current_user.email_address != self.email_address.data:
            user = main.User.query.filter_by(email_address=self.email_address.data).first()
            if user:
                raise ValidationError('Email already exists. Sign in or use another email address.')