import sys
import locale
import re
import os
import youtube_dl
import boto3
from xml.etree import ElementTree
from subprocess import check_call, check_output
from pathlib import Path

print('defaultencoding', sys.getdefaultencoding())
print('filesystemencoding', sys.getfilesystemencoding())
print('preferredencoding', locale.getpreferredencoding())

VERSION_TAG_NAME = 'AWS_LAMBDA_SNIFF'
VERSION_TAG_VALUE = None
with Path('VERSION').open() as f:
    VERSION_TAG_VALUE = f.read().strip()

NORMALIZE_FILENAME_SRC = os.environ['NORMALIZE_FILENAME_SRC']
NORMALIZE_FILENAME_DST = os.environ['NORMALIZE_FILENAME_DST']
NORMALIZE_FILENAME_DEL = os.environ['NORMALIZE_FILENAME_DEL']
NORMALIZE_FILENAME = str.maketrans(NORMALIZE_FILENAME_SRC, NORMALIZE_FILENAME_DST, NORMALIZE_FILENAME_DEL)

os.environ['PATH'] += os.pathsep + os.getcwd()


class HandlerLogger:

    PATTERNS = [
        re.compile(r'\[ffmpeg\] Destination: (?P<audiopath>.*)'),
        re.compile(
            r'\[ffmpeg\] Post-process file (?P<audiopath>.*) exists, skipping'),
    ]

    def debug(self, msg):
        print(msg)
        for pattern in self.PATTERNS:
            match = pattern.match(msg)
            if match:
                self.audiopath = Path(match.group('audiopath'))

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def download_and_get_audio_path(work_dir, url):
    logger = HandlerLogger()

    ydl_opts = {
        'verbose': True,
        'format': 'bestaudio/best',
        'outtmpl': str(work_dir / '%(id)s%(ext)s.%(ext)s'),
        'cachedir': str(work_dir),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'best',
            'preferredquality': 'best',
        }],
        'postprocessor_args': [
            '-fflags', 'bitexact',
        ],
        'logger': logger,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        ydl.process_ie_result(info, download=True)

    return logger.audiopath


def add_tags(audiopath, tags):
    check_call(['tagit', 'c', str(audiopath)])
    for tag_name, tag_value in tags.items():
        check_call(['tagit', 'i', tag_name, tag_value, str(audiopath)])


def add_vesion_tag(audiopath):
    check_call(['tagit', 'i', VERSION_TAG_NAME, VERSION_TAG_VALUE, str(audiopath)])


def add_replaygain_tags(audiopath):
    xml = ElementTree.fromstring(check_output([
        'bs1770gain/bs1770gain',
        '--replaygain',
        '--xml',
        str(audiopath),
    ]))

    track_gain = xml.find('./album/track/integrated').attrib['lu']
    album_gain = xml.find('./album/summary/integrated').attrib['lu']

    check_call(['tagit', 'i', 'REPLAYGAIN_ALGORITHM', 'ITU-R BS.1770', str(audiopath)])
    check_call(['tagit', 'i', 'REPLAYGAIN_REFERENCE_LOUDNESS', '-18.00', str(audiopath)])
    check_call(['tagit', 'i', 'REPLAYGAIN_TRACK_GAIN', '{} dB'.format(track_gain), str(audiopath)])
    check_call(['tagit', 'i', 'REPLAYGAIN_ALBUM_GAIN', '{} dB'.format(album_gain), str(audiopath)])


def get_final_filename(audiopath, artist, title):
    filename = '{} - {}{}'.format(artist, title, audiopath.suffix)
    return filename.translate(NORMALIZE_FILENAME)


def upload_to_s3(audiopath, bucket, filename):
    s3 = boto3.resource('s3')
    with audiopath.open('rb') as f:
        s3.meta.client.upload_file(str(audiopath), bucket, filename)


def handler(event, context):
    print('event', event)

    work_dir = Path(os.environ['WORK_DIR'])
    bucket = os.environ['BUCKET']
    url = event['url']
    tags = event['tags']
    artist = tags['ARTIST']
    title = tags['TITLE']

    audiopath = download_and_get_audio_path(work_dir, url)
    add_tags(audiopath, tags)
    add_vesion_tag(audiopath)
    add_replaygain_tags(audiopath)
    filename = get_final_filename(audiopath, artist, title)
    upload_to_s3(audiopath, bucket, filename)

    return None
