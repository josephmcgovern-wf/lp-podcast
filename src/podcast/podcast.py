import logging
import math
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom

from google.appengine.ext import ndb

from src import config
from src.gcs.bucket import Bucket
from src.settings.env_var import EnvVar


class Podcast(ndb.Model):
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'itunesu': 'http://www.itunesu.com/feed',
    }
    PUBLISHED_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S CST'
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
    def fetch_all(cls):
        tree = cls._xml_tree()
        channel = tree.find('channel')
        return [
            cls._convert_element_to_dict(i) for i in
            channel.findall('item')
        ]

    @classmethod
    def _write_tree(cls, tree):
        logging.debug("Updating feed...")
        ugly_xml = ET.tostring(tree).replace('\n', '')
        xml = minidom.parseString(ugly_xml).toprettyxml(indent="  ").encode(
            'utf-8')
        Bucket.update_file_contents(config.FEED_PATH, xml)

    @classmethod
    def add_episode(cls, episode_data):
        tree = cls._xml_tree()
        channel = tree.find('channel')
        channel.append(cls._convert_dict_to_element(episode_data))
        cls._write_tree(tree)

    @classmethod
    def edit_episode(
            cls, episode_id, name=None, description=None, subtitle=None, date_recorded=None):
        tree = cls._xml_tree()
        channel = tree.find('channel')
        for item in channel.findall('item'):
            if item.find('guid').text == episode_id:
                if name:
                    item.find('title').text = name
                if description:
                    item.find('description').text = description
                    item.find('itunes:summary', cls.NAMESPACES).text = description
                if subtitle:
                    item.find('itunes:subtitle', cls.NAMESPACES).text = subtitle
                if date_recorded:
                    time_published = datetime(
                        date_recorded.year,
                        date_recorded.month,
                        date_recorded.day,
                        11,
                        30
                    )
                    item.find('pubDate').text = time_published.strftime(cls.PUBLISHED_DATE_FORMAT)
                break
        cls._write_tree(tree)

    @classmethod
    def delete_episode(cls, episode_id):
        # Remove episode from rss feed
        audio_file_url = None
        tree = cls._xml_tree()
        channel = tree.find('channel')
        for item in channel.findall('item'):
            if item.find('guid').text == episode_id:
                audio_file_url = item.find('enclosure').attrib['url']
                channel.remove(item)
                logging.debug("Found episode and removed it from tree!")
                break
        else:
            raise Exception('No episode found with id {}'.format(episode_id))
        cls._write_tree(tree)

        logging.debug("Deleting audio file...")
        # Delete audio file from bucket
        bucket_name = EnvVar.get('bucket_name')
        formatted_bucket_name = '/{}/'.format(bucket_name)
        parts = audio_file_url.split(formatted_bucket_name)
        audio_filepath = parts[-1]
        Bucket.delete_file(audio_filepath)

    @classmethod
    def _convert_element_to_dict(cls, element):
        def getvalue(element, value, namespaces=None):
            namespaces = namespaces or {}
            return element.find(value, namespaces).text

        audio_file_info = element.find('enclosure').attrib
        return {
            'name': getvalue(element, 'title'),
            'description': getvalue(element, 'description'),
            'subtitle': getvalue(element, 'itunes:subtitle', namespaces=cls.NAMESPACES),
            'audio_file_url': audio_file_info['url'],
            'audio_file_length': audio_file_info['length'],
            'id': audio_file_info['url'],
            'date_recorded': datetime.strptime(
                getvalue(element, 'pubDate'), cls.PUBLISHED_DATE_FORMAT)
        }

    @classmethod
    def _convert_dict_to_element(cls, data):
        root = ET.Element('item')
        ET.SubElement(root, 'title').text = data['name']
        ET.SubElement(root, 'description').text = data['description']
        ET.SubElement(root, 'itunes:summary').text = data['description']
        ET.SubElement(root, 'itunes:subtitle').text = data['subtitle']
        ET.SubElement(root, 'itunes:explicit').text = 'no'
        ET.SubElement(
            root, 'enclosure', url=data['audio_file_url'], type='audio/mpeg',
            length=str(data['audio_file_length']))
        ET.SubElement(root, 'guid').text = data['audio_file_url']
        ET.SubElement(root, 'itunes:duration').text = cls._formatted_duration(data['duration'])
        time_published = datetime(
            data['date_recorded'].year,
            data['date_recorded'].month,
            data['date_recorded'].day,
            11,
            30
        )
        ET.SubElement(root, 'pubDate').text = time_published.strftime(
            cls.PUBLISHED_DATE_FORMAT)
        return root

    @staticmethod
    def _formatted_duration(duration):
        seconds = int(round(duration % 60))
        total_minutes = int(math.floor(duration / 60))
        minutes = int(total_minutes % 60)
        hours = int(math.floor(total_minutes / 60))
        minutes_str = str(minutes)
        if minutes < 10:
            minutes_str = '0' + minutes_str
        seconds_str = str(seconds)
        if seconds < 10:
            seconds_str = '0' + seconds_str
        return '%s:%s:%s' % (hours, minutes_str, seconds_str)

    @classmethod
    def _xml_tree(cls):
        contents = Bucket.get_file_contents(config.FEED_PATH)
        ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
        ET.register_namespace(
            'itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        ET.register_namespace('itunesu', 'http://www.itunesu.com/feed')
        tree = ET.fromstring(contents)
        return tree
