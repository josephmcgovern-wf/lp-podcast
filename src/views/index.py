from flask import render_template
from src.views.base_view import BaseView


class HomeView(BaseView):

    def get(self):
        return render_template('index.html')


def setup_urls(app):
    app.add_url_rule('/', view_func=HomeView.as_view('home'))
