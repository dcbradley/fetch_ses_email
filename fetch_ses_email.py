#!/usr/bin/env python3
import boto3
import mailbox
import argparse
import pathlib
import os
import pwd
import sys

parser = argparse.ArgumentParser(
    description='Fetch email from an EC2 S3 bucket fed by Amazon SES.',
    epilog='Use Amazon boto3 configuration and environment to authenticate to S3.'
)
parser.add_argument('bucket_name')
parser.add_argument('--user',default=os.getlogin(),required=False)
args = parser.parse_args()

s3_bucket = args.bucket_name

# Create s3 client
client = boto3.client('s3')

# Get new mail
response = client.list_objects_v2(
    Bucket=s3_bucket,
    Delimiter=','
)

if not ('Contents' in response):
    sys.exit(0)

new_messages = [msg['Key'] for msg in response['Contents'] if not msg['Key'].startswith('processed/')]

if args.user != os.getlogin():
    p = pwd.getpwnam(args.user)
    if not p:
        sys.stderr.write("Failed to find user with name " + args.user)
        sys.exit(1)
    os.setuid(p.pw_uid)
    homedir = p.pw_dir
else:
    homedir = str(pathlib.Path.home())

maildir = homedir + "/Maildir"

if new_messages:
    inbox = mailbox.Maildir(maildir)

    s3 = boto3.resource('s3')
    for i in new_messages:
        try:
            message_content = s3.Object(s3_bucket, i).get()['Body'].read().decode()
        except UnicodeDecodeError:
            message_content = s3.Object(s3_bucket, i).get()['Body'].read().decode('cp1252')

        inbox.add(message_content)

        #s3.Object(s3_bucket,f"processed/{i}").copy_from(CopySource=f"{s3_bucket}/{i}")
        s3.Object(s3_bucket,i).delete()
