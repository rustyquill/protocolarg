
#!/usr/bin/env python
from datetime import datetime
import base64
import json

# minimum starting date for lambda to work, set to the utc timestamp for players finding
# the vhs cassette (2023-10-08T12:12:12 BST)
# time is in utc. this means our australian friends will have to wait a bit longer
# while our american friends will be able to access the endpoint earlier
# this shouldnt be a problem as the last key to access the site will be made available
# to players only on the 8th in the afternoon.
MINIMUM_DATE = "2023-10-08T10:30:00"

# header to overwrite the minimum date
# requirement used for testing!
# if the header is set to the value 'DREAD-FOR-ALL' the minimum date will be ignored
DEBUG_HEADER = 'x-enable-dread-for-all-rustyquill-employees'
DEBUG_HEADER_VALUE = 'DREAD-FOR-ALL-BECAUSE-WE-ARE-ALL-LIKE-THIS'

# custom cookie to test for salted timestamp
# if the cookie is missing or the value is not correct the request will be rejected
# this is used to prevent people from accessing the site if they aren't arriving via the database site
ENC_TIMESTAMP_QUERYSTRING_NAME = 'tm'
ENC_TIMESTAMP_KEY = 'unbroken-relative-unknown-demurrer-POLYMATH-aerie'
ENC_TIMESTAMP_MAX_AGE = 15

# custom cookie set by the finale page itself.
# if this one is set we know the player visited the site
# already via the database website redirect and we don't have
# to check the x-access-check cookie
FINALE_COOKIE_NAME = 'arg-finale-visited'

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


def get_request_from_event(event: dict) -> dict:
    """
    returns the request from the event
    """

    request = None
    records = event.get('Records')

    if records:
        request = records[0].get('cf', {}).get('request', None)

    return request

def get_cookie_from_request(request: dict, cookie: str) -> str:
    """
        returns the cookie from the given event
    """

    cookie_list = request.get('headers', {}).get('cookie', [{}])[0]

    for c in cookie_list.get('value', '').split(';'):
        if c.strip().startswith(cookie):
            try:
                # cut the value out of the cookie
                # we cant split on = due to base64 encoding
                return c[len(cookie)+1:].strip()
            except IndexError:
                return None

    return None

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

def get_token_from_querystring(querystring: str, token_name: str):
    """
    returns the token from the given querystring
    """

    if not querystring:
        return None

    for query in querystring.split('&'):
        if query.startswith(f'{token_name}='):
            token = query[len(f'{token_name}='):]
            token = token.replace('%3D', '=')
            return token

    return None

def get_current_time_in_utc() -> datetime:
    """
    returns the current time in utc
    """

    return datetime.utcnow()

def convert_minimum_date_to_datetime(minimum_date: str) -> datetime:
    """
    converts the minimum date string to a datetime object
    """

    return datetime.fromisoformat(minimum_date)


def is_current_time_after_minimum_date(current_time: datetime, minimum_date: datetime) -> bool:
    """
    returns true if the current time is after the minimum date
    """

    return current_time >= minimum_date

def is_debug_header_set(request: dict) -> bool:
    """
    returns true if the debug header is set
    """

    debug_header = request.get('headers', {}).get(
        DEBUG_HEADER, [])
    if debug_header:
        if debug_header[0].get('value', '') == DEBUG_HEADER_VALUE:
            return True

    return False

def decrypt_timestamp(encrypted_timestamp: str, key: str) -> datetime:
    """
    decrypts the encrypted timestamp header
    https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
    """

    try:
        encrypted_timestamp_decoded = base64.b64decode(encrypted_timestamp).decode('utf-8')

        decoded_chars = []
        for i in range(len(encrypted_timestamp_decoded)):
            key_c = key[i % len(key)]
            decoded_c = chr(ord(encrypted_timestamp_decoded[i]) - ord(key_c) % 256)
            decoded_chars.append(decoded_c)
        decoded_string = "".join(decoded_chars)

        return datetime.fromisoformat(decoded_string)
    except Exception:
        pass

    return None

def is_decrypted_timestamp_valid(decrypted_timestamp: datetime, current_time: datetime, max_age: int) -> bool:
    """
    returns true if the decrypted timestamp is in the range of the current time
    """

    if decrypted_timestamp > current_time:
        return False

    return (current_time - decrypted_timestamp).total_seconds() <= max_age


def lambda_handler(event, context):
    """
    serve the "normal" website or the "nightmare" version
    depending on the clients current time
    """

    # get all values required values to check for access
    request = get_request_from_event(event=event)
    current_time = get_current_time_in_utc()
    minimum_date = convert_minimum_date_to_datetime(minimum_date=MINIMUM_DATE)
    querystring = get_querystring_from_request(request=request)
    encrypted_timestamp = get_token_from_querystring(querystring=querystring, token_name=ENC_TIMESTAMP_QUERYSTRING_NAME)
    client_ip = get_client_ip_from_request(request=request)

    # test if request is sent after the minimum date
    if not is_current_time_after_minimum_date(current_time=current_time, minimum_date=minimum_date) and not is_debug_header_set(request=request):
        emit_event(reason='before minimum date', status='denied', client_ip=client_ip)
        return dict(
            status='404',
            statusDescription='Not Found',
        )

    # if the visited cookie is set we allow access to the site
    if get_cookie_from_request(request=request, cookie=FINALE_COOKIE_NAME):
        emit_event(reason='finale cookie set', status='allowed', client_ip=client_ip)
        return request

    # check if we have a salted timestamp header, if not access is denied
    if not encrypted_timestamp:
        emit_event(reason='no salted timestamp', status='denied', client_ip=client_ip)
        return dict(
            status='404',
            statusDescription='Not Found',
        )

    # decrypt the salted timestamp
    decrypted_timestamp = decrypt_timestamp(encrypted_timestamp=encrypted_timestamp, key=ENC_TIMESTAMP_KEY)

    # if the timestamp is not in the max age range access is denied
    if not is_decrypted_timestamp_valid(decrypted_timestamp=decrypted_timestamp, current_time=current_time, max_age=ENC_TIMESTAMP_MAX_AGE):
        emit_event(reason='invalid salted timestamp', status='denied', client_ip=client_ip)
        return dict(
            status='404',
            statusDescription='Not Found',
        )

    # if we are here the request is valid and we can serve the site
    emit_event(reason='valid salted timestamp', status='allowed', client_ip=client_ip)
    return request
