#! /bin/sh
NAME=$(basename $(pwd))
PACKAGE=package-$NAME-$(cat VERSION).zip
pip3 install --requirement requirements.txt --target .
zip -r $PACKAGE VERSION bs1770gain ffmpeg ffprobe tagit youtube_dl handler.py
aws lambda update-function-code --function-name $NAME --zip-file fileb://$PACKAGE
