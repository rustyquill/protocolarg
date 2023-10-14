
#!/usr/bin/env python
import base64
import json
from datetime import datetime, timedelta, timezone

# "key used to generate the "nonce" token value
# the token is not really a nonce token nor is it really safe
# but it is good enough for our purposes
# it consists of a rot13 shifted keyphrase + the current time in UTC
# the nonce token can be verified by decoding the keyphrase and
# ensuring the time is in a valid range (e.g. not in the future or to old)
NONCE_KEYPHRASE='rdBETRzrxHSSGdSNhlNwRZJRHtLNIcJOeXRKeYJnLRScLUWQHCaTGxOQWJvijNvQ'
ROT13_TABLE_ENCODE = str.maketrans(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
)
ROT13_TABLE_DECODE = str.maketrans(
    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
)


# uri and host for the finale page
FINALE_URI = '/94c3/8aa7821f-d685-4318-98a7-a0ef86cd3c49/index.html'
FINALE_HOST = 'office-of-incident-assessment-and-response.org.uk'
# allow overwritting the host for testing
FINALE_HOST_HEADER = 'x-finale-host'

# custom cookie to test for salted timestamp
# if the cookie is missing or the value is not correct the request will be rejected
# this is used to prevent people from accessing the finale page if they havent passed
# the database login and search
ENC_TIMESTAMP_QUERYSTRING_NAME = 'tm'
ENC_TIMESTAMP_KEY = 'unbroken-relative-unknown-demurrer-POLYMATH-aerie'


def get_utc_now():
    return datetime.utcnow()

def is_nonce_valid(nonce: str, max_age_in_minutes: int) -> bool:
    """ verify the nonce token is valid """

    try:
        nonce = base64.urlsafe_b64decode(nonce).decode('utf-8')
    except:
        return False

    # split the token from timestamp
    keyphrase, timestamp = nonce.split(':')

    # check if timestamp is not older then max_age_in_minutes
    now = get_utc_now().replace(tzinfo=timezone.utc)
    timestamp = datetime.utcfromtimestamp(float(timestamp)).replace(tzinfo=timezone.utc)

    if timedelta(minutes=max_age_in_minutes) < now - timestamp:
        return False

    # decode the keyphrase with rot13
    keyphrase = keyphrase.translate(ROT13_TABLE_DECODE)

    # check if the keyphrase matches the expected keyphrase
    if keyphrase != NONCE_KEYPHRASE:
        return False

    return True

def get_nonce_from_querystring(querystring: str):
    """
    returns the token from the given querystring
    """

    if not querystring:
        return None

    for query in querystring.split('&'):
        if query.startswith(f'nonce='):
            token = query[len(f'nonce='):]
            token = token.replace('%3D', '=')
            return token

    return None

def get_request_from_event(event: dict) -> dict:
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

def get_querystring_from_request(request: dict) -> str:
    """
    returns the querystring from the given event
    """

    querystring = request.get('querystring', '')

    if not querystring:
        return None

    return querystring

def return_access_denied_redirect(location: str):
    """
    redirect to the given location
    """

    return dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [dict(key='Location', value=location)],
            }
    )

def is_token_valid(token: str, verify_token: str) -> bool:
    """
    returns True if the token is valid
    """

    if token == verify_token:
        return True

    return False

def get_finale_host_from_request(request: dict) -> str:
    """
    returns true if the debug header is set
    """

    header = request.get('headers', {}).get(
        FINALE_HOST_HEADER, [])
    if header:
        return header[0].get('value', FINALE_HOST)

    return FINALE_HOST

def get_finale_url(host: str) -> str:
    """
    returns the finale url
    """

    return f'https://{host}{FINALE_URI}'

def encrypt_timestamp(timestamp: datetime, key: str) -> str:
    """
    encrypts the timestamp using the given key
    https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
    """

    timestamp_string = timestamp.isoformat()

    encoded_chars = []
    for i in range(len(timestamp_string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(timestamp_string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    decoded_string = "".join(encoded_chars)

    return base64.b64encode(decoded_string.encode('utf-8')).decode('utf-8')

def return_finale_redirect(location: str, querystring: str, expires: str = 'Fri, 5 Jan 2024 23:59:59 GMT'):

    return dict(
        status='302',
        statusDescription='Found',
        headers={
            'location': [ dict(key='Location', value=f'{location}?{querystring}') ],
        }
    )

def get_client_ip_from_request(request: dict) -> str:
    """
    returns the client ip from the given event
    """

    client_ip = request.get('clientIp', '')

    if not client_ip:
        return None

    return client_ip


def emit_event(reason: str, status: str, client_ip: str):
    """
    emit json formatted log event
    """

    print(json.dumps(
        dict(
            reason=reason,
            status=status,
            client_ip=client_ip,
        )
    ))

def lambda_handler(event, context):
    """
    verify the user has executed a search, then redirect to the finale page
    """


    # get all values required values to check for access
    request = get_request_from_event(event=event)
    host = get_host_from_request(request=request)
    client_ip = get_client_ip_from_request(request=request)
    querystring = get_querystring_from_request(request=request)
    nonce = get_nonce_from_querystring(querystring=querystring)
    finale_host = get_finale_host_from_request(request)
    finale_url = get_finale_url(host=finale_host)

    if not nonce:
        emit_event(reason='invalid nonce', status='denied', client_ip=client_ip)
        return return_access_denied_redirect(location=f'https://{host}/')


    if not is_nonce_valid(nonce=nonce, max_age_in_minutes=15):
        emit_event(reason='invalid nonce', status='denied', client_ip=client_ip)
        return return_access_denied_redirect(location=f'https://{host}/')

    encrypted_timestamp = encrypt_timestamp(timestamp=datetime.now(), key=ENC_TIMESTAMP_KEY)
    emit_event(reason='valid nonce', status='allowed', client_ip=client_ip)
    return return_finale_redirect(location=finale_url, querystring=f'{ENC_TIMESTAMP_QUERYSTRING_NAME}={encrypted_timestamp}')
