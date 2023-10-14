
#!/usr/bin/env python
import base64
import json
from urllib.parse import parse_qs
from typing import List
from dataclasses import dataclass
import random
from datetime import datetime, timedelta, timezone

# the required symbols in order
# valid symbols that can be passed from the form are:
# "air"
# "alkali"
# "ashes"
# "cinnabar"
# "copper"
# "day-night"
# "earth"
# "fire"
# "gold"
# "iron"
# "jupiter"
# "lead"
# "mercury"
# "none" (if no symbol is selected)
# "oxygen"
# "phlogiston"
# "platinum"
# "realgar"
# "salt"
# "sulfur"
# "tin"

# the symbols need to be marked in order for the query to be successful!
REQUIRED_SYMBOLS = [
    'lead',
    'mercury',
    'sulphur',
    'fire',
    'salt',
    'jupiter',
    'gold',
    'cinnabar',
    'ashes',
    'iron',
]

# random list of error messages to display to user for wrong queries
ERROR_MESSAGES = [
    'Invalid query',
    'Query not found',
    'Server error. Please try again later',
    'Query failed',
    'Something went wrong',
    'Query timed out',
]

@dataclass
class Response():
    success: bool
    error: str
    results: int
    nonce: str


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

def get_utc_now():
    return datetime.utcnow()

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

def parse_symbols_from_querystring(querystring: str) -> List[str]:
    """ parse the given query string and return the symbols as lidt """

    qs = parse_qs(querystring)
    if not qs:
        return []
    symbols = qs.get('query', [''])[0].split(',')
    return symbols

def generate_nonce_token(keyphrase: str) -> str:
    """ generate a nonce token """

    # encode the keyphrase with rot13
    keyphrase = keyphrase.translate(ROT13_TABLE_ENCODE)

    # create the nonce token by appending the keyphrase and the current time
    nonce = f'{keyphrase}:{get_utc_now().timestamp()}'

    # encode the nonce token with base64
    nonce = base64.urlsafe_b64encode(nonce.encode('utf-8'))

    return nonce.decode('utf-8')

def is_nonce_valid(nonce: str, max_age_in_minutes: int) -> bool:
    """ verify the nonce token is valid """

    # decode the nonce token with base64
    nonce = base64.urlsafe_b64decode(nonce).decode('utf-8')

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

def return_successful_query() -> Response:
    """ return a successfull query response """
    return Response(
        success=True,
        error='',
        results=1,
        nonce=generate_nonce_token(keyphrase=NONCE_KEYPHRASE),
    )

def return_error_query() -> Response:
    """ return a error query response """

    return Response(
        success=False,
        error=random.choice(ERROR_MESSAGES),
        results=0,
        nonce='',
    )

def return_lambda_response(resp: Response) -> dict:
    """ return a lambda response """

    return {
        'status': '200',
        'statusDescription': 'OK',
        'body': json.dumps(resp.__dict__),
        'headers': {
            "content-type": [
                {
                    'key': 'Content-Type',
                    'value': 'application/json'
                }
            ],
        },
    }

def lambda_handler(event, context):
    """
    serve the "normal" website or the "nightmare" version
    depending on the clients current time
    """

    # get all values required values to check for access
    request = get_request_from_event(event=event)
    querystring = get_querystring_from_request(request=request)
    client_ip = get_client_ip_from_request(request=request)

    if parse_symbols_from_querystring(querystring=querystring) == REQUIRED_SYMBOLS:
        emit_event(reason='valid query', status='allowed', client_ip=client_ip)
        return return_lambda_response(resp=return_successful_query())

    emit_event(reason='invalid query', status='denied', client_ip=client_ip)
    return return_lambda_response(resp=return_error_query())

