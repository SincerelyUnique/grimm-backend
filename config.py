import os
import uuid


class Config(object):
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    SECURITY_PASSWORD_SALT = uuid.uuid4().hex
    WXAppID = ''
    WXAppSecret = ''


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/grimmdb"
    SMS_ACCESS_KEY_ID = ''
    SMS_ACCESS_KEY_SECRET = ''
    SMTP_ADDRESS = ''
    SMTP_PORT = ''
    SMTP_SERVER = ''
    SMTP_PASSWORD = ''


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/grimmdb"
    SMS_ACCESS_KEY_ID = ''
    SMS_ACCESS_KEY_SECRET = ''
    SMTP_ADDRESS = ''
    SMTP_PORT = ''
    SMTP_SERVER = ''
    SMTP_PASSWORD = ''


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/grimmdb"
    SMS_ACCESS_KEY_ID = ''
    SMS_ACCESS_KEY_SECRET = ''
    SMTP_ADDRESS = ''
    SMTP_PORT = ''
    SMTP_SERVER = ''
    SMTP_PASSWORD = ''


configuration = {'dev': DevConfig, 'prod': ProdConfig, 'test': TestConfig}
