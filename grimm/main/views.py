from datetime import datetime

import bcrypt
from flask import jsonify
from sqlalchemy import inspect

from grimm import logger, db, engine
from grimm.main import main
from grimm.models.admin import Admin
from grimm.utils import constants


@main.route("/", methods=['GET'])
def main_app():
    return 'Welcome to Grimm!'


@main.route("/db/init", methods=['GET'])
def init_db():
    """init db, attention: must create db manually and then execute this interface"""
    if inspect(engine).has_table(Admin.__tablename__):
        return 'Database table already exists.'
    db.create_all()
    admin_info = Admin()
    admin_info.id = 0
    admin_info.registration_date = datetime.now().strftime("%Y-%m-%d")
    admin_info.email = 'no.reply@rp-i.org'
    admin_info.email_verified = 1
    admin_info.name = "root"
    salt = bcrypt.gensalt(constants.DEFAULT_PASSWORD_SALT)
    bcrypt_password = bcrypt.hashpw('Cisco123456.'.encode('utf-8'), salt)
    admin_info.password = bcrypt_password
    db.session.add(admin_info)
    db.session.commit()
    return 'Database table created successfully.'


@main.route("/tags", methods=['GET'])
def tags_db():
    """view function to get all tags info 111"""
    tag_list = [{'tag_id': i, 'tag_name': constants.TAG_LIST[i]} for i in range(len(constants.TAG_LIST))]
    logger.info("query all tags info successfully")
    return jsonify(tag_list)
