import pytest
from emails import load_email_templates, EmailFilter, Email, return_email_from_email_template

def test_template_file_load():
    """ ensure the given template file exists and can be loaded """

    emails = load_email_templates('emails.yaml')

    assert len(emails) > 0


def test_template_file_load_raises_exception():
    """ ensure an exception is raised when the given template file does not exist """

    with pytest.raises(FileNotFoundError):
        load_email_templates('does_not_exist.yaml')

def test_return_from_email_template():
    """ ensure an Email object is returned from the given email template """

    email_template = dict(
        subject='subject',
        body='body',
        filters=dict(
            sender=['sender'],
            recipient=['recipient'],
            subject=['subject'],
            body=['body']
        )
    )

    email = return_email_from_email_template(email_template)

    assert email.subject == 'subject'
    assert email.body == 'body'
    assert email.filters['sender'].filter == ['sender']
    assert email.filters['recipient'].filter == ['recipient']
    assert email.filters['subject'].filter == ['subject']
    assert email.filters['body'].filter == ['body']

def test_return_from_email_template_no_filters():
    """ ensure an Email object is returned from the given email template """

    email_template = dict(
        subject='subject',
        body='body',
    )

    email = return_email_from_email_template(email_template)

    assert email.subject == 'subject'
    assert email.body == 'body'
    assert email.filters['sender'].filter == []
    assert email.filters['recipient'].filter == []
    assert email.filters['subject'].filter == []
    assert email.filters['body'].filter == []

def test_email_filter_matches():
    """ ensure an EmailFilter matches the given text """

    email_filter = EmailFilter(['test'])

    assert email_filter.matches('test')
    assert email_filter.matches('123test')
    assert email_filter.matches('test123')
    assert email_filter.matches('123test123')
    assert email_filter.matches('abc') is False


def test_email_filter_matches_multiple_filters():
    """ ensure an EmailFilter matches the given text """

    email_filter = EmailFilter(['test', 'abc'])

    assert email_filter.matches('test')
    assert email_filter.matches('123test')
    assert email_filter.matches('test123')
    assert email_filter.matches('123test123')
    assert email_filter.matches('abc')

def test_email_filter_matches_no_filter():
    """ ensure an EmailFilter matches the given text """

    email_filter = EmailFilter([])

    assert email_filter.matches('test')
    assert email_filter.matches('123test')
    assert email_filter.matches('test123')
    assert email_filter.matches('123test123')
