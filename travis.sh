#! /bin/sh
NAME=$(basename $(pwd))
PACKAGE_PREFIX=package-
PACKAGE=$PACKAGE_PREFIX$NAME-$(cat VERSION).zip

rm -vrf youtube_dl*
pip3 install --requirement requirements.txt --target .

rm -vf $PACKAGE_PREFIX*.zip
zip -r $PACKAGE VERSION bs1770gain ffmpeg ffprobe tagit youtube_dl handler.py

aws lambda update-function-code --function-name $NAME --zip-file fileb://$PACKAGE
