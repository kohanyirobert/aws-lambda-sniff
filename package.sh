#! /bin/sh
rm -vf package-*.zip
zip -r package-$(basename $(pwd))-$(cat VERSION).zip VERSION bs1770gain ffmpeg ffprobe tagit youtube_dl handler.py
