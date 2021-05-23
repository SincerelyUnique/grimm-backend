import os
import uuid


class Config(object):
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    SECURITY_PASSWORD_SALT = uuid.uuid4().hex
    ThreadPoolExecutor = 10
    ProcessPoolExecutor = 5
    wxappid = 'wx933eded634abf038'
    wxsecret = '9e25fb830e30b2a36959e795a9db628a'
    SWAGGER = {
        'title': 'Grimm API',
        "description": "Grimm api doc, build with swagger.",
        'uiversion': 2
    }


class DevConfig(Config):
    # SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@localhost:3306/grimmdb"
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost:3306/grimmdb"


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@localhost:3306/grimmdb"


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@localhost:3306/grimmdb"


configuration = {'dev': DevConfig, 'prod': ProdConfig, 'test': TestConfig}
