from flask import render_template, flash, redirect, url_for, request, json,g,session
from app import app, db
from app.forms import LoginForm, RegistrationForm, SearchContactForm,SettingsForm,SendForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User,Dialog,Message,association_table 
from werkzeug.urls import url_parse
from random import choice
from datetime import datetime
import time
from sqlalchemy import and_
from config import userpic_colors

@app.before_request
def before_request():
	g.start = time.time()

@app.after_request
def after_request(response):
	diff = time.time() - g.start # время выполнения запроса
	print(diff)
	return response

@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for('login'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return redirect(url_for('login'))

@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('im'))
	form = LoginForm()
	if form.validate_on_submit(): # в случае если данные формы в порядке
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Неверное имя пользователя или пароль','error')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next') # берет next аргумент из url
		if not next_page or url_parse(next_page).netloc != '': # блокирует редирект на полный url (защита от подмены сайта)
			next_page = url_for('im')
		return redirect(next_page)
	return render_template('login.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if current_user.is_authenticated:
		return redirect(url_for('im'))
	if form.validate_on_submit():
		user = User(username=form.username.data,email=form.email.data,color=choice(userpic_colors))
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		user.add_admin() # добавляет в контакты аккаунт администратора сайта, создает диалог с ним
		db.session.commit()
		flash('Вы успешно зарегестрированы')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/im', methods=['GET','POST'])
@app.route('/im<int:im_id>', methods=['GET','POST'])
@login_required
def im(im_id=None):
	session['time'] = datetime.utcnow() # нужно для функции check_new_messages(), смотреть ниже
	time = datetime.utcnow()
	contacts_form = SearchContactForm()
	settings_form = SettingsForm()
	if settings_form.submit.data and settings_form.validate_on_submit():
		current_user.username = settings_form.username1.data
		current_user.email = settings_form.email.data
		current_user.status = settings_form.status.data
		if settings_form.password.data:
			current_user.set_password(settings_form.password.data)
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
		flash('Данные обновлены!','settings')
		return redirect(url_for('im', im_id=im_id))
	settings_form.username1.data = current_user.username
	settings_form.email.data = current_user.email
	settings_form.status.data = current_user.status
	if contacts_form.submit1.data and contacts_form.validate_on_submit():
		user = User.query.filter_by(username=contacts_form.username.data).first()
		current_user.add_contact(user)
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
		flash('Пользователь добавлен в контакты', 'contacts')
		return redirect(url_for('im',im_id=im_id))
	if im_id==None : 
		left_messages = current_user.left_messages()
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
		return render_template('im_none.html', time = time, left_messages=left_messages,
			contacts_form=contacts_form,settings_form=settings_form)
	else:
		dialog = Dialog.query.get(im_id)
		if dialog:
			if current_user.in_dialog(dialog.id): # Проверка, есть ли у пользователя доступ к диалогу
				current_user.read_unread_messages(im_id)
				left_messages = current_user.left_messages()
				current_user.last_seen = datetime.utcnow()
				db.session.commit()
				if dialog.personal == True: # нужно для отображения информации о пользователе в шапке сайта
					user = dialog.users.filter(User.username != current_user.username).first() 
				messages = current_user.dialog_messages(dialog.id).limit(50).all()
				return render_template('im.html', user=user, time=time, messages=messages,dialog=dialog, left_messages=left_messages,
					contacts_form=contacts_form,settings_form=settings_form)
			else: 
				return redirect(url_for('im'))
		else: 
			return redirect(url_for('im'))


"""
функция открытия диалога, вызывается, когда пользователь
открывает личный диалог через меню "Контакты"
"""
@app.route('/open_dialog/<username>')
@login_required
def open_dialog(username):
	user = User.query.filter_by(username=username).first()
	if user:
		row = current_user.is_personal_dialog(user) # возвращает (dialog_id,user_id) из association_table
		if row: # если есть личный диалог, открываем его
			return redirect(url_for('im', im_id=row[0]))
		else:  # если нет, создаем и открываем
			current_user.create_personal_dialog(user)
			db.session.commit()
			row = current_user.is_personal_dialog(user)
			return redirect(url_for('im', im_id=row[0]))
	else:
		return redirect(url_for('im'))
'''
функция подгрузки старых сообщений, 
срабатывает, когда скролл достигает верха
'''
@app.route('/get_more_messages', methods=['POST']) 
@login_required
def get_more_messages():
	time = datetime.utcnow()
	req = request.get_json()
	count = req['count'] # количество сообщений на странице, чтобы знать, в каком диапазоне извлекать из базы
	dialog_id = req['dialog_id']
	if current_user.in_dialog(dialog_id): 
		messages = current_user.dialog_messages(dialog_id).slice(count,count+20).all()
		return render_template('_messages.html', messages=messages, time=time)


"""
функция получения информации о пользователе,
вызывается при клике на никнейм в диалоге, 
отображается модальным окном
"""
@app.route('/get_user_info', methods=['POST'])
@login_required
def get_user_info():
	time = datetime.utcnow()
	user_id = request.get_json()
	user = User.query.get(user_id)
	return render_template('_user_info.html', user=user,time=time)


"""
вызывается js функцией каждую секунду.
выполняет две задачи: проверяет наличие новых сообщений в открытом диалоге,
проверяет, есть ли новые сообщения среди всех диалогов(чтобы отобразить их в левом блоке сайта).

Session используется для того, чтобы доставать из бд только те сообщения, которые были отправлены
между срабатываниями функции сheck_new_message(). Для экономии времени выполнения запроса.
"""
@app.route('/check_new_messages', methods=['POST'])
@login_required
def check_new_messages():
	time = datetime.utcnow()
	req = request.get_json()
	if req:
		count = db.session.query(association_table).filter(
			and_(association_table.c.user_id == current_user.id, association_table.c.dialog_id == req)).first()[2]
		if count:
			messages = current_user.dialog_messages(req).limit(count).all()
			current_user.read_unread_messages(req)
			db.session.commit()
			new_messages_html = render_template('_messages.html', messages=messages,time=time)
		else: new_messages_html = ''
	else: new_messages_html = ''
	new_left_messages = current_user.new_left_messages(session.get('time', None))
	session['time'] = datetime.utcnow()
	if new_left_messages:
		new_left_messages_html = render_template('_left_messages.html',left_messages=new_left_messages,time=time)
	else: new_left_messages_html = ''
	return {'left_messages' : new_left_messages_html, 'count' : len(new_left_messages), 'messages': new_messages_html}

'''
вызывается при отправке сообщения
'''	
@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
	time = datetime.utcnow()
	req = request.get_json()
	dialog = Dialog.query.get(req['dialog_id'])
	form = SendForm(text=req['textarea_data'])
	if form.validate():
		message = Message(body=req['textarea_data'], sender=current_user, dialog=dialog)
		current_user.send_message(dialog,message)
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
		messages = [message]
		return render_template('_messages.html', messages=messages,time=time)
	else:
		return ''

'''
функция загрузки тестового пользователя, для демонстрации возможностей приложения без регистрации
'''
@app.route('/login_test_user')
def login_test_user():
	user = User.query.filter_by(username='test').first()
	login_user(user)
	return redirect(url_for('im'))
