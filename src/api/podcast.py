from flask import request
from flask.views import MethodView
import json
from src.aws.bucket import Bucket

from src.podcast.podcast import Podcast


class PodcastAPI(MethodView):

    def post(self):
        data = request.get_json()
        p = Podcast(**data)
        try:
            p._check_initialized()
        except Exception as e:
            import traceback
            print e.message
            print traceback.format_exc()
            return e.message, 400
        p.put()
        p.add_to_rss_feed()
        '''
        audio = request.files.get('audioFile')
        s3 = boto3.resource(
            's3',
            aws_access_key_id='AKIAJ27FDLGCOSSHLJPQ',
            aws_secret_access_key='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')
        bucket = s3.Bucket('podcast-testing')
        fname = secure_filename(audio.filename)
        bucket.upload_fileobj(audio, 'podcasts/%s' % fname)
        '''
        return 'Success', 200


class AudioFileAPI(MethodView):

    def post(self):
        try:
            f = request.files['audioFile']
            link = Bucket.upload_file(f)
            return json.dumps({'url': link})
        except Exception as e:
            return e.message, 500


def setup_urls(app):
    app.add_url_rule(
        '/api/internal/podcast/',
        methods=['POST'],
        view_func=PodcastAPI.as_view('internal.podcast'))
    app.add_url_rule(
        '/api/internal/podcast/upload/',
        methods=['POST'],
        view_func=AudioFileAPI.as_view('internal.podcast.audio'))
