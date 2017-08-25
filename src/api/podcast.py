from flask import request
import json
import re

from google.appengine.ext import blobstore

from src.aws.bucket import Bucket
from src.podcast.podcast import Podcast
from src.views.base_view import BaseView


class PodcastAPI(BaseView):

    def post(self):
        data = request.get_json()
        p = Podcast(**data)
        try:
            p._check_initialized()
        except Exception as e:
            return e.message, 400
        p.put()
        p.add_to_rss_feed()
        return 'Success', 200


class AudioFileAPI(BaseView):

    def post(self):
        try:
            f = request.files['audioFile']
            link = Bucket.upload_file(f)
            return json.dumps({'url': link})
        except Exception as e:
            return e.message, 500

    def _delete_blob_key(self):
        pattern = 'blob-key="(.*)";'
        headers = request.headers['Content-Type']
        match = re.search(pattern, headers)
        if not match:
            return
        key = match.group(1)
        blobstore.delete(key)


def setup_urls(app):
    app.add_url_rule(
        '/api/internal/podcast/',
        methods=['POST'],
        view_func=PodcastAPI.as_view('internal.podcast'))
    app.add_url_rule(
        '/api/internal/podcast/upload/',
        methods=['POST'],
        view_func=AudioFileAPI.as_view('internal.podcast.audio'))
