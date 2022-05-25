import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # stuff like custom secret key, database path
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in, the default shit
        app.config.from_mapping(test_config)

    # ensure the instance folder exists, for SQLite database folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # if we have an __init__.py, . means current module
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    # the default endpoint for index would be blog/index
    #   so the add_url_rule() changes it so that it is just '/'
    app.add_url_rule('/', endpoint='index')

    return app