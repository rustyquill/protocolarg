
#!/usr/bin/env python
from datetime import datetime
import base64
import json
from dataclasses import dataclass

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
    calculate the cipher from the given password and
    compare it to the given cipher
    """


    # get all values required values to check for access
    request = get_request_from_event(event=event)
    querystring = get_querystring_from_request(request=request)
    client_ip = get_client_ip_from_request(request=request)
    player_password = get_password_from_querystring(querystring=querystring)

    # encode the player and the reference password
    player_password_encoded = None
    if player_password:
        player_password_encoded = encode_password(password=player_password, key=KEYWORD, shift=SHIFT)
    reference_password_encoded = encode_password(password=PASSWORD, key=KEYWORD, shift=SHIFT)

    if not player_password_encoded == reference_password_encoded:
        # for now we have no valid logins at all!
        emit_event(reason='invalid password', status='denied', client_ip=client_ip)
        return return_lambda_response(Response(success=False, validated=reference_password_encoded))

    emit_event(reason='valid password', status='allowed', client_ip=client_ip)
    return return_lambda_response(Response(success=True, validated=reference_password_encoded))
