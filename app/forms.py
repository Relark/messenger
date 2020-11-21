from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm): 
	username = StringField('Логин', validators = [DataRequired(u'Введите логин')])
	password = PasswordField('Пароль', validators = [DataRequired(u'Введите пароль')])
	remember_me = BooleanField('Запомнить?')
	submit = SubmitField('Войти')

class RegistrationForm(FlaskForm): 
	username = StringField('Логин', validators=[DataRequired(u'Введите логин')])
	email = StringField('Email', validators=[DataRequired(u'Введите email'), Email('Введите настоящий email')])
	password = PasswordField('Пароль', validators=[DataRequired(u'Введите пароль')])
	password2 = PasswordField('Повторите пароль', validators=[DataRequired(u'Повторите пароль'), EqualTo('password', 'Пароли не совпадают')])
	submit = SubmitField('Регистрация')

	def validate_username(self,username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Логин уже занят')

	def validate_email(self,email):
		email = User.query.filter_by(email=email.data).first()
		if email:
			raise ValidationError('Email уже занят')


class SearchContactForm(FlaskForm): 
	username = StringField('Добавить контакт:', validators=[DataRequired(u'Введите имя пользователя')])
	submit1 = SubmitField('Добавить')

	def validate_username(self,username):
		user = User.query.filter_by(username=username.data).first()
		if not user:
			raise ValidationError('Пользователь не найден')
		if user == current_user:
			raise ValidationError('Нельзя добавить себя в контакты')
		if user == current_user.contacts.filter_by(username=username.data).first():
			raise ValidationError('Пользователь уже в вашем списке контактов')

class SettingsForm(FlaskForm):
	username1 = StringField('Логин:', validators=[DataRequired(u'Введите логин')])
	password = PasswordField('Новый пароль:')
	password2 = PasswordField('Повторите пароль:', validators=[EqualTo('password', 'Пароли не совпадают')])
	email = StringField('Email:', validators=[DataRequired(u'Введите email'), Email('Введите настоящий email')])
	status = TextAreaField('О себе:', validators=[DataRequired(u'Введите информацию')])
	submit = SubmitField('Изменить')

	def validate_username1(self,username1):
		user = User.query.filter_by(username=username1.data).first()
		if user and current_user != user:
			raise ValidationError('Такой логин уже занят')
	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user and current_user != user:
			raise ValidationError('Такой email уже занят')

class SendForm(Form):
	text = StringField(validators=[DataRequired()])