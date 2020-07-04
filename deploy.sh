#! /bin/sh
NAME=$(basename $(pwd))
PREFIX=package-
PACKAGE=$PREFIX$NAME-$(cat VERSION).zip
BINARIES="bs1770gain/bs1770gain ffmpeg ffprobe tagit"
FILES="bs1770gain/ youtube_dl/ VERSION ffmpeg ffprobe tagit handler.py"

# INFO: `youtube-dl` can't find/use non-executable binaries.
chmod -v +x $BINARIES

rm -vrf youtube_dl*
pip3 install --requirement requirements.txt --target .

rm -vf $PREFIX*.zip
zip -r $PACKAGE $FILES

aws lambda update-function-code --function-name $NAME --zip-file fileb://$PACKAGE
