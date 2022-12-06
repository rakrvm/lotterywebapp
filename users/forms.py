from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, Length, EqualTo
import re

def character_check(form, field):
    excluded_chars = "* ? ! ' ^ + % & / ( ) = } ] [ { $ # @ < >" #specified characters not allowed

    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")

def phone_check(form, field):
    phone_numbercheck = re.compile("^[0-9]{4}-[0-9]{3}-[0-9]{4}$")

    if not phone_numbercheck.match(field.data):
        raise ValidationError('Must be a valid phone number in the format XXXX-XXX-XXXX')

def password_check(form,field):
    password_checker = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)')

    if not password_checker.match(field.data):
        raise ValidationError("Must contain at least; 1 number, 1 lowercase and uppercase character, "
                              "at least 1 special character.")


class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    firstname = StringField(validators=[DataRequired(), character_check])
    lastname = StringField(validators=[DataRequired(), character_check])
    phone = StringField(validators=[DataRequired(), phone_check])
    password = PasswordField(validators=[DataRequired(), Length(min = 6, max= 12), password_check])
    confirm_password = PasswordField(validators=[DataRequired(),EqualTo("password", message="Must be equal to password")])
    submit = SubmitField(validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    recaptcha = RecaptchaField()
    pin = StringField(validators=[DataRequired()])
    submit = SubmitField(validators=[DataRequired()])