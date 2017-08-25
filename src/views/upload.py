from flask import render_template

from google.appengine.ext import blobstore

from src.views.base_view import BaseView


class UploadView(BaseView):

    def get(self):
        upload_url = blobstore.create_upload_url(
            '/api/internal/podcast/upload/')
        return render_template('upload.html', upload_url=upload_url)


def setup_urls(app):
    app.add_url_rule('/upload/', view_func=UploadView.as_view('upload'))
