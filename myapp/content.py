#========================================================================
# Demonstrating the content with various authentication and authorization 
# requirements
#========================================================================
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
import json
from myapp.auth import login_required
import requests

bp = Blueprint('content', __name__)

#============================================
# Content that comes purely from this application
#============================================
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
    name = session.get('user')
    return f"Welcome - {name} - to the private page."

#============================================
# Content that comes from external API
#============================================
@bp.route("/api/public")
def api_public():
    # Make request to public endpoint without providing token
    url = "http://localhost:3000/api/public"
    res = requests.get(url)
    return res.content

# Private content
@bp.route("/api/private")
@login_required
def api_private():
    access_token = session.get('user')['access_token']
    token_type = session.get('user')['token_type']
    headers = { 'Authorization': f"{token_type} {access_token}" }
    url = "http://localhost:3000/api/private"
    res = requests.get(url, headers=headers)
    return res.content

# Scoped content
@bp.route("/api/private-scoped")
@login_required
def api_private_scoped():
    access_token = session.get('user')['access_token']
    token_type = session.get('user')['token_type']
    headers = { 'Authorization': f"{token_type} {access_token}" }
    url = "http://localhost:3000/api/private-scoped"
    res = requests.get(url, headers=headers)
    return res.content