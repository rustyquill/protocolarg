
#!/usr/bin/env python3

"""
    viewer request lambda@edge function

    check for terms and conditions cookie or query string
    parsing of querystring and cookie is simplified as we assume
    that these parametrers are only set by the terms and conditions page
    which we control the format of!
"""

import json

# name of the querystring parameter or cookie
# to check for!
CALLBACK_QUERYSTRING = 'callbackUrl=https://'
TC_QUERYSTRING = 'termsAndConditionsAccepted=true'
COOKIE_STRING = 'themagnusprotocolargtc=true'

# default values for the terms and conditions page
TERMS_AND_CONDITIONS_URI = '/terms.html'
TERMS_AND_CONDITIONS_HOST = 'themagnusprotocolarg.com'
# TERMS_AND_CONDITIONS_URL = f'https://{TERMS_AND_CONDITIONS_HOST}{TERMS_AND_CONDITIONS_URI}'
# allow setting of a custom terms and conditions host
TERMS_AND_CONDITIONS_HOST_HEADER = 'x-terms-and-conditions-host'

def get_request_from_event(event: dict):
    """
    returns the request from the event
    """

    request = None
    records = event.get('Records')

    if records:
        request = records[0].get('cf', {}).get('request', None)

    return request

def get_host_from_request(request: dict) -> str:
    """
    returns the host from the given event
    """

    host = request.get('headers', {}).get('host', [])

    if not host:
        return None

    return host[0].get('value', None)

def get_cookie_from_request(request: dict) -> str:
    """
    returns the cookie from the given event
    """

    cookie = request.get('headers', {}).get('cookie', [])

    if not cookie:
        return None

    return cookie[0].get('value', None)


def get_querystring_from_request(request: dict) -> str:
    """
    returns the querystring from the given event
    """

    querystring = request.get('querystring', '')

    if not querystring:
        return None

    return querystring

def get_client_ip_from_request(request: dict) -> str:
    """
    returns the client ip from the given event
    """

    client_ip = request.get('clientIp', '')

    if not client_ip:
        return None

    return client_ip

def get_uri_from_request(request: dict) -> str:
    """
    returns the uri from the given event
    """

    uri = request.get('uri', '')

    if not uri:
        return None

    return uri

def get_terms_and_conditions_host_from_request(request: dict) -> str:
    """
    returns true if the debug header is set
    """

    header = request.get('headers', {}).get(
        TERMS_AND_CONDITIONS_HOST_HEADER, [])
    if header:
        return header[0].get('value', TERMS_AND_CONDITIONS_HOST)

    return TERMS_AND_CONDITIONS_HOST

def get_terms_and_conditions_url(host: str) -> str:
    """
    returns the terms and conditions url
    """

    return f'https://{host}{TERMS_AND_CONDITIONS_URI}'

def is_cookie_set(cookie: str, cookie_string_to_check_for: str = COOKIE_STRING) -> bool:
    """ check if the terms and conditions cookie is set """

    if not cookie:
        return False

    if cookie_string_to_check_for in cookie:
        return True

    return False

def is_querystring_set(querystring: str, querystring_to_check_for: str = TC_QUERYSTRING) -> bool:

    if not querystring:
        return False

    if querystring_to_check_for in querystring:
        return True

    return False

def return_callback_redirect_with_cookie(host: str, uri: str, cookie: str = COOKIE_STRING, expires: str = 'Fri, 5 Jan 2024 23:59:59 GMT') -> dict:

    location = f'https://{host}'
    if uri:
        location = f'{location}{uri}'

    cookie_value = f'{cookie}; Path=/; SameSite=Lax; Secure; Expires={expires}'

    return dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [dict(key='Location', value=location)],
            'set-cookie': [dict(key='Set-Cookie', value=cookie_value)],
            }
        )

def return_callback_redirect_without_cookie(host: str, uri: str) -> dict:

    location = f'https://{host}'
    if uri:
        location = f'{location}{uri}'

    return dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [dict(key='Location', value=location)],
            }
        )


def return_terms_and_conditions_redirect(host: str, uri: str, terms_and_conditions_url: str) -> dict:
    """ return redirect to terms and conditions page """

    location = f'{terms_and_conditions_url}?callbackUrl=https://{host}'
    if uri:
        location = f'{location}{uri}'

    return dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [ dict(key='Location', value=location) ]
        }
    )

def emit_event(reason: str, client_ip: str):
    """
    emit json formatted log event
    """

    print(json.dumps(
        dict(
            reason=reason,
            client_ip=client_ip,
        )
    ))


def lambda_handler(event, context):
    """
    verify cookie is set, if no cookie is available check for query string
    if both are not set redirect to terms and conditions page
    """

    request = get_request_from_event(event)
    host = get_host_from_request(request)
    querystring = get_querystring_from_request(request)
    uri = get_uri_from_request(request)
    cookie = get_cookie_from_request(request)
    client_ip = get_client_ip_from_request(request)

    # setup terms and conditions host and url
    terms_and_conditions_host = get_terms_and_conditions_host_from_request(request)
    terms_and_conditions_url = get_terms_and_conditions_url(terms_and_conditions_host)

    # special case for the terms and conditions page itself
    if host == terms_and_conditions_host \
        and uri == TERMS_AND_CONDITIONS_URI:

        # if the player is visiting the terms and conditions page
        # but no callback query string is set we can assume they
        # navigated to the terms and conditions page manually
        # e.g. we return the unmodified request
        if not is_querystring_set(querystring=querystring, querystring_to_check_for=CALLBACK_QUERYSTRING):
            return request

        # if a querystring is set but no cookie is set for themagnusprotocolarg.com
        # we can assume the player is coming from an arg page and needs to accept the
        # terms and conditions
        if not is_cookie_set(cookie):
            emit_event(reason='new player detected', client_ip=client_ip)
            return request

        # if querystring is set AND cookie already exists for themagnusprotocolarg.com
        # we can assume the player already accepted the terms and conditions and can be redirected
        # back to the callback url without presenting the terms and conditions page!

        # we split the callback query string up to get the host
        # and attach the termsAndConditionsAccepted=true query string to the request
        # so the callback website can set the cookie
        return return_callback_redirect_without_cookie(host=f'{querystring.split("=")[1][8:]}?{TC_QUERYSTRING}', uri=None)

    # if a valid cookie is present proceed with request
    if is_cookie_set(cookie):
        return request

    # if no cookie is set but the cookie accepted query string is set
    # the player is being redirected from the terms and conditions page
    # lets do one last redirect to set the cookie
    if is_querystring_set(querystring):
        # if the query string is set we return a redirect to the uri
        # but setting the cookie via header
        return return_callback_redirect_with_cookie(host=host, uri=uri)

    # neither cookie nor querystring are set
    # player needs to be redirected to terms and condition host
    return return_terms_and_conditions_redirect(host=host, uri=uri, terms_and_conditions_url=terms_and_conditions_url)

