import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


# a Blueprint is a collection of routes and app functions that 
#   we can define here before an app is created. Normally we would do something 
#   like app.route() or api.add_resource, where app is from Api(app)
#   bp.route('/register')

# this creates a Blueprint named auth, and the blueprint needs to know where it is defined
#   so we pass __name__ as its second argument
bp = Blueprint('auth', __name__, url_prefix='/auth')

# associates /register endpoint with register function here

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # db.execute() takes a SQL query with ? as placeholders and 
                #   a tuple of values to replace them with
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # url_for is preferable to writing the url because if you end up 
                #   changing the login url, don't have to change it here
                return redirect(url_for("auth.login"))

        # will show error if there is one, errors are stored and
        #   can be retrieved while rendering the template
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # fetchone() returns one row from the query or None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            # this id is stored when validation succeeds
            #   the browser stores it as a cookie for further requests
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# this decorator says that this function runs before the view function
#   no matter what url is requested
# load_logged_in_user sees if there is a user that is logged in
#   stores the result to g.user, None or the user id
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    # removes the user id from session
    session.clear()
    return redirect(url_for('index'))


# this is a decorator that wraps the original view function it is applied to
#   makes us require authentication in other views
#   **kwargs gets all of the inputs to view. So we have access to g or g.user
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view