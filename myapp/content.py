from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
import json

from myapp.auth import login_required

bp = Blueprint('content', __name__)

# Index route
@bp.route("/")
def home():
    return render_template(
        "home.html", 
        session = session.get('user'), 
        user_data = json.dumps(session.get('user'), indent=4),
        )

# Public content
@bp.route("/public")
def public():
    return "This is a public content!"

# Private content
@bp.route("/private")
@login_required
def private():
    name = session.get('user')['userinfo']['name']
    return f"Welcome - {name} - to the private page."
