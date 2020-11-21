import os

basedir = os.path.abspath(os.path.dirname(__file__))
userpic_colors = ['#6fb1e4', '#cc90e2', '#80d066', '#e57979', '#cc90e2', '#ecd074', '#fba76f', '#f98bae']

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
