import os
import uuid

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    SECURITY_PASSWORD_SALT = uuid.uuid4().hex
    WXAppID = 'wx933eded634abf038'
    WXAppSecret = '9e25fb830e30b2a36959e795a9db628a'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/grimmdb"
    # SQLALCHEMY_DATABASE_URI = "mysql+cymysql://root:root@localhost:3306/grimmdb"
    # SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@localhost:3306/grimmdb"
    SMS_ACCESS_KEY_ID = ''
    SMS_ACCESS_KEY_SECRET = ''
    SMTP_ADDRESS = ''
    SMTP_PORT = ''
    SMTP_SERVER = ''
    SMTP_PASSWORD = ''


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/grimmdb"
    SMS_ACCESS_KEY_ID = ''
    SMS_ACCESS_KEY_SECRET = ''
    SMTP_ADDRESS = ''
    SMTP_PORT = ''
    SMTP_SERVER = ''
    SMTP_PASSWORD = ''


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/grimmdb"
    SMS_ACCESS_KEY_ID = ''
    SMS_ACCESS_KEY_SECRET = ''
    SMTP_ADDRESS = ''
    SMTP_PORT = ''
    SMTP_SERVER = ''
    SMTP_PASSWORD = ''


configuration = {'dev': DevelopmentConfig, 'prod': ProductionConfig, 'test': TestingConfig}
