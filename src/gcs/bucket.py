import cloudstorage as gcs
from werkzeug.utils import secure_filename
from src import config
from src.settings.env_var import EnvVar
from google.appengine.ext import blobstore


class Bucket(object):

    @classmethod
    def create_audio_file_from_blob_key(cls, blob_key):
        blob_info = blobstore.get(blob_key)
        source = blob_info.gs_object_name
        bucket_name = EnvVar.get('bucket_name')
        filename = secure_filename(blob_info.filename)
        destination = '/%s/audio/%s' % (bucket_name, filename)
        """
        f = gcs.open(
            destination, 'w', content_type='audio/mp3',
            options={'x-goog-acl': 'public-read'})
        f.write(blob_info.open().read())
        f.close()
        """
        gcs.copy2(
            source, destination, metadata={
                'x-goog-acl': 'public-read',
                'content-type': 'audio/mp3',
                'content_type': 'audio/mp3'})
        blobstore.delete(blob_key)
        return cls._get_public_link_for_path(destination)

    @classmethod
    def delete_file(cls, path):
        path = cls._get_path_in_bucket(path)
        gcs.delete_file(path)

    @classmethod
    def _get_public_link_for_path(cls, path):
        if path.startswith('/'):
            path = path[1:]
        return '%s/%s' % (config.BASE_BUCKET_URL, path)

    @classmethod
    def get_file_contents(cls, path):
        path = cls._get_path_in_bucket(path)
        f = gcs.open(path)
        data = f.read()
        f.close()
        return data

    @classmethod
    def update_file_contents(cls, path, contents):
        path = cls._get_path_in_bucket(path)
        f = gcs.open(
            path, 'w', content_type='text/xml',
            options={'x-goog-acl': 'public-read'})
        f.write(contents)
        f.close()

    @classmethod
    def _get_path_in_bucket(cls, path):
        bucket_name = EnvVar.get('bucket_name')
        return '/%s/%s' % (bucket_name, path)
