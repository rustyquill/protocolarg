#!/usr/bin/env python3

"""
 send one time oiar emails with "broken" oiar logo
 to a list of players
"""

import click
from typing import List
import boto3
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase


OIAR_EMAIL_LOGOS: List[str] = [
    'assets/1bf9e1ad-1645-4db1-97a4-13245d644fe5.png',
    'assets/c5827104-fa7d-41ad-81e5-f09e150347d8.png',
]

# email template
OIAR_EMAIL_SENDER: str = 'noreply@office-of-incident-assessment-and-response.org.uk'
OIAR_EMAIL_SUBJECT: str = 'Automated Response: Message Review Outcome'
OIAR_EMAIL_TEMPLAT: str = """
<html>
<body>
    <p>
        Dear [Recipient's Name],
    </p>
    <p>
        Thank you for your recent correspondence with the O.I.A.R.
    </p>
    <p>
        After careful consideration, we have reviewed your message dated [Date of Message]. It is the policy of the O.I.A.R. to ensure that all communications we engage in are constructive and directly pertain to our stated mission and objectives.
    </p>
    <p>
        Upon thorough review, we have determined that the content of your message does not provide the necessary value for further discussion or action on our part.
    <p>
        Thank you for your attention,
        The O.I.A.R. Team
    </p>
    <table style="width: 500px; font-size: 11pt; font-family: Arial, sans-serif; border-top: 2px solid #333333;"
    cellspacing="0" cellpadding="0">
    <tbody>
        <tr>
            <td style="width: 100px; padding-right: 10px; vertical-align: top; padding-top: 25px;" rowspan="6" width="100"
            valign="top">
            <a href="https://office-of-incident-assessment-and-response.org.uk/" target="_blank"><img alt="Logo"
                style="width:120px; height:auto; border:0;" src="{url}/{logo}" width="77"
                border="0"></a>
            </td>
            <td style="padding-left:10px; font-size: 10pt; font-family: Arial, sans-serif; padding-top: 15px;">
                <table cellspacing="0" cellpadding="0">
                    <tbody>
                        <tr>
                            <td colspan="2"
                            style="font-size: 10pt; color:#0079ac; font-family: Arial, sans-serif; width: 400px; vertical-align: top;"
                            valign="top">
                            <strong><span>Realise, Report and Respond with the O.I.A.R.</span></strong>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2"
                        style="font-size: 10pt; font-family: Arial, sans-serif; padding-bottom: 5px; vertical-align: top; line-height:17px;"
                        valign="top">
                        <span><br>
                            <span>
                                <span style="font-size: 10pt; font-family: Arial, sans-serif; color: #333333;">Office of Incident,
                                    Assessment, and Response</span><br>
                                    <span style="font-size: 10pt; font-family: Arial, sans-serif; color: #333333;">Royal Mint Court,
                                        London</span><br>
                                        <span style="font-size: 10pt; font-family: Arial, sans-serif; color: #333333;">EC3N 4QN, United
                                            Kingdom</span>
                                        </span>
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td style="font-weight:bold; color: #0079ac; width:200px; height:19px; padding-top: 10px;" width="200">
                                    <span
                                    style="font-weight:bold; font-size: 8pt; color: #0079ac; width:200px; height:19px; padding-top: 10px;">
                                    <a href="https://office-of-incident-assessment-and-response.org.uk/" target="_blank"
                                    style="text-decoration:none;">https://office-of-incident-assessment-and-response.org.uk</a>
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2"
                            style="font-size: 10pt; font-family: Arial, sans-serif; padding-bottom: 5px; vertical-align: top; line-height:17px; font-style: italic;"
                            valign="top">
                            <span><br>
                                <span>
                                    <span style="font-size: 6pt; font-family: Arial, sans-serif; color: #333333;">In accordance with
                                        governmental guidelines we encourage you to consider the environmental impact before printing
                                        this email.</span><br>
                                    </span>
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
    </tbody>
</table>
</body>
</html>
"""


@click.command()
@click.option('--email', '-e', help='List of emails to send emails too', required=True, multiple=True, default=[])
@click.option('--url', help='The base host serving the pictures for the oiar', default='https://office-of-incident-assessment-and-response.org.uk')
def main(email, url):
    """ iterate over the email addresses, render a template per email, rotate logo for each email, send emails """

    try:

        client = boto3.client('ses', region_name='eu-west-1')

        for count, e in enumerate(email):
            logo = OIAR_EMAIL_LOGOS[count % len(OIAR_EMAIL_LOGOS)]
            template = OIAR_EMAIL_TEMPLAT.format(url=url, logo=logo)

            msg = MIMEMultipart()
            msg['Subject'] = OIAR_EMAIL_SUBJECT
            msg['From'] = OIAR_EMAIL_SENDER
            msg['To'] = e

            msg.attach(MIMEText(template, 'html'))
            print(f'sending email to {e} with logo {url}/{logo}')
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




