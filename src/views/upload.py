from flask import render_template

from src.views.base_view import BaseView


class UploadView(BaseView):

    def get(self):
        return render_template('upload.html')


def setup_urls(app):
    app.add_url_rule('/upload/', view_func=UploadView.as_view('upload'))
