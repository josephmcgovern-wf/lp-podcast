from flask import Flask
from src.api.podcast import setup_urls as api_podcast_setup_urls
from src.views.upload import setup_urls as upload_setup_urls
from src.views.index import setup_urls as index_setup_urls
from src.views.history import setup_urls as history_setup_urls

app = Flask(__name__)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.secret_key = 'MySuperSecretKey'

index_setup_urls(app)
upload_setup_urls(app)
api_podcast_setup_urls(app)
history_setup_urls(app)
