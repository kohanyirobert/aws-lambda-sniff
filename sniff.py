import os
import youtube_dl
import boto3
from subprocess import call
from pathlib import Path

os.environ['PATH'] += os.pathsep + os.getcwd()


class HandlerLogger:

    PREFIX = '[ffmpeg] Destination: '

    def debug(self, msg):
        if msg.startswith(self.PREFIX):
            self.audiopath = Path(msg[len(self.PREFIX):])

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


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
        'logger': logger,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        ydl.process_ie_result(info, download=True)

    return logger.audiopath


def add_artist_and_title_tags(audiopath, artist, title):
    call(['tagit', 'c', str(audiopath)])
    call(['tagit', 'i', 'ARTIST', artist, str(audiopath)])
    call(['tagit', 'i', 'TITLE', title, str(audiopath)])


def add_replaygain_tags(audiopath, work_dir):
    tmp_dir = work_dir / 'tmp'

    call([
        'bs1770gain/bs1770gain',
        '--replaygain',
        '--output',
        str(tmp_dir),
        str(audiopath),
    ])

    call([
        'mv',
        str(tmp_dir / audiopath.name),
        str(audiopath),
    ])


def get_final_filename(audiopath, artist, title):
    return '{} - {}{}'.format(artist, title, audiopath.suffix)


def upload_to_s3(audiopath, filename):
    s3 = boto3.resource('s3')
    with audiopath.open('rb') as f:
        s3.meta.client.upload_file(str(audiopath), os.environ['BUCKET'], filename)


def handler(event, context):
    work_dir = Path(event['work_dir'])
    url = event['url']
    artist = event['artist']
    title = event['title']

    audiopath = download_and_get_audio_path(work_dir, url)
    add_artist_and_title_tags(audiopath, artist, title)
    add_replaygain_tags(audiopath, work_dir)
    filename = get_final_filename(audiopath, artist, title)
    upload_to_s3(audiopath, filename)

    return None


if __name__ == '__main__':
    os.environ['BUCKET'] = 'aws-lambda-sniff'
    handler({
        'work_dir': '/tmp',
        'url': 'https://www.youtube.com/watch?v=5rc7pqdcbK4',
        'artist': 'test artist',
        'title': 'test title',
    }, None)
