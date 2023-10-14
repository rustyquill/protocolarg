#!/usr/bin/env python

import json
import base64
import os
import re
import boto3
from typing import Dict, List

from emails import load_email_templates, Email
from email.mime.multipart import MIMEMultipart

"""
    react on emails sent to oiar
    incoming emails are routed to an sns topic which executes this lambda


    see the following page for an example sns event
    https://docs.aws.amazon.com/ses/latest/dg/receiving-email-action-lambda-event.html

    and these website for examples how to send emails with boto3
    https://www.learnaws.org/2020/12/18/aws-ses-boto3-guide/
"""

def send_email(message: MIMEMultipart):
    """
    sends an email with boto3 ses
    """

    ses_client = boto3.client('ses')

    response = ses_client.send_raw_email(
        Source=message['From'],
        Destinations=[message['To']],
        RawMessage=dict(
            Data=message.as_string()
        )
    )

    return response


def check_if_lambda_is_active() -> bool:
    """ checks for the env variable EMAIL_AUTO_RESPONDER_IS_ACTIVE """

    return os.getenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'False').lower() in ('true', 1)

def return_recipients_exclusions() -> List[str]:
    """ checks for the env variable EMAIL_AUTO_RESPONDER_RECIPIENTS_EXCLUSION """

    exclusions = os.getenv('EMAIL_AUTO_RESPONDER_RECIPIENTS_EXCLUSION', None)

    if not exclusions:
        return []

    return exclusions.split(',')

def get_mail_event_from_event(event: dict) -> Dict:
    """cuts out the mail event from the sns event"""

    mail_event = event.get('Records', [{}])[0].get('Sns', {}).get('Message', None)

    if not mail_event:
        raise Exception('no mail event found')

    return json.loads(mail_event)


def get_common_header_from_mail_event(event: dict, name: str) -> Dict[str, str]:
    """
    returns the header from the event
    """

    return event.get('mail', {}).get('commonHeaders', {}).get(name, None)

def get_body_from_mail_event(event: dict) -> str:
    """
    returns the body from the event
    """

    body = event.get('content', None)

    if not body:
        raise Exception('no body found')

    # decode base64 encoded body
    try:
        body = base64.b64decode(body).decode('utf-8')
    except BaseException as ex:
        print('Unable to decode body, assuming it is not base64 encoded')

    return body

def get_subject_from_mail_event(event: dict) -> str:
    """
    returns the subject from the event
    """

    subject = get_common_header_from_mail_event(event, 'subject')

    if not subject:
        print('No subject found!')
        return ''

    return subject

def get_sender_from_mail_event(event: dict) -> str:
    """
    returns the sender from the event
    """

    sender = get_common_header_from_mail_event(event, 'from')

    if not sender:
        raise Exception('no sender found')

    # senders are passed as a list, we can assume that there is always only
    # a single address in the list
    sender = sender[0]

    # parse the given sender string and return only the email address
    # a sender can look like this:
    # "Sebastian Hutter <huttersebastian@gmail.com>"
    # or like this
    # huttersebastian@gmail.com
    try:
        return re.search(r'[\w\.-]+@[\w\.-]+', sender).group(0)
    except Exception as ex:
        raise Exception(f'no email address found in sender: {sender}')


def get_recipient_from_mail_event(event: dict) -> str:
    """
    returns the recipient from the event
    """

    recipient = get_common_header_from_mail_event(event, 'to')

    if not recipient:
        raise Exception('no recipient found')

    # recipients are passed as a list, we can assume that there is always only
    # a single address in the list
    recipient = recipient[0]

    # parse the given recipient string and return only the email address
    # a sender can look like this:
    # "Sebastian Hutter <huttersebastian@gmail.com>"
    # or like this
    # huttersebastian@gmail.com
    try:
        return re.search(r'[\w\.-]+@[\w\.-]+', recipient).group(0)
    except Exception as ex:
        raise Exception(f'no email address found in recipient: {recipient}')

    return recipient

def is_email_matching_template(email_template: Email, sender: str, recipient: str, subject: str, body: str) -> bool:
    """
    checks if the given email matches the given template
    """

    return email_template.filters['sender'].matches(sender) and \
        email_template.filters['recipient'].matches(recipient) and \
        email_template.filters['subject'].matches(subject) and \
        email_template.filters['body'].matches(body)

def emit_event(recipient: str, sender: str, subject: str):
    """
    emits log event to cloudwatch
    """

    print(json.dumps(
        dict(
            recipient=recipient,
            sender=sender,
            subject=subject
        )
    ))

def lambda_handler(event, context):
    """
    parse the events received from sns
    retrieve from, to, subject and body
    depending on the recipient, subject and body respond to the email with different
    messagaes
    """

    # exit the lambda immediately if it is not active
    is_active = check_if_lambda_is_active()
    if not check_if_lambda_is_active():
        return

    # load email templates
    email_templates = load_email_templates('emails.yaml')
    if not email_templates:
        raise Exception('no email templates found')

    # parse the email event
    recipients_exclusion = return_recipients_exclusions()
    mail_event = get_mail_event_from_event(event=event)
    body = get_body_from_mail_event(event=mail_event)
    subject = get_subject_from_mail_event(event=mail_event)
    sender = get_sender_from_mail_event(event=mail_event)
    recipient = get_recipient_from_mail_event(event=mail_event)

    # exit the lambda if recipient is in exclusion list
    if recipient in recipients_exclusion:
        print(f'recipient {recipient} is in exclusion list, exiting lambda')
        return

    # iterate over all email templates and check if the received email
    # matches any of the filters. if so send the email and then exit the lambda
    for email_template in email_templates:

        if is_email_matching_template(
            email_template=email_template,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body
        ):
            emit_event(
                sender=recipient,
                recipient=sender,
                subject=email_template.subject,
            )
            send_email(
                message=email_template.message(
                    from_email=recipient,
                    to_email=sender,
                )
            )
            return
