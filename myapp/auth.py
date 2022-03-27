import functools

import json

# Current app is used to access the application object when the blueprint is created
from flask import (
    Blueprint, g, redirect, render_template, request, session, url_for, current_app
)

from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth

# To load .env
# Should be replaced with loading secrets from the instance
from os import environ as env

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Configure Authlib to handle applications authentication with Auth0
oauth = OAuth(current_app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


# /login route visitors will be redirected to Auth0 to begin authentication flow
@bp.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )


# After finishing the log-in with Auth0, the user will be returned to the application's /callback route
# This route will also save the session for the user
@bp.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


# /logout will clear user's session in the app and redirects to Auth0 logout endpoint before
# the users are returned to home route
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# Registers a function that runs befor the view function no matter what URL is requested
# it stores the user data in g.user, which lasts for the lenght of a single request
# NB: i don't understand the need for this
@bp.before_app_request
def load_logged_in_user():
    user = session.get('user')

    if user is None:
        g.user = None
    else:
        g.user = user

# A decorator to require authentication
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view