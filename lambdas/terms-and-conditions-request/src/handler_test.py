#!/usr/bin/env python3

from handler import get_host_from_request, get_cookie_from_request, get_querystring_from_request
from handler import get_uri_from_request, get_request_from_event, is_cookie_set, is_querystring_set
from handler import return_terms_and_conditions_redirect, return_callback_redirect_with_cookie
from handler import return_callback_redirect_without_cookie, lambda_handler, get_terms_and_conditions_host_from_request
from handler import get_terms_and_conditions_url
from handler import TERMS_AND_CONDITIONS_HOST, TERMS_AND_CONDITIONS_URI, TERMS_AND_CONDITIONS_HOST_HEADER
from handler import CALLBACK_QUERYSTRING, TC_QUERYSTRING, COOKIE_STRING

def test_get_request_from_event_empty_event():
    request = get_request_from_event({})

    assert request is None


def test_get_request_from_event_empty_records():
    request = get_request_from_event({'Records': []})

    assert request is None


def test_get_request_from_event_no_cf():
    request = get_request_from_event({'Records': [{'test': 'test'}]})

    assert request is None


def test_get_request_from_event_empty_cf():
    request = get_request_from_event({'Records': [{'cf': {}}]})

    assert request is None


def test_get_request_from_event():
    request = get_request_from_event({'Records': [{'cf': {'request': {}}}]})

    assert request == {}

def test_get_host_from_request_empty():
    request = dict(
        headers=dict()
    )

    host = get_host_from_request(request)

    assert host is None

def test_get_host_from_request():
    request = dict(
        headers=dict(host=[dict(key='Host', value='test.com')])
    )

    host = get_host_from_request(request)

    assert host == 'test.com'

def test_get_cookie_from_request_empty():
    request = dict(
        headers=dict()
    )

    cookie = get_cookie_from_request(request)

    assert cookie is None

def test_get_host_from_request():
    request = dict(
        headers=dict(cookie=[dict(key='Cookie', value='test=true;')])
    )

    cookie = get_cookie_from_request(request)

    assert cookie == 'test=true;'


def test_get_querystring_from_request_empty():
    request = dict(
        querystring=''
    )

    querystring = get_querystring_from_request(request)

    assert querystring is None

def test_get_querystring_from_request():
    request = dict(
        querystring='my=query'
    )

    querystring = get_querystring_from_request(request)

    assert querystring == 'my=query'

def test_get_uri_from_request_empty():
    request = dict(
        uri=''
    )

    uri = get_uri_from_request(request)

    assert uri is None

def test_get_uri_from_request():
    request = dict(
        uri='/'
    )

    uri = get_uri_from_request(request)

    assert uri == '/'

def test_is_querystring_set_true():
    """ensure true is returned if the query string contains the QUERYSTRING"""

    assert is_querystring_set(querystring='?this=is&along=querystring&termsAndConditionsAccepted=true') == True

def test_is_querystring_set_false():
    assert is_querystring_set(querystring='?this=is&along=querystring') == False

def test_is_cookie_set_true():
    """ensure true is returned if the query string contains the COOKIE_STRING"""

    assert is_cookie_set(cookie='themagnusprotocolargtc=true;') == True

def test_is_cookie_set_false():
    assert is_cookie_set(cookie='anyothercookie=124; abc=def') == False

def test_return_terms_and_conditions_redirect():
    """ensure terms and conditions url looks correct"""

    redirect = return_terms_and_conditions_redirect(
        host='test.com',
        uri='/index.html',
        terms_and_conditions_url='http://localhost:4000/terms.html'
    )

    assert redirect == dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [ dict(key='Location', value='http://localhost:4000/terms.html?callbackUrl=https://test.com/index.html') ]
        }
    )

def test_return_callback_redirect_with_cookie():
    """ ensure callback redirect with cookie looks correct """

    redirect = return_callback_redirect_with_cookie(
        host='test.com',
        uri='/index.html',
        cookie='themagnusprotocolargtc=true',
        expires='Fri, 5 Jan 2024 23:59:59 GMT'
    )

    assert redirect == dict (
        status='302',
        statusDescription='Found',
        headers={
            'location': [dict(key='Location', value='https://test.com/index.html')],
            'set-cookie': [dict(key='Set-Cookie', value='themagnusprotocolargtc=true; Path=/; SameSite=Lax; Secure; Expires=Fri, 5 Jan 2024 23:59:59 GMT')],
        }
    )

def test_return_callback_redirect_without_cookie():
    """ ensure callback redirect without cookie looks correct """

    redirect = return_callback_redirect_without_cookie(
        host='test.com',
        uri='/index.html',
    )

    assert redirect == dict (
        status='302',
        statusDescription='Found',
        headers={
            'location': [dict(key='Location', value='https://test.com/index.html')],
        }
    )


def test_get_terms_and_conditions_host_from_request_empty():
    """ ensure empty request returns None """

    request = dict(
        headers=dict()
    )

    host = get_terms_and_conditions_host_from_request(request)

    assert host is TERMS_AND_CONDITIONS_HOST

def test_get_terms_and_conditions_host_header_from_request_empty_value():
    """ ensure request with host header returns host header """

    request = {
        'headers': {
            TERMS_AND_CONDITIONS_HOST_HEADER: [{'key': TERMS_AND_CONDITIONS_HOST_HEADER, 'value': ''}]
        }
    }


    host = get_terms_and_conditions_host_from_request(request)

    assert host == TERMS_AND_CONDITIONS_HOST

def test_get_terms_and_conditions_host_header_from_request_empty_value():
    """ ensure request with host header returns host header """

    request = {
        'headers': {
            TERMS_AND_CONDITIONS_HOST_HEADER: [{'key': TERMS_AND_CONDITIONS_HOST_HEADER, 'value': 'test.com'}]
        }
    }

    host = get_terms_and_conditions_host_from_request(request)

    assert host == 'test.com'

def test_get_terms_and_conditions_url():

    url = get_terms_and_conditions_url(host='test.com')

    assert url == f'https://test.com{TERMS_AND_CONDITIONS_URI}'

def test_lambda_handler_no_cookie_no_query_string():
    """ ensure lambda without cookie or query string returns redirect """

    event = dict(
        Records=[
            dict(
                cf=dict(
                    request=dict(
                        headers=dict(host=[dict(key='Host', value='test.com')]),
                        uri='/',
                        querystring='',
                    )
                )
            )
        ]
    )

    response = lambda_handler(event=event, context=None)
    conditions_url = get_terms_and_conditions_url(host=get_terms_and_conditions_host_from_request({}))

    assert response == dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [{
                'key': 'Location',
                'value': f'{conditions_url}?callbackUrl=https://test.com/'
            }]
        }
    )

def test_lambda_handler_cookie():
    """ ensure lambda returns original request if cookie is set """

    event = dict(
        Records=[
            dict(
                cf=dict(
                    request=dict(
                        headers=dict(
                            host=[dict(key='Host', value='test.com')],
                            cookie=[dict(key='Cookie', value='themagnusprotocolargtc=true;')]
                        ),
                        uri='/',
                        querystring='',
                    )
                )
            )
        ]
    )

    response = lambda_handler(event=event, context=None)

    assert response == event['Records'][0]['cf']['request']

def test_lambda_handler_querystring():
    """ ensure lambda returns a 302 to itself with cookie info if querystring is set """

    event = dict(
        Records=[
            dict(
                cf=dict(
                    request=dict(
                        headers=dict(
                            host=[dict(key='Host', value='test.com')],
                        ),
                        uri='/',
                        querystring=TC_QUERYSTRING,
                    )
                )
            )
        ]
    )

    response = lambda_handler(event=event, context=None)

    assert response == dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [dict(key='Location', value=f'https://test.com/')],
            'set-cookie': [dict(key='Set-Cookie', value=f'{COOKIE_STRING}; Path=/; SameSite=Lax; Secure; Expires=Fri, 5 Jan 2024 23:59:59 GMT')],
        }
    )

def test_lambda_handler_terms_and_condition_host_no_querystring_no_cookie():
    """ ensure the original request is returned if accessing the terms and conditions page without query string or cookie """

    event = dict(
        Records=[
            dict(
                cf=dict(
                    request=dict(
                        headers=dict(
                            host=[dict(key='Host', value=TERMS_AND_CONDITIONS_HOST)],
                        ),
                        uri=TERMS_AND_CONDITIONS_URI,
                        querystring='',
                    )
                )
            )
        ]
    )

    response = lambda_handler(event=event, context=None)

    assert response == event['Records'][0]['cf']['request']


def test_lambda_handler_terms_and_condition_host_with_querystring_no_cookie():
    """ ensure the original request is returned if accessing the terms and conditions page without cookie """

    event = dict(
        Records=[
            dict(
                cf=dict(
                    request=dict(
                        headers=dict(
                            host=[dict(key='Host', value=TERMS_AND_CONDITIONS_HOST)],
                        ),
                        uri=TERMS_AND_CONDITIONS_URI,
                        querystring=f'{CALLBACK_QUERYSTRING}test.com/index.html',
                    )
                )
            )
        ]
    )

    response = lambda_handler(event=event, context=None)

    assert response == event['Records'][0]['cf']['request']

def test_lambda_handler_terms_and_condition_host_with_querystring_and_cookie():
    """ ensure a redirect with cookie pointing to the callback url is returned """

    event = dict(
        Records=[
            dict(
                cf=dict(
                    request=dict(
                        headers=dict(
                            host=[dict(key='Host', value=TERMS_AND_CONDITIONS_HOST)],
                            cookie=[dict(key='Cookie', value=COOKIE_STRING)],
                        ),
                        uri=TERMS_AND_CONDITIONS_URI,
                        querystring=f'{CALLBACK_QUERYSTRING}test.com/index.html',
                    )
                )
            )
        ]
    )

    response = lambda_handler(event=event, context=None)

    assert response == dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [dict(key='Location', value=f'https://test.com/index.html?{TC_QUERYSTRING}')],
        }
    )
