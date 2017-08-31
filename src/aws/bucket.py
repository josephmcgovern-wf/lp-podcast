import boto3
from werkzeug.utils import secure_filename

from src import config
from src.settings.env_var import EnvVar


class Bucket(object):

    @classmethod
    def get_file_contents(cls, path):
        obj = cls._get_file_obj(path)
        return obj.get()['Body'].read()

    @classmethod
    def update_file_contents(cls, path, contents):
        obj = cls._get_file_obj(path)
        obj.put(Body=contents, ACL='public-read')

    @classmethod
    def upload_file(cls, blob):
        bucket = cls._get_bucket()
        name = secure_filename(blob.filename)
        path = 'audio/%s' % name
        bucket.put_object(
            ACL='public-read',
            Key=path,
            Body=blob.open().read(),
            ContentType=blob.content_type,
        )
        link = cls._get_filepath(path)
        return link

    @classmethod
    def _get_filepath(cls, name):
        bucket_name = EnvVar.get('bucket_name')
        return '%s/%s/%s' % (config.BASE_URL, bucket_name, name)

    @classmethod
    def _get_bucket(cls):
        s3 = cls._get_s3()
        bucket_name = EnvVar.get('bucket_name')
        bucket = s3.Bucket(bucket_name)
        return bucket

    @classmethod
    def _get_file_obj(cls, path):
        s3 = cls._get_s3()
        bucket_name = EnvVar.get('bucket_name')
        obj = s3.Object(bucket_name, path)
        return obj

    @classmethod
    def _get_s3(cls):
        ak = EnvVar.get('s3_access_key')
        sk = EnvVar.get('s3_secret_key')
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ak,
            aws_secret_access_key=sk)
        return s3
