import boto3
import tempfile
from werkzeug.utils import secure_filename

from src import config


class Bucket(object):

    @classmethod
    def get_file_contents(cls, path):
        obj = cls._get_file_obj(path)
        return obj.get()['Body'].read()

    @classmethod
    def update_file_contents(cls, path, contents):
        tf = tempfile.TemporaryFile()
        tf.write(contents)
        obj = cls._get_file_obj(path)
        obj.put(Body=tf)

    @classmethod
    def upload_file(cls, file_object):
        bucket = cls._get_bucket()
        name = cls._get_filename(file_object)
        path = 'podcasts/%s' % name
        bucket.upload_fileobj(file_object, path)
        link = cls._get_filepath(path)
        return link

    @classmethod
    def _get_filepath(cls, name):
        return '%s/%s' % (config.BASE_URL, name)

    @classmethod
    def _get_filename(cls, file_object):
        return secure_filename(file_object.filename)

    @classmethod
    def _get_bucket(cls):
        s3 = cls._get_s3()
        bucket = s3.Bucket(config.BUCKET_NAME)
        return bucket

    @classmethod
    def _get_file_obj(cls, path):
        s3 = cls._get_s3()
        obj = s3.Object(config.BUCKET_NAME, path)
        return obj

    @classmethod
    def _get_s3(cls):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=config.AK,
            aws_secret_access_key=config.SK)
        return s3
