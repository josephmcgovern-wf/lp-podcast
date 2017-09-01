from flask import render_template

from src.views.base_view import BaseView


class HistoryView(BaseView):

    def get(self):
        return render_template('history.html')


def setup_urls(app):
    app.add_url_rule('/history/', view_func=HistoryView.as_view('history'))
