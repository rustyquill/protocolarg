
#!/usr/bin/env python
from datetime import datetime, timedelta
import base64
import json
from dataclasses import dataclass
from wsgiref.handlers import format_date_time
from time import mktime


KEYWORD = 'allisbonzomerch'
PASSWORD = 'tabernabonzotasticmerch'
# this is kinda funky as the shift can not be bigger as 26 letters
# but the clue for the players is 2000. we will be using modulo 26
# to get the correct shift
SHIFT = 2000

@dataclass
class Response():
    success: bool
    validated: str

def encode_password(password: str, key: str, shift: int) -> str:
    """ encode the given password with a keyed caesaer  cipher """

    # remove duplicate letters from the keyword
    keyword = ''.join(sorted(set(key), key=key.index))
    # create the substitution alphabet
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    key_alpha = keyword.lower() + ''.join(sorted(set(alphabet) - set(keyword.lower())))
    # create a dictionary to map each letter of the alphabet to its cipher equivalent
    real_shift = shift % len(alphabet)
    cipher_alpha = key_alpha[real_shift:] + key_alpha[:real_shift]
    translation_table = str.maketrans(alphabet, cipher_alpha)

    return password.lower().translate(translation_table)

def get_request_from_event(event: dict) -> dict:
    """
    returns the request from the event
    """

    request = None
    records = event.get('Records')

    if records:
        request = records[0].get('cf', {}).get('request', None)

    return request

def get_querystring_from_request(request: dict) -> str:
    """
    returns the querystring from the given event
    """

    querystring = request.get('querystring', '')

    if not querystring:
        return None

    return querystring

def get_host_from_request(request: dict) -> str:
    """
    returns the host from the given event
    """

    host = request.get('headers', {}).get('host', [])

    if not host:
        return None

    return host[0].get('value', None)

def get_password_from_querystring(querystring: str):
    """
    returns the token from the given querystring
    """

    if not querystring:
        return None

    for query in querystring.split('&'):
        if query.startswith(f'password='):
            token = query[len(f'password='):]
            token = token.replace('%3D', '=')
            return token

    return None

def get_cookie_from_request(request: dict) -> str:
    """
    returns the cookie from the given event
    """

    cookie = request.get('headers', {}).get('cookie', [])

    if not cookie:
        return None

    return cookie[0].get('value', None)

def is_cookie_set(cookie: str, cookie_string_to_check_for: str) -> bool:
    """ check if the terms and conditions cookie is set """

    if not cookie:
        return False

    if cookie_string_to_check_for in cookie:
        return True

    return False

def return_with_cookie(host: str, uri: str, cookie: str, expires: str) -> dict:

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

def return_without_cookie(host: str, uri: str) -> dict:

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

def get_client_ip_from_request(request: dict) -> str:
    """
    returns the client ip from the given event
    """

    client_ip = request.get('clientIp', '')

    if not client_ip:
        return None

    return client_ip

def get_cookie_expiration_time(minutes: int):
    # Get the current time
    now = datetime.utcnow()
    # Add N minutes to the current time
    expire_time = now + timedelta(minutes=minutes)
    # Convert the expiration time to a timestamp
    stamp = mktime(expire_time.timetuple())
    # Format the timestamp in the RFC 1123 date format
    return format_date_time(stamp)


def lambda_handler(event, context):
    """
    calculate the cipher from the given password and
    compare it to the given cipher
    """


    # get all values required values to check for access
    request = get_request_from_event(event=event)
    host = get_host_from_request(request)
    querystring = get_querystring_from_request(request=request)
    client_ip = get_client_ip_from_request(request=request)
    player_password = get_password_from_querystring(querystring=querystring)
    cookie = get_cookie_from_request(request)

    player_password_encoded = None
    if player_password:
        player_password_encoded = encode_password(password=player_password, key=KEYWORD, shift=SHIFT)
    reference_password_encoded = encode_password(password=PASSWORD, key=KEYWORD, shift=SHIFT)

    # if a cookie is set lets check the cookie value against the reference password
    cookie_string_to_check_for = f'bonzobazaarauthentication={reference_password_encoded}'
    if is_cookie_set(cookie=cookie, cookie_string_to_check_for=cookie_string_to_check_for):
        emit_event(reason='cookie set', status='allowed', client_ip=client_ip)
        return request

    # if no cookie is set make sure the querty string password is valid
    # and set a new cookie
    if player_password_encoded == reference_password_encoded:
        emit_event(reason='valid password', status='allowed', client_ip=client_ip)
        return return_with_cookie(
            host=host,
            uri='/shop/shop.html',
            cookie=cookie_string_to_check_for,
            expires=get_cookie_expiration_time(minutes=30)
        )

    # if no password is set or no cookie exists redirect player back to index page
    emit_event(reason='invalid password', status='denied', client_ip=client_ip)
    return return_without_cookie(
        host=host,
        uri='/index.html',
    )

