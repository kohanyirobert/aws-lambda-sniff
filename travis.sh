#! /bin/sh
pip3 install --requirement requirements.txt --target .
zip -r package-$(basename $(pwd))-$(cat VERSION).zip VERSION bs1770gain ffmpeg ffprobe tagit youtube_dl handler.py
aws lambda update-function-code --function-name $(basename $(pwd)) --zip-file fileb://package-$(basename $(pwd))-$(cat VERSION).zip
