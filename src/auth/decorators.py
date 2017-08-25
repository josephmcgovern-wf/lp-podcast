from google.appengine.api import users
from flask import redirect, request
from src.settings.env_var import EnvVar


def login_required(f):
    def wrapped_f(*args, **kwargs):
        user = users.get_current_user()
        email = user.email() if user else ""
        whitelisted_emails = EnvVar.get('whitelisted_emails')
        if not email or email not in whitelisted_emails:
            return redirect(users.create_login_url(
                dest_url=request.full_path))

        return f(*args, **kwargs)
    return wrapped_f
