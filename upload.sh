#! /bin/sh
aws s3 cp package-$(basename $(pwd))-$(cat VERSION).zip s3://aws-lambda-deployment-packages
