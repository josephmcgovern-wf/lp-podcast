import os


BASE_BUCKET_URL = 'https://storage.googleapis.com'
BUCKET_NAME = '{}.appspot.com'.format(
    os.environ.get('APPLICATION_ID', 'lp-podcast').lstrip('s~'))
FEED_PATH = 'rss/rss.xml'
