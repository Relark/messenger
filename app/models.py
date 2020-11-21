from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy import or_, and_, func
from random import choice
from config import userpic_colors
import time

#Таблица связи диалогов и пользователей + непрочитанные сообщения
association_table = db.Table('association_table',
	db.Column('dialog_id',db.Integer, db.ForeignKey('dialog.id'),index=True),
	db.Column('user_id',db.Integer, db.ForeignKey('user.id'),index=True),
	db.Column('unread',db.Integer,default = 0,index=True)
	)

#Таблица связи, контакты.
contacts = db.Table('contacts',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('contact_id', db.Integer, db.ForeignKey('user.id'))
	)
# Модель пользователя
class User(UserMixin,db.Model): 
	id = db.Column(db.Integer, primary_key=True, index=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	sent_messages = db.relationship('Message', backref='sender',lazy='dynamic')
	last_seen = db.Column(db.DateTime, default=datetime.utcnow()) # Время последнего http запроса
	contacts = db.relationship(
		'User', secondary=contacts,
		primaryjoin=(contacts.c.user_id == id), 
		secondaryjoin=(contacts.c.contact_id == id),
		backref=db.backref('i_am_contact_these_users',lazy='dynamic'), lazy='dynamic')
	color = db.Column(db.String(10),default=choice(userpic_colors)) # Цвет иконки пользователя
	status = db.Column(db.String(1000), default="Место для информации о себе")

	def set_password(self,password): 
		self.password_hash = generate_password_hash(password)

	def check_password(self,password): 
		return check_password_hash(self.password_hash, password)

	def add_contact(self, user): 
		self.contacts.append(user)

	def remove_contact(self, user): # Пока не реализовано 
		if self.is_contact(user):
			self.contacts.remove(user)

	def is_contact(self,user): 
		return self.contacts.filter(
			contacts.c.contact_id == user.id).count() > 0

	def create_personal_dialog(self,user):
		dialog = Dialog(creator=self, personal=True)
		dialog.users.append(self)
		dialog.users.append(user)
		db.session.add(dialog)

	'''
	возвращает строку (dialog_id,user_id) из association_table с общим личным диалогом для двух пользователей,
	если такая есть
	'''
	def is_personal_dialog(self,user):
		subq = db.session.query(association_table.c.user_id,association_table.c.dialog_id).filter(
			(or_(association_table.c.user_id == self.id,association_table.c.user_id == user.id))).subquery()
		return db.session.query(subq.c.dialog_id, func.count(subq.c.dialog_id)).group_by(subq.c.dialog_id).\
				having(func.count(subq.c.dialog_id) == 2).first()


	def dialog_messages(self,dialog_id):
		dialog = Dialog.query.get(dialog_id)
		return dialog.messages.order_by(Message.timestamp.desc())


	def in_dialog(self,dialog_id): # проверка, есть ли пользователь в диалоге
		return db.session.query(association_table).filter(
					and_(association_table.c.user_id == self.id,\
						association_table.c.dialog_id == dialog_id)).count() > 0

	def send_message(self,dialog,message): 
		db.session.add(message)
		query = association_table.update().where(and_(
			association_table.c.user_id != self.id, association_table.c.dialog_id == dialog.id))\
				.values(unread=association_table.c.unread+1)
		db.session.execute(query)


	'''
	left_messages() возвращает список вида [ (m, i,j,k, m.id), ... ], где
	m - cообщение, объект класса Message, 
	i - id диалога в котором это сообщение,
	j - id пользователя,для которого выполняется запрос,
	k - количество непрочитанных пользователем сообщений в диалоге,
	m.id - id сообщения.
	Отображается в левой части сайта, нужно для удобной навигации пользователя по диалогам
	'''
	def left_messages(self):
		subq = db.session.query(Message.id.label('m_id'), Message.dialog_id.label('m_dialog_id'),association_table).join(association_table, and_(
			association_table.c.user_id == self.id,association_table.c.dialog_id == Message.dialog_id)).subquery()
		subq1 = db.session.query(func.max(subq.c.m_id).label('max_id'),subq.c.dialog_id).group_by(subq.c.dialog_id).subquery()
		return db.session.query(Message,association_table,subq1.c.max_id).filter(Message.id == subq1.c.max_id).join(
				association_table, and_(Message.dialog_id == association_table.c.dialog_id, association_table.c.user_id==self.id))\
					.order_by(Message.timestamp.desc()).all()

	'''
	Возвращает никнейм собеседника, если диалог личный,
	либо название диалога, если в нем много пользователей.
	'''
	def dialog_name(self,dialog): # 
		if dialog.personal == True :
			return dialog.users.filter(User.username != self.username).first().username
		else:
			return dialog.name

	'''
	Возвращает цвет иконки собеседника, если диалог личный,
	либо цвет иконки диалога, если в нем много пользователей.
	'''
	def dialog_color(self,dialog): # +
		if dialog.personal == True :
			return dialog.users.filter(User.username != self.username).first().color
		else:
			return dialog.color

	def read_unread_messages(self,dialog_id): # помечает непрочитанные сообщения как прочитанные.
		query = association_table.update().where(and_(
			association_table.c.user_id == self.id, association_table.c.dialog_id == dialog_id)).\
				values(unread=0)
		db.session.execute(query)

	''' 
	при регистрации пользователя добавляет ему в контакты мой аккаунт, 
	отправляет сообщение с информацией о приложении.
	'''
	def add_admin(self):
		admin = User.query.filter_by(username='admin').first()
		dialog = Dialog(creator=admin, personal=True)
		db.session.add(dialog)
		dialog.users.append(self)
		dialog.users.append(admin)
		text = '''Добро пожаловать!'''
		message = Message(
			body=text, sender=admin, dialog=dialog)
		db.session.commit()
		admin.send_message(dialog,message)
		self.add_contact(admin)

	'''
	функция обновления списка диалогов в реальном времени, без перезагрузки страницы.
	Подробнее в routes.py, функция check_new_messages()
	'''
	def new_left_messages(self,time):
		subq = db.session.query(Message.timestamp,Message.id.label('m_id'), Message.dialog_id.label('m_dialog_id'),association_table)\
			.filter(Message.timestamp > time).join(association_table, and_(
				association_table.c.user_id == self.id,association_table.c.dialog_id == Message.dialog_id)).subquery()
		subq1 = db.session.query(func.max(subq.c.m_id).label('max_id'),subq.c.dialog_id).group_by(subq.c.dialog_id).subquery()
		return db.session.query(Message,association_table,subq1.c.max_id).filter(
				Message.timestamp > time).filter(Message.id == subq1.c.max_id).join(
					association_table, and_(Message.dialog_id == association_table.c.dialog_id,\
						association_table.c.user_id==self.id)).order_by(Message.timestamp.desc()).all()

	def __repr__(self):
		return '<User {}>'.format(self.username)

# Модель сообщений
class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True,index=True)
	body = db.Column(db.String(4096))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # время отправки
	sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	dialog_id = db.Column(db.Integer, db.ForeignKey('dialog.id'),index=True)

	def __repr__(self):
		return '<Message: {}>'.format(self.id)
# Модель диалогов
class Dialog(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column(db.String(64), index=True)
	creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	creator = db.relationship('User', backref=db.backref(
		'dialog_creator',lazy='dynamic'))
	messages = db.relationship('Message', foreign_keys = 'Message.dialog_id', backref = 'dialog', lazy='dynamic')
	users = db.relationship(
		'User', secondary=association_table, backref=db.backref('dialogs', lazy='dynamic'), lazy='dynamic' )
	personal = db.Column(db.Boolean, index=True) # True, если диалог между двумя пользователями.
	color = db.Column(db.String(10), default=choice(userpic_colors)) # цвет иконки диалога

	def __repr__(self):
		return '<Dialog: {}>'.format(self.id)
		
@login.user_loader
def load_user(id):
	return User.query.get(int(id))