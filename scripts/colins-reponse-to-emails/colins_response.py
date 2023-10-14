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



# email template
OIAR_EMAIL_SENDER: str = 'colin@office-of-incident-assessment-and-response.org.uk'
OIAR_EMAIL_SUBJECT: str = 'Change of email address'
OIAR_EMAIL_TEMPLATE: str = """
<html>
<body>
    <p>
        I've swapped this email to an auto-respond after some smartarse gave my email to spammers.
    </p>

    <p>
        If you're contacting me about work, hold fire. I'm sending everyone the new address a.s.a.p.
    </p>

    <p>
        For everyone else:<br/>
        <b>LEAVE. ME. ALONE. YOU. IRRITATING. GOBSHITES.</b>
    </p>

    <p>
        Zero Regards
    </p>

    <table style="width: 500px; font-size: 11pt; font-family: Arial, sans-serif; border-top: 2px solid #333333;"
    cellspacing="0" cellpadding="0">
    <tbody>
        <tr>
            <td style="width: 100px; padding-right: 10px; vertical-align: top; padding-top: 25px;" rowspan="6" width="100"
            valign="top">
            <a href="https://office-of-incident-assessment-and-response.org.uk/" target="_blank"><img alt="Logo"
                style="width:120px; height:auto; border:0;" src="https://office-of-incident-assessment-and-response.org.uk/assets/email-logo.png" width="77"
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
def main(email):
    """ iterate over the email addresses, render a template per email, rotate logo for each email, send emails """

    try:

        client = boto3.client('ses', region_name='eu-west-1')

        for count, e in enumerate(email):

            msg = MIMEMultipart()
            msg['Subject'] = OIAR_EMAIL_SUBJECT
            msg['From'] = OIAR_EMAIL_SENDER
            msg['To'] = e

            msg.attach(MIMEText(OIAR_EMAIL_TEMPLATE, 'html'))
            print(f'sending email to {e}')
            client.send_raw_email(
                Source=msg['From'],
                Destinations=[msg['To']],
                RawMessage=dict(
                    Data=msg.as_string()
                )
            )
    except Exception as err:
        print(f'error sending email to {e}: {err}')
        sys.exit(1)

if __name__ == "__main__":
    main()




