#!/usr/bin/env python3

"""
 send one time oiar emails with "broken" oiar logo
 to a list of players
"""

import click
from typing import List
import boto3
import sys
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase


# email template
OIAR_EMAIL_SENDER: str = 'dokumente@freiheitentschluesseln.de'
OIAR_EMAIL_SUBJECT: str = ''
OIAR_EMAIL_TEMPLAT: str = '''
<html>
    <head>
        <style type="text/css">
            .main {
                width: 512px;
                height: 512px;
            }
        </style>
    </head>
<body>
    <div class="main">
        <img src="https://freiheitentschluesseln.de/_6A1F7106A_$.gif" widht="100%" height="100%" />
    </div>
</body>
</html>
'''


@click.command()
@click.option('--email', '-e', help='List of emails to send emails too', required=True, multiple=True, default=[])
@click.option('--url', help='The base host serving the pictures for the oiar', default='https://office-of-incident-assessment-and-response.org.uk')
def main(email, url):
    """ iterate over the email addresses, render a template per email, rotate logo for each email, send emails """

    try:

        client = boto3.client('ses', region_name='eu-west-1')
        for count, e in enumerate(email):
            template = OIAR_EMAIL_TEMPLAT#.format(url=url, logo=logo)

            msg = MIMEMultipart()
            msg['Subject'] = OIAR_EMAIL_SUBJECT
            msg['From'] = OIAR_EMAIL_SENDER
            msg['To'] = e

            msg.attach(MIMEText(template, 'html'))

            client.send_raw_email(
                Source=msg['From'],
                Destinations=[msg['To']],
                RawMessage=dict(
                    Data=msg.as_string()
                )
            )
    except Exception as e:
        print(f'error sending email to {e}: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()




