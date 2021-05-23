from flask import jsonify

from grimm import logger
from grimm.main import main
from grimm.utils import constants


@main.route("/tags", methods=['GET'])
def tags_db():
    """view function to get all tags info 111"""
    tag_list = [{'tag_id': i, 'tag_name': constants.TAG_LIST[i]} for i in range(len(constants.TAG_LIST))]
    logger.info("query all tags info successfully")
    return jsonify(tag_list)
