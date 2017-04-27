#! /bin/sh
aws lambda update-function-code --function-name $(basename $(pwd)) --s3-bucket aws-lambda-deployment-packages --s3-key package-$(basename $(pwd))-$(cat VERSION).zip
