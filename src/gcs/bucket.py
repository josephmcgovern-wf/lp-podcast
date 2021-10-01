import uuid
from datetime import timedelta

from google.auth.transport import requests
from google.auth import compute_engine
from google.cloud import storage

from src import config


class Bucket(object):
    @classmethod
    def transfer_audio_file_to_appropriate_location(cls, filename):
        bucket = cls._bucket_client()
        blob = bucket.blob(filename)
        dest = "audio/{}-{}".format(str(uuid.uuid4()), filename)
        new_blob = bucket.rename_blob(blob, dest)
        new_blob.acl.save_predefined("public-read")
        return new_blob

    @classmethod
    def generate_new_audio_upload_url(cls, filename, content_type=None):
        client = cls._bucket_client()
        auth_request = requests.Request()
        signing_credentials = compute_engine.IDTokenCredentials(auth_request, "")
        return client.blob(filename, chunk_size=262144 * 5).generate_signed_url(
            expiration=timedelta(hours=1),
            method="PUT",
            content_type=content_type,
            credentials=signing_credentials,
        )

    @classmethod
    def delete_file(cls, path):
        bucket = cls._bucket_client()
        blob = bucket.blob(path)
        blob.delete()

    @classmethod
    def _get_public_link_for_path(cls, path):
        if path.startswith("/"):
            path = path[1:]
        return "%s/%s" % (config.BASE_BUCKET_URL, path)

    @classmethod
    def get_file_contents(cls, path):
        bucket = cls._bucket_client()
        blob = bucket.blob(path)
        return blob.download_as_string()

    @classmethod
    def update_file_contents(cls, path, contents, content_type=None):
        bucket = cls._bucket_client()
        blob = bucket.blob(path)
        blob.upload_from_string(
            contents, content_type=content_type, predefined_acl="public-read"
        )

    @staticmethod
    def _bucket_client():
        storage_client = storage.Client()
        return storage_client.bucket(config.BUCKET_NAME)
