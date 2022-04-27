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


# Configure Authlib to handle authentication and authorization
oauth = OAuth(current_app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    # Define the url for querying access token for our external api
    # and indicate that we are using Authorization Code Flow
    access_token_url=f"https://{env.get('AUTH0_DOMAIN')}/oauth/token",
    access_token_params={
        "grant_type":"authorization_code"
    },
    # Define the URL for auth0 authorization endpoint
    # define all the scopes for which you want to get the access
    # And indicate the the 'code' should be returned that could be
    # exchanges for access token.
    authorize_url=f"https://{env.get('AUTH0_DOMAIN')}/authorize",
    authorize_params={
        "scope": "openid email profile read:calculator",
        "audience": "https://testapi/api",
        "response_type": "code",
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

# A decorator to require authentication
def login_required(view):
    """Opens a view for authenticated user and login page for anonymous user.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user'):
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view