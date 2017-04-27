import os
import sniff

if __name__ == '__main__':
    os.environ['BUCKET'] = 'aws-lambda-sniff'
    sniff.handler({
        'work_dir': '/tmp',
        'url': 'https://www.youtube.com/watch?v=5rc7pqdcbK4',
        'artist': 'test artist',
        'title': 'test title',
    }, None)
