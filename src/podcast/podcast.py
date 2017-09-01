from datetime import datetime
import math
import xml.etree.ElementTree as ET
from xml.dom import minidom

from google.appengine.ext import ndb

from src.aws.bucket import Bucket
from src.settings.env_var import EnvVar


class Podcast(ndb.Model):
    audio_file_length = ndb.IntegerProperty(required=True)
    audio_file_url = ndb.StringProperty(required=True)
    date_recorded = ndb.DateProperty(required=True)
    duration = ndb.FloatProperty(required=True)
    description = ndb.TextProperty(required=True)
    name = ndb.StringProperty(required=True)
    subtitle = ndb.StringProperty(required=True)
    time_created = ndb.DateTimeProperty(auto_now_add=True)

    @property
    def duration_string(self):
        seconds = int(round(self.duration % 60))
        total_minutes = int(math.floor(self.duration / 60))
        minutes = int(total_minutes % 60)
        hours = int(math.floor(total_minutes / 60))
        minutes_str = str(minutes)
        if minutes < 10:
            minutes_str = '0' + minutes_str
        seconds_str = str(seconds)
        if seconds < 10:
            seconds_str = '0' + seconds_str
        return '%s:%s:%s' % (hours, minutes_str, seconds_str)

    @property
    def published_date_string(self):
        year = self.date_recorded.year
        month = self.date_recorded.month
        day = self.date_recorded.day
        date = datetime(year, month, day, 11, 30)
        return date.strftime('%a, %d %b %Y %H:%M:%S CST')

    @classmethod
    def sync_feed_with_datastore(cls, ignore=[]):
        path = EnvVar.get('feed_path')
        contents = Bucket.get_file_contents(path)
        cls._prep_element_tree()
        tree = ET.fromstring(contents)
        channel = tree.find('channel')
        existing_podcasts = channel.findall('item')
        for existing_podcast in existing_podcasts:
            channel.remove(existing_podcast)
        podcasts = Podcast.query().fetch()
        for podcast in podcasts:
            if podcast in ignore:
                continue
            channel.append(podcast.convert_to_xml())
        ugly_xml = ET.tostring(tree).replace('\n', '')
        xml = minidom.parseString(ugly_xml).toprettyxml(indent="  ").encode(
            'utf-8')
        Bucket.update_file_contents(path, xml)

    @classmethod
    def _prep_element_tree(cls):
        ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
        ET.register_namespace(
            'itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        ET.register_namespace('itunesu', 'http://www.itunesu.com/feed')

    def add_to_rss_feed(self):
        path = EnvVar.get('feed_path')
        contents = Bucket.get_file_contents(path)
        self._prep_element_tree()
        tree = ET.fromstring(contents)
        channel = tree.find('channel')
        channel.append(self.convert_to_xml())
        ugly_xml = ET.tostring(tree).replace('\n', '')
        xml = minidom.parseString(ugly_xml).toprettyxml(indent="  ").encode(
            'utf-8')
        Bucket.update_file_contents(path, xml)

    def convert_to_xml(self):
        root = ET.Element('item')
        ET.SubElement(root, 'title').text = self.name
        ET.SubElement(root, 'description').text = self.description
        ET.SubElement(root, 'itunes:summary').text = self.description
        ET.SubElement(root, 'itunes:subtitle').text = self.subtitle
        ET.SubElement(root, 'itunes:explicit').text = 'no'
        ET.SubElement(
            root, 'enclosure', url=self.audio_file_url, type='audio/mpeg',
            length=str(self.audio_file_length))
        ET.SubElement(root, 'guid').text = self.audio_file_url
        ET.SubElement(root, 'itunes:duration').text = self.duration_string
        ET.SubElement(root, 'pubDate').text = self.published_date_string
        return root

    def edit(self, **kwargs):
        for k, v in kwargs:
            if hasattr(self, k):
                setattr(self, k, v)
        self.put()
        self.sync_feed_with_datastore()

    def delete(self):
        self.sync_feed_with_datastore(ignore=[self])
        audio_file_path = self._get_audio_file_path()
        Bucket.delete_file(audio_file_path)
        self.key.delete()

    def _get_audio_file_path(self):
        bucket_name = EnvVar.get('bucket_name')
        formatted_bucket_name = '/%s/' % bucket_name
        parts = self.audio_file_url.split(formatted_bucket_name)
        return parts[-1]

    def serialize(self):
        data = self._to_dict()
        data['id'] = self.key.id()
        if self.time_created:
            data['time_created'] = self.time_created.isoformat()
        if self.date_recorded:
            data['date_recorded'] = self.date_recorded.isoformat()
        return data
