import datetime
from flask import request
import json
import re

from src.gcs.bucket import Bucket
from src.podcast.podcast import Podcast
from src.views.base_view import BaseView


class PodcastAPI(BaseView):

    def get(self):
        podcasts = sorted(Podcast.fetch_all(), key=lambda x: x['date_recorded'], reverse=True)
        for p in podcasts:
            p['date_recorded'] = p['date_recorded'].strftime('%Y-%m-%d')
        return json.dumps({'podcasts': podcasts}), 200

    def delete(self):
        data = request.get_json()
        if not data['episode_id']:
            return 'Podcast id required', 400
        Podcast.delete_episode(data['episode_id'])
        return 'Success', 202

    def put(self):
        data = request.get_json()
        podcast_data = data.get('podcast_data')
        if not podcast_data:
            return 'podcast_data required', 400
        prev_podcast_data = dict(podcast_data)
        podcast_data = self._cleanup_data(podcast_data)
        podcast_id = podcast_data.pop('id')
        Podcast.edit_episode(podcast_id, **podcast_data)
        return json.dumps({'podcast': prev_podcast_data}), 200

    def _cleanup_data(self, data):
        if data.get('date_recorded'):
            data['date_recorded'] = datetime.datetime.strptime(
                data['date_recorded'], '%Y-%m-%d').date()
        return data

    def post(self):
        data = request.get_json()
        data['date_recorded'] = self._get_date(data.get('date_recorded'))
        try:
            Podcast.add_episode(data)
        except Exception as e:
            return e.message, 400
        return 'Success', 200

    def _get_date(self, date_str):
        if not date_str:
            return None
        elements = date_str.split('-')
        if len(elements) != 3:
            return None
        try:
            year, month, date = elements
            return datetime.date(int(year), int(month), int(date))
        except:
            return None


class AudioFileAPI(BaseView):

    def post(self):
        try:
            key = self._get_blob_key()
            link = Bucket.create_audio_file_from_blob_key(key)
            return json.dumps({'url': link})
        except Exception as e:
            return e.message, 500

    def _get_blob_key(self):
        pattern = 'blob-key=(.*)$'
        f = request.files['audioFile']
        if not f:
            return None
        headers = f.headers['Content-Type']
        match = re.search(pattern, headers)
        if not match:
            return None
        key = match.group(1)
        return key


def setup_urls(app):
    app.add_url_rule(
        '/api/internal/podcast/',
        view_func=PodcastAPI.as_view('internal.podcast'))
    app.add_url_rule(
        '/api/internal/podcast/<int:podcast_id>/',
        view_func=PodcastAPI.as_view('internal.podcast.specific'))
    app.add_url_rule(
        '/api/internal/podcast/upload/',
        methods=['POST'],
        view_func=AudioFileAPI.as_view('internal.podcast.audio'))
