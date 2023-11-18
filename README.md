# fetch_ses_email
Fetch email from an EC2 S3 bucket fed by Amazon SES.

Based on a code snippet from https://markw.dev/aws-free-email/
This variant drops the email in an inbox in maildir format,
and it adds support for optionally running as root and
writing into some other user's mailbox.
