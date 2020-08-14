import logging
import os
import json

import requests
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    login_user,
)
from oauthlib.oauth2 import WebApplicationClient
from requests_toolbelt.adapters import appengine

from src.api.podcast import setup_urls as api_podcast_setup_urls
from src.auth.user import User
from src.settings.env_var import EnvVar
from src.views.upload import setup_urls as upload_setup_urls
from src.views.index import setup_urls as index_setup_urls
from src.views.history import setup_urls as history_setup_urls


# Mute ndb so that it doesn't log queries and their results
logging.getLogger("google.cloud.ndb._datastore_api").setLevel(logging.WARNING)
logging.getLogger("google.cloud.ndb._datastore_query").setLevel(logging.WARNING)

# Configuration
# Note: if the client id/secret are rotated, you must delete and recreate the
# instances that have the old values
GOOGLE_CLIENT_ID = EnvVar.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = EnvVar.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

appengine.monkeypatch()
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.contrib.appengine.AppEnginePlatformWarning
)

# Flask app setup
app = Flask(__name__)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.secret_key = EnvVar.get("FLASK_SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
    else:
        return "User email not available or not verified by Google.", 401


    # Ensure email is supported
    whitelisted_emails = EnvVar.get('whitelisted_emails')
    if users_email not in whitelisted_emails:
        return "Forbidden", 401

    # Create a user in your db with the information provided
    # by Google
    user = User.get_or_add(unique_id, users_email)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("home"))



index_setup_urls(app)
upload_setup_urls(app)
api_podcast_setup_urls(app)
history_setup_urls(app)
