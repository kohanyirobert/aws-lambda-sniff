#! /bin/sh
bucket=aws-lambda-deployment-packages
key=package-$(basename $(pwd))-$(cat VERSION).zip
aws s3api head-object --bucket $bucket --key $key
if [ $? -ne 0 ]
then
  aws s3 cp $key s3://$bucket
else
  echo $key already exists
fi
