import datetime
from flask import request
import json
import re
import uuid
import urllib

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
            if not data.get('audio_filename'):
                raise Exception('Expected audio filename')
            filename = data.pop('audio_filename')
            new_blob = Bucket.transfer_audio_file_to_appropriate_location(filename)
            data['audio_file_url'] = new_blob.public_url
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


class GetSignedUploadUrl(BaseView):

    def get(self):
        filename = urllib.unquote_plus(request.args.get('filename', str(uuid.uuid4())))
        content_type = request.args.get('content_type', '')
        url = Bucket.generate_new_audio_upload_url(filename, content_type=content_type)
        return json.dumps({'url': url})


def setup_urls(app):
    app.add_url_rule(
        '/api/internal/podcast/',
        view_func=PodcastAPI.as_view('internal.podcast'))
    app.add_url_rule(
        '/api/internal/podcast/generate_upload_url/',
        view_func=GetSignedUploadUrl.as_view('internal.podcast.generate_upload_url'))

