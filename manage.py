import os

from flask_script import Manager

from grimm import create_app, logger

basedir = os.path.abspath(os.path.dirname(__file__))
app = create_app(os.path.join(basedir, "config.py"))
manager = Manager(app)


@app.errorhandler(404)
def page_not_found(e):
    logger.warning('Server 404.')


@app.errorhandler(500)
def internal_server_error(e):
    logger.error('Server 500.')


@app.errorhandler(503)
def server_unavailable(e):
    logger.error('Server 503.')


if __name__ == '__main__':
    manager.run()
