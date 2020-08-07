from flask_login import login_required

from flask.views import MethodView


class BaseView(MethodView):
    decorators = [login_required]
