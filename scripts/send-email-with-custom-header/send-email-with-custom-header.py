#!/usr/bin/env python3

"""
 send one time oiar emails with "broken" oiar logo
 to a list of players
"""

import boto3
import sys
import base64

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase



# email template
EMAIL_SENDER: str = 'admin@bonzobazaar.co.uk'
EMAIL_SUBJECT: str = ''
EMAIL_TEMPLATE: str = ''
# lady mowbrays account
EMAIL_RECIPIENT: str = '14dym0w8r4y@proton.me'

EMAIL_CUSTOM_HEADER_NAME: str = 'X-BNZBZR-CLAVIS'
EMAIL_CUSTOM_HEADER_VALUE: str = base64.b64encode(b'allisbonzomerch').decode('utf-8')

def main():
    """ iterate over the email addresses, render a template per email, rotate logo for each email, send emails """

    try:

        client = boto3.client('ses', region_name='eu-west-1')

        msg = MIMEMultipart()
        msg['Subject'] = EMAIL_SUBJECT
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        msg[EMAIL_CUSTOM_HEADER_NAME] = EMAIL_CUSTOM_HEADER_VALUE

        msg.attach(MIMEText(EMAIL_TEMPLATE, 'html'))
        print(f'sending email to {EMAIL_RECIPIENT}')
        client.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']],
            RawMessage=dict(
                Data=msg.as_string()
            )
        )
    except Exception as err:
        print(f'error sending email to {EMAIL_RECIPIENT}: {err}')
        sys.exit(1)

if __name__ == "__main__":
    main()




