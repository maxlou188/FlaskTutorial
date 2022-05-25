import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    # teardown_appcontext() tells flask to call that function when cleaning up
    #   after returning response
    app.teardown_appcontext(close_db)

    # adds a new command that can be called with the flask command
    app.cli.add_command(init_db_command)

def init_db():
    db = get_db()

    # open_resource() opens a file relative to flaskr application,
    #   the one that we gave __init__.py for
    with current_app.open_resource('schema.sql') as f:
        # get_db() is used to make the connection
        #   and now we can execute those operations
        #   with db
        db.executescript(f.read().decode('utf8'))

# click.command() defines a command line command called 'init-db'
#   that calls the init_db() function and echoes a successful message
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# g is an object in each request, unique with each request
#   stores data that might be accessed by multiple functions
#   throughout the request. 

def get_db():
    # this db not in g ensures that the connection is stored and reused 
    #   instead of creating a new connection if get_db() is called a 
    #   second time in the same request. If we already called get_db()
    #   once, then we directly return g.db!
    if 'db' not in g:
        # establishes a connetion to the file pointed at by the
        #   'DATABASE' key
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # means return rows that behave like dicts, accesing
        #   columns name by name
        g.db.row_factory = sqlite3.Row

    return g.db

# checks if there was a connection and closes it if there was one
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()