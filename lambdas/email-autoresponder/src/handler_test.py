#!/usr/bin/env python3

import pytest
import json
import boto3
from moto import mock_ses
from moto.ses import ses_backends
from moto.core import DEFAULT_ACCOUNT_ID
from handler import get_mail_event_from_event, get_body_from_mail_event, get_recipient_from_mail_event
from handler import get_sender_from_mail_event, get_subject_from_mail_event, get_common_header_from_mail_event
from handler import is_email_matching_template, check_if_lambda_is_active
from handler import send_email, return_recipients_exclusions, lambda_handler
from emails import Email, EmailFilter
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def test_check_if_lambda_is_inactive_undefined():
    assert check_if_lambda_is_active() == False

def test_check_if_lambda_is_inactive(monkeypatch):
    """ ensure False is returned """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'F')
    assert check_if_lambda_is_active() == False

def test_check_if_lambda_is_active(monkeypatch):
    """ ensure True is returned """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'true')

    assert check_if_lambda_is_active() == True

def test_return_recipients_exclusions_undefined():
    """ ensure empty list is returned if env var is not set """

    assert return_recipients_exclusions() == []

def test_return_recipients_exclusions_empty(monkeypatch):
    """ ensure empty list is returned if env var is empty """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_RECIPIENTS_EXCLUSION', '')
    assert return_recipients_exclusions() == []

def test_return_recipients_exclusions(monkeypatch):
    """ ensure list is returned """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_RECIPIENTS_EXCLUSION', 'test,abcdef')
    assert return_recipients_exclusions() == ['test', 'abcdef']

def test_get_mail_event_from_event():
    """ ensure mail event is returned """

    event = dict(
        Records=[
            dict(Sns=dict(Message='{"hello": "world"}'))
        ]
    )

    assert get_mail_event_from_event(event) == dict(hello='world')

def test_get_mail_event_from_event_raises_exception():
    """ ensure mail event is returned """

    event = dict(
        Records=[{}]
    )

    with pytest.raises(Exception, match='no mail event found'):
        get_mail_event_from_event(event)

def test_get_body_from_mail_event():
    """ ensure decoded body is returned"""

    event = dict(
        content='aGVsbG8gd29ybGQ=' # hello world
    )

    assert get_body_from_mail_event(event) == 'hello world'

def test_get_body_from_mail_event_raises_empty_execption():
    """ ensure exception is raised if no body is found """

    event = dict()

    with pytest.raises(Exception, match='no body found'):
        get_body_from_mail_event(event)

def test_get_common_header_from_mail_event():
    """ test get header function """

    event = dict(
        mail=dict(
            commonHeaders=dict(
                test='value'
            )
        )
    )

    assert get_common_header_from_mail_event(event, 'test') == 'value'

def test_get_common_header_from_mail_event_empty():
    """ ensure None is returned if no header is found """

    event = dict()

    assert get_common_header_from_mail_event(event, 'test') == None

def test_get_subject_from_mail_event():
    """ ensure subject is returned """

    event = dict(
        mail=dict(
            commonHeaders={
                'subject': 'subject'
            }
        )
    )

    assert get_subject_from_mail_event(event) == 'subject'

def test_get_subject_from_mail_event_without_subject_returns_empty_string():
    """ ensure exception is raised when no subject is found """

    event = dict()

    assert get_subject_from_mail_event(event) == ''

def test_get_sender_from_mail_event_full_sender():
    """ ensure sender is returned """

    event = dict(
        mail=dict(
            commonHeaders={
                'from': ['Sebastian Hutter <huttersebastian@gmail.com>']
            }
        )
    )

    assert get_sender_from_mail_event(event) == 'huttersebastian@gmail.com'

def test_get_sender_from_mail_event_email_only():
    """ ensure sender is returned """

    event = dict(
        mail=dict(
            commonHeaders={
                'from': ['huttersebastian@gmail.com']
            }
        )
    )

    assert get_sender_from_mail_event(event) == 'huttersebastian@gmail.com'

def test_get_sender_from_mail_event_raises_exception():
    """ ensure exception is raised when no sender is found """

    event = dict()

    with pytest.raises(Exception, match='no sender found'):
        get_sender_from_mail_event(event)

def test_get_sender_from_mail_event_invalid_email():
    """ ensure sender exception is raised if invalid email address """

    event = dict(
        mail=dict(
            commonHeaders={
                'from': ['invalidsender']
            }
        )
    )

    with pytest.raises(Exception, match='no email address found in sender: invalidsender'):
        get_sender_from_mail_event(event)

def test_get_recipient_from_mail_event_full_email():
    """ ensure recipient is returned """

    event = dict(
        mail=dict(
            commonHeaders={
                'to': ['Sebastian Hutter <huttersebastian@gmail.com>']
            }
        )
    )

    assert get_recipient_from_mail_event(event)== 'huttersebastian@gmail.com'

def test_get_recipient_from_mail_event_email_only():
    """ ensure recipient is returned """

    event = dict(
        mail=dict(
            commonHeaders={
                'to': ['huttersebastian@gmail.com']
            }
        )
    )

    assert get_recipient_from_mail_event(event)== 'huttersebastian@gmail.com'

def test_get_sender_from_mail_event_raises_exception():
    """ ensure exception is raised when no recipient is found """

    event = dict()

    with pytest.raises(Exception, match='no recipient found'):
        get_recipient_from_mail_event(event)

def test_get_sender_from_mail_event_invalid_email():
    """ ensure recipient exception is raised if invalid email address """

    event = dict(
        mail=dict(
            commonHeaders={
                'to': ['invalidsender']
            }
        )
    )

    with pytest.raises(Exception, match='no email address found in recipient: invalidsender'):
        get_recipient_from_mail_event(event)


def test_is_email_matching_template_no_filters():
    email = Email()
    email.subject = 'test'
    email.body = ''
    email.filters = dict(
        sender=EmailFilter(filter=[]),
        recipient=EmailFilter(filter=[]),
        subject=EmailFilter(filter=[]),
        body=EmailFilter(filter=[]),
    )

    assert is_email_matching_template(email, 'sender', 'recipient', 'subject', 'body') == True


def test_is_email_matching_template_sender_single_filter():
    email = Email()
    email.subject = 'test'
    email.body = ''
    email.filters = dict(
        sender=EmailFilter(filter=['sender']),
        recipient=EmailFilter(filter=[]),
        subject=EmailFilter(filter=[]),
        body=EmailFilter(filter=[]),
    )

    assert is_email_matching_template(email, 'sender', 'recipient', 'subject', 'body') == True
    assert is_email_matching_template(email, 'thiswontdo', 'recipient', 'subject', 'body') == False

def test_is_email_matching_template_multiple_filters():
    email = Email()
    email.subject = 'test'
    email.body = ''
    email.filters = dict(
        sender=EmailFilter(filter=['sender1', 'sender2']),
        recipient=EmailFilter(filter=[]),
        subject=EmailFilter(filter=['subject1', 'subject2']),
        body=EmailFilter(filter=[]),
    )

    assert is_email_matching_template(email, 'sender1', 'recipient', 'subject1', 'body') == True
    assert is_email_matching_template(email, 'sender2', 'recipient', 'subject2', 'body') == True
    assert is_email_matching_template(email, 'thiswontdo', 'recipient', 'subject', 'body') == False
    assert is_email_matching_template(email, 'thiswontdo', 'recipient', 'wronsubejct', 'body') == False


@pytest.fixture
def aws_credentials(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'testing')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'testing')
    monkeypatch.setenv('AWS_SECURITY_TOKEN', 'testing')
    monkeypatch.setenv('AWS_SESSION_TOKEN', 'testing')
    monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-east-1')

@pytest.fixture
def ses_backend(aws_credentials):
    # depending on used boto and moto versions
    # the ses backends are slighlty different

    if 'global' in ses_backends[DEFAULT_ACCOUNT_ID].keys():
        return ses_backends[DEFAULT_ACCOUNT_ID]['global']

    return ses_backends[DEFAULT_ACCOUNT_ID]['us-east-1']

@mock_ses
def test_email_sent(ses_backend):
    """ ensure email is sent """

    ses_backend.verify_email_address('sender@email.com')

    def message(self, from_email: str, to_email: str) -> MIMEMultipart:
        """ returns a mime email message """



        for attachment in self.attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment.name}')
            msg.attach(part)

        return msg

    msg = MIMEMultipart()
    msg['Subject'] = 'Auto-Response: Please do not reply.'
    msg['From'] = 'sender@email.com'
    msg['To'] = 'recipient@email.com'
    msg.attach(MIMEText('''
    <html>
        <head></head>
        <body>
            <h1 style='text-align:center'>This is the heading</h1>
            <p>Hello, world</p>
        </body>
    </html>
                    ''', 'html'))


    response = send_email(
        message=msg
    )

    assert response.get('ResponseMetadata', {}).get('HTTPStatusCode', 0) == 200

    # retrieve the message id from the response
    # and make sure the email in the ses backend matches
    response_message_id =  response.get('MessageId', None)
    assert response_message_id != None

    message_found_in_backend = False
    for m in ses_backend.sent_messages:
        if m.id == response_message_id:
            message_found_in_backend = True
            assert m.source == 'sender@email.com'
            assert m.destinations[0] == 'recipient@email.com'
            assert 'Auto-Response: Please do not reply.' in m.raw_data
            assert '<p>Hello, world</p>' in m.raw_data

    assert message_found_in_backend == True



def test_lambda_handler_exits_immediately_if_disabled(monkeypatch):
    """ ensure lambda exits if disabled """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'false')

    # if disabled the lambda will not raise an exception even though
    # no mail event is found
    try:
        lambda_handler(event={}, context={})
    except Exception as e:
        assert False, f"'lambda_handler' raised an exception {e}"

def test_lambda_handler_exists_if_no_emails_template_file_is_found(monkeypatch, tmp_path):
    """ ensure lambda exits if no email file is found """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'true')
    monkeypatch.chdir(tmp_path)

    # if disabled the lambda will not raise an exception even though
    # no mail event is found
    with pytest.raises(Exception, match='No such file or directory'):
        lambda_handler(event={}, context={})

def test_lambda_handler_exists_if_no_emails_template_are_defined(monkeypatch, tmp_path):
    """ ensure lambda exits if no email template is found """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'true')
    monkeypatch.chdir(tmp_path)

    with open('emails.yaml', 'w') as f:
        f.write('emails: []')


    with pytest.raises(Exception, match='no email templates found'):
        lambda_handler(event={}, context={})

@mock_ses
def test_lambda_handler_sends_no_email_if_no_match(monkeypatch, ses_backend):
    """ ensure no email is sent when no matching email template is found """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'true')

    event = dict(
        Records=[
            dict(
                Sns=dict(
                    Message=json.dumps(
                        dict(
                            mail=dict(
                                commonHeaders={
                                    'to': ['some@email.com'],
                                    'from': ['another@email.com'],
                                    'subject': 'subject',
                                },
                            ),
                            content='aGVsbG8gd29ybGQ=',
                        )
                    )
                )
            )
        ]
    )

    assert len(ses_backend.sent_messages) == 0

@mock_ses
def test_lambda_handler_sends_email_if_match(monkeypatch, ses_backend):
    """ ensur email is sent id matching email template is found """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'true')

    event = dict(
        Records=[
            dict(
                Sns=dict(
                    Message=json.dumps(
                        dict(
                            mail=dict(
                                commonHeaders={
                                    'to': ['customercare@bonzo.land'],
                                    'from': ['huttersebastian@gmail.com'],
                                    'subject': 'subject',
                                },
                            ),
                            content='aGVsbG8gd29ybGQ=',
                        )
                    )
                )
            )
        ]
    )

    ses_backend.verify_email_address('customercare@bonzo.land')
    lambda_handler(event=event, context={})

    assert len(ses_backend.sent_messages) == 1

@mock_ses
def test_lambda_handler_exits_if_recipient_in_exclusion_list(monkeypatch, ses_backend):
    """ ensure no email is sent if the recipient is in the exclusion list """

    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_IS_ACTIVE', 'true')
    monkeypatch.setenv('EMAIL_AUTO_RESPONDER_RECIPIENTS_EXCLUSION', 'customercare@bonzo.land')

    event = dict(
        Records=[
            dict(
                Sns=dict(
                    Message=json.dumps(
                        dict(
                            mail=dict(
                                commonHeaders={
                                    'to': ['customercare@bonzo.land'],
                                    'from': ['another@email.com'],
                                    'subject': 'subject',
                                },
                            ),
                            content='aGVsbG8gd29ybGQ=',
                        )
                    )
                )
            )
        ]
    )

    assert len(ses_backend.sent_messages) == 0
