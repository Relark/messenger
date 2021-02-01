from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Message, Dialog, association_table
from sqlalchemy import and_

class UserTestCase(unittest.TestCase):
	def setUp(self):
		app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/messenger_test'
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_password_hashing(self):
		u = User(username='Tom')
		u.set_password('cat')
		self.assertFalse(u.check_password('dog'))
		self.assertTrue(u.check_password('cat'))

	def test_contacts(self):
		u1 = User(username='Tom')
		u2 = User(username='Jerry')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		self.assertEqual(u1.contacts.all(), [])
		self.assertEqual(u2.contacts.all(), [])

		u1.add_contact(u2)
		db.session.commit()
		self.assertTrue(u1.is_contact(u2))
		self.assertFalse(u2.is_contact(u1))
		self.assertEqual(u1.contacts.count(), 1)
		self.assertEqual(u2.contacts.count(), 0)

		u1.remove_contact(u2)
		db.session.commit()
		self.assertFalse(u1.is_contact(u2))
		self.assertFalse(u2.is_contact(u1))
		self.assertEqual(u1.contacts.count(), 0)
		self.assertEqual(u2.contacts.count(), 0)

class DialogTestCase(unittest.TestCase):
	def setUp(self):
		app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/messenger_test'
		db.create_all()
		# создадим несколько пользователей
		u1 = User(username='u1')
		u2 = User(username='u2')
		u3 = User(username='u3')
		u4 = User(username='u4')
		db.session.add(u1)
		db.session.add(u2)
		db.session.add(u3)
		db.session.add(u4)
		db.session.commit()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_create_personal_dialog(self):
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u3 = User.query.filter_by(username='u3').first()
		u4 = User.query.filter_by(username='u4').first()

		#Создадим диалоги между пользователями
		u1.create_personal_dialog(u2)
		u3.create_personal_dialog(u4)
		u1.create_personal_dialog(u4)
		db.session.commit()

		d1 = Dialog.query.get(1) # диалог между u1 и u2
		d2 = Dialog.query.get(2) # диалог между u3 и u4
		d3 = Dialog.query.get(3) # диалог между u1 и u4

		# проверяем правильно ли пользователи добавились в диалоги
		self.assertCountEqual(u1.dialogs.all(), [d1,d3])
		self.assertCountEqual(u2.dialogs.all(), [d1])
		self.assertCountEqual(u3.dialogs.all(), [d2])
		self.assertCountEqual(u4.dialogs.all(), [d2,d3])

	def test_in_dialog(self):
		# проверяем функцию in_dialog
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u3 = User.query.filter_by(username='u3').first()
		u4 = User.query.filter_by(username='u4').first()

		u1.create_personal_dialog(u2)
		u3.create_personal_dialog(u4)
		u1.create_personal_dialog(u4)
		db.session.commit()

		d1 = Dialog.query.get(1) # диалог между u1 и u2
		d2 = Dialog.query.get(2) # диалог между u3 и u4
		d3 = Dialog.query.get(3) # диалог между u1 и u4

		self.assertTrue(u1.in_dialog(d1.id))
		self.assertFalse(u1.in_dialog(d2.id))
		self.assertTrue(u1.in_dialog(d3.id))

		self.assertTrue(u2.in_dialog(d1.id))
		self.assertFalse(u2.in_dialog(d2.id))
		self.assertFalse(u2.in_dialog(d3.id))

		self.assertTrue(u3.in_dialog(d2.id))
		self.assertFalse(u3.in_dialog(d1.id))
		self.assertFalse(u3.in_dialog(d3.id))

		self.assertTrue(u4.in_dialog(d2.id))
		self.assertTrue(u4.in_dialog(d3.id))
		self.assertFalse(u4.in_dialog(d1.id))

	def test_is_personal_dialog(self):
		# is_personal_dialog проверяет, есть ли личный диалог между пользователями
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u3 = User.query.filter_by(username='u3').first()
		u4 = User.query.filter_by(username='u4').first()

		u1.create_personal_dialog(u2)
		u3.create_personal_dialog(u4)
		u1.create_personal_dialog(u4)
		db.session.commit()

		self.assertTrue(u1.is_personal_dialog(u2))
		self.assertTrue(u1.is_personal_dialog(u4))
		self.assertFalse(u1.is_personal_dialog(u3))

		self.assertTrue(u2.is_personal_dialog(u1))
		self.assertFalse(u2.is_personal_dialog(u3))
		self.assertFalse(u2.is_personal_dialog(u4))

		self.assertTrue(u3.is_personal_dialog(u4))
		self.assertFalse(u3.is_personal_dialog(u1))
		self.assertFalse(u3.is_personal_dialog(u2))

		self.assertTrue(u4.is_personal_dialog(u1))
		self.assertTrue(u4.is_personal_dialog(u3))
		self.assertFalse(u4.is_personal_dialog(u2))

	def test_messages(self):
		# тестируем отправление сообщений
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u1.create_personal_dialog(u2)
		db.session.commit()
		d1 = Dialog.query.get(1) # диалог между u1 и u2

		self.assertFalse(d1.messages.all())
		m1 = Message(body='message1', sender=u1, dialog=d1)
		m2 = Message(body='message2', sender=u1, dialog=d1)
		m3 = Message(body='message3', sender=u2, dialog=d1)
		u1.send_message(dialog=d1, message=m1)
		u1.send_message(dialog=d1, message=m2)
		u2.send_message(dialog=d1, message=m3)
		db.session.commit()
		self.assertCountEqual(d1.messages.all(),[m1,m2,m3])
		self.assertCountEqual(u1.sent_messages.all(),[m1,m2])
		self.assertCountEqual(u2.sent_messages.all(),[m3])

	def test_dialog_messages(self):
		# dialog_messages  возвращает отсортированные сообщения от новых к старым
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u1.create_personal_dialog(u2)
		d1 = Dialog.query.get(1) #диалог между u1 и u2

		m1 = Message(body='message1', sender=u1, dialog=d1)
		m2 = Message(body='message2', sender=u1, dialog=d1)
		m3 = Message(body='message3', sender=u2, dialog=d1)

		u1.send_message(dialog=d1, message=m1)
		u1.send_message(dialog=d1, message=m2)
		u2.send_message(dialog=d1, message=m3)
		db.session.commit()

		self.assertEqual(u1.dialog_messages(d1.id).all(), [m3,m2,m1])
		self.assertEqual(u2.dialog_messages(d1.id).all(), [m3,m2,m1])

	def test_unread_messages(self):

		# Тут мы хотим проверить, правильно ли добавляется в бд информация о непрочитанных сообщениях
		# при отправке нового сообщения.

		# u1_row, u2_row - строки из association_table вида (i,j,k),
		# где i - id диалога, j - id пользователя в диалоге,
		# k -  количество непрочитанных сообщений пользователем в диалоге.

		# Т.е. u1_row[2] - число непрочитанных сообщений в диалоге у пользователя u1.

		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u1.create_personal_dialog(u2)
		d1 = Dialog.query.get(1)

		u1_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u1.id, association_table.c.dialog_id == d1.id)).first()
		u2_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u2.id, association_table.c.dialog_id == d1.id)).first()

		# У u1,u2 нет непрочитанных сообщений
		self.assertEqual(u1_row[2], 0)
		self.assertEqual(u2_row[2], 0) 

		m1 = Message(body='message1', sender=u1, dialog=d1)
		m2 = Message(body='message2', sender=u1, dialog=d1)
		m3 = Message(body='message3', sender=u2, dialog=d1)

		u1.send_message(dialog=d1, message=m1)
		u1.send_message(dialog=d1, message=m2)
		u2.send_message(dialog=d1, message=m3)
		db.session.commit()

		u1_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u1.id, association_table.c.dialog_id == d1.id)).first()
		u2_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u2.id, association_table.c.dialog_id == d1.id)).first()

		self.assertEqual(u1_row[2], 1) # У u1 одно непрочитанное сообщение
		self.assertEqual(u2_row[2], 2) # У u2 два непрочитанных сообщения

	def test_read_unread_messages(self):
		# проверка функции read_unread_messages, помечающей непрочитанные сообщения прочитанными
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u1.create_personal_dialog(u2)
		d1 = Dialog.query.get(1)

		m1 = Message(body='message1', sender=u1, dialog=d1)
		m2 = Message(body='message2', sender=u1, dialog=d1)
		m3 = Message(body='message3', sender=u2, dialog=d1)
		
		u1.send_message(dialog=d1, message=m1)
		u1.send_message(dialog=d1, message=m2)
		u2.send_message(dialog=d1, message=m3)
		db.session.commit()

		u1_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u1.id, association_table.c.dialog_id == d1.id)).first()
		u2_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u2.id, association_table.c.dialog_id == d1.id)).first()
		self.assertEqual(u1_row[2], 1)
		self.assertEqual(u2_row[2], 2)

		u1.read_unread_messages(d1.id) 
		db.session.commit()
		u1_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u1.id, association_table.c.dialog_id == d1.id)).first()
		u2_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u2.id, association_table.c.dialog_id == d1.id)).first()
		self.assertEqual(u1_row[2], 0)
		self.assertEqual(u2_row[2], 2)

		u2.read_unread_messages(d1.id)
		db.session.commit()
		u1_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u1.id, association_table.c.dialog_id == d1.id)).first()
		u2_row = db.session.query(association_table).filter(and_(
			association_table.c.user_id == u2.id, association_table.c.dialog_id == d1.id)).first()
		self.assertEqual(u1_row[2], 0)
		self.assertEqual(u1_row[2], 0)

	def test_left_messages(self):
		# left_messages возвращаетй список, 
		# в котором находится по одному последнему сообщению из каждого диалога пользователя.
		# Эти сообщения отображаются в левой колонке на сайте, для удобной навигации по диалогам.

		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u3 = User.query.filter_by(username='u3').first()

		u1.create_personal_dialog(u2)
		u2.create_personal_dialog(u3)
		u3.create_personal_dialog(u1)
		db.session.commit()

		d1 = Dialog.query.get(1) # диалог между u1 и u2
		d2 = Dialog.query.get(2) # диалог между u2 и u3
		d3 = Dialog.query.get(3) # диалог между u3 и u1

		self.assertFalse(u1.left_messages())
		self.assertFalse(u2.left_messages())
		self.assertFalse(u3.left_messages())

		m1 = Message(body='message1',sender=u1,dialog=d1)
		m2 = Message(body='message2',sender=u2,dialog=d1)
		m3 = Message(body='message3',sender=u2,dialog=d2)
		m4 = Message(body='message4',sender=u3,dialog=d2)
		m5 = Message(body='message5',sender=u3,dialog=d3)
		m6 = Message(body='message6',sender=u1,dialog=d3)

		u1.send_message(d1,m1)
		u2.send_message(d1,m2)
		u2.send_message(d2,m3)
		u3.send_message(d2,m4)
		u3.send_message(d3,m5)
		u1.send_message(d3,m6)
		db.session.commit()
		
		# left_messages() возвращает список вида [ (m, i,j,k, m.id), ... ], где
		# m - сообщение, 
		# i - id диалога в котором это сообщение,
		# j - id пользователя,для которого выполняется запрос,
		# k - количество непрочитанных пользователем сообщений в диалоге,
		# m.id - id сообщения
			
		self.assertCountEqual(u1.left_messages(), [ (m2,d1.id,u1.id,1,m2.id), (m6,d3.id,u1.id,1,m6.id) ] )
		self.assertCountEqual(u2.left_messages(), [ (m2,d1.id,u2.id,1,m2.id), (m4,d2.id,u2.id,1,m4.id) ] )
		self.assertCountEqual(u3.left_messages(), [ (m6,d3.id,u3.id,1,m6.id), (m4,d2.id,u3.id,1,m4.id) ] )

	def test_dialog_name(self):
		# dialog_name возвращает имя диалога, если в диалоге много пользователей,
		# либо имя собеседника, если диалог личный
		# т.к. многопользовательские диалоги пока не реализованы, тестируется только часть функции
		
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u1.create_personal_dialog(u2)
		db.session.commit()
		d1 = Dialog.query.get(1)
		self.assertEqual(u1.dialog_name(d1), u2.username)
		self.assertEqual(u2.dialog_name(d1), u1.username)

	def test_dialog_color(self):
		# dialog_color возвращает цвет иконки диалога, если в диалоге много пользователей,
		# либо цвет иконки собеседника, если диалог личный
		# т.к. многопользовательские диалоги пока не реализованы, тестируется только часть функции
		u1 = User.query.filter_by(username='u1').first()
		u2 = User.query.filter_by(username='u2').first()
		u1.create_personal_dialog(u2)
		db.session.commit()
		d1 = Dialog.query.get(1)
		self.assertEqual(u1.dialog_color(d1), u2.color)
		self.assertEqual(u2.dialog_color(d1), u1.color)


	def test_add_admin(self):
		# add_admin добавляет каждому зарегестрированному пользователю
		# в контакты аккаунт администратора(мой аккаунт) и приветственное сообщение.
		u1 = User.query.filter_by(username='u1').first()
		admin = User(username='admin')
		db.session.add(admin)
		db.session.commit()
		u1.add_admin()
		db.session.commit()
		self.assertEqual(u1.contacts.all(), [admin])
		print(admin.dialogs.all()[0])
		self.assertCountEqual(admin.dialogs.all()[0].users.all(), [admin,u1])
		self.assertTrue(admin.sent_messages.all())

if __name__ == '__main__':
	unittest.main(verbosity=2)