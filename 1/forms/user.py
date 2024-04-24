from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, DateField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    birthday = DateField('Дата рождения', validators=[DataRequired()])
    sex = SelectField('Пол', validators=[DataRequired()], choices=['Мужской', 'Женский'])
    image = FileField('Фото акканта', validators=[])
    submit = SubmitField('Зарегистрироваться')


class EditForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    birthday = DateField('Дата рождения', validators=[DataRequired()])
    sex = SelectField('Пол', validators=[DataRequired()], choices=['Мужской', 'Женский'])
    image = FileField('Фото акканта', validators=[])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterCompanyForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать')


class LoginCompanyForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Получить доступ')
