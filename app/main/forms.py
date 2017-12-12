from flask_wtf import FlaskForm
from wtforms import fields, ValidationError
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, Email
from ..models import User, Link


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('login')

    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            raise ValidationError('Wrong email address or password.')
        if not user.verify_password(field.data):
            raise ValidationError('Wrong email address or password.')


class LinkCreateForm(FlaskForm):
    domain = StringField('domain', render_kw={"placeholder": "eg. baidu.com"})
    start_url = StringField('start url', render_kw={"placeholder": "eg. https://baidu.com"})
    submit = SubmitField('create')

    def validate_domain(self, field):
        links = Link.query.filter_by(domain=field.data)
        if links.count():
            raise ValidationError('Domain already registerred. Please try another one.')


class BrokenLinkForm(FlaskForm):
    url = StringField('url', render_kw={"readonly": True})
    referer = StringField('referer', render_kw={"readonly": True})
    status = StringField('status', render_kw={"readonly": True})


class LinkForm(FlaskForm):
    domain = StringField('domain', render_kw={"readonly": True})
    start_url = StringField('start url', render_kw={"readonly": True})
    broken_links = fields.FieldList(fields.FormField(BrokenLinkForm))
    last_check_datetime = DateTimeField('last check datetime', render_kw={"readonly": True})
    status = StringField('status', render_kw={"readonly": True})


class RegistrationForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField('password confirm', validators=[DataRequired()])
    username = StringField('username')
    submit = SubmitField('KO')

    def validate_email(self, field):
        """docstring for validate_email"""
        users = User.query.filter_by(email=field.data)
        if users.count():
            raise ValidationError('Email address already registerred. Please try another one.')
