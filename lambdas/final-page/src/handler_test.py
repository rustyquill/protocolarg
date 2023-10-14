# #!/usr/bin/env python

# import handler for monkeypatching
import handler
import pytest
import base64

from datetime import datetime, timedelta
from handler import get_request_from_event, get_current_time_in_utc, convert_minimum_date_to_datetime
from handler import is_current_time_after_minimum_date, get_cookie_from_request
from handler import DEBUG_HEADER, DEBUG_HEADER_VALUE, is_debug_header_set
from handler import ENC_TIMESTAMP_QUERYSTRING_NAME, ENC_TIMESTAMP_KEY, ENC_TIMESTAMP_MAX_AGE
from handler import lambda_handler, decrypt_timestamp, is_decrypted_timestamp_valid
from handler import FINALE_COOKIE_NAME, get_token_from_querystring, get_querystring_from_request

def encode_string(payload: str, key: str) -> str:
    # https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password
    encoded_chars = []
    for i in range(len(payload)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(payload[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.b64encode(encoded_string.encode('utf-8'))

# fixtures for timestmap tests
@pytest.fixture
def timestamp_cleartext():
    return datetime.utcnow()
@pytest.fixture
def timestamp_encrypted(timestamp_cleartext):
    return encode_string(timestamp_cleartext.isoformat(), ENC_TIMESTAMP_KEY)



# example event for completeness sake!
CLOUDFRONT_EVENT = {
    'Records': [
        {
            'cf': {
                'config': {
                    'distributionDomainName': 'd1dxd9x88yyxb1.cloudfront.net',
                    'distributionId': 'E14BZQWGSG7O3O',
                    'eventType': 'origin-request',
                    'requestId': '_Gq1Q8O59LUnMbFRjMdLZJ16Z4oFzV1eKpG2LXigJ_C-zJR-PIbzCQ=='
                },
                'request': {
                    'clientIp': '81.6.47.76',
                    'headers': {
                        'host': [{'key': 'Host', 'value': 'host.com'}],
                        'user-agent': [{'key': 'User-Agent', 'value': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0'}],
                        'accept': [{'key': 'accept', 'value': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}],
                        'accept-language': [{'key': 'accept-language', 'value': 'en-US,en;q=0.5'}],
                        'accept-encoding': [{'key': 'accept-encoding', 'value': 'gzip, deflate, br'}],
                        'dnt': [{'key': 'dnt', 'value': '1'}],
                        'upgrade-insecure-requests': [{'key': 'upgrade-insecure-requests', 'value': '1'}],
                        'sec-fetch-dest': [{'key': 'sec-fetch-dest', 'value': 'document'}],
                        'sec-fetch-mode': [{'key': 'sec-fetch-mode', 'value': 'navigate'}],
                        'sec-fetch-site': [{'key': 'sec-fetch-site', 'value': 'cross-site'}],
                        'if-modified-since': [{'key': 'if-modified-since', 'value': 'Tue, 01 Aug 2023 14:53:44 GMT'}],
                        'if-none-match': [{'key': 'if-none-match', 'value': '"5861e3adfcac620693bb313e6b9354ec"'}],
                        'te': [{'key': 'te', 'value': 'trailers'}]
                    },
                    'method':
                    'GET', 'querystring': '',
                    'uri': '/94c3/8aa7821f-d685-4318-98a7-a0ef86cd3c49/index.html'
                }
            }
        }
    ]
}


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

def test_get_current_time_in_utc():
    current_time = get_current_time_in_utc()

    assert type(current_time) is datetime
    assert current_time.tzinfo is None

def test_convert_minimum_date_to_datetime():
    minimum_date = convert_minimum_date_to_datetime('2023-10-08T00:00:00')

    assert type(minimum_date) is datetime
    assert str(minimum_date) == '2023-10-08 00:00:00'

def test_is_current_time_after_minimum_date_equal():
    current_time = datetime(2023, 10, 8, 0, 0, 0)
    minimum_date = datetime(2023, 10, 8, 0, 0, 0)

    assert is_current_time_after_minimum_date(current_time, minimum_date) is True

def test_is_current_time_after_minimum_date_before():
    current_time = datetime(2023, 10, 8, 0, 0, 0)
    minimum_date = datetime(2023, 10, 9, 0, 0, 0)

    assert is_current_time_after_minimum_date(current_time, minimum_date) is False

def test_is_current_time_after_minimum_date_after():
    current_time = datetime(2023, 10, 9, 0, 0, 0)
    minimum_date = datetime(2023, 10, 8, 0, 0, 0)

    assert is_current_time_after_minimum_date(current_time, minimum_date) is True

def test_is_debug_header_set_none():
    request = {
        'headers': {}
    }

    assert is_debug_header_set(request) is False

def test_is_debug_header_set_empty():
    request = {
        'headers': {
            DEBUG_HEADER: []
        }
    }

    assert is_debug_header_set(request) is False

def test_is_debug_header_set_wrong_value():
    request = {
        'headers': {
            DEBUG_HEADER: [{'key': DEBUG_HEADER, 'value': 'wrong'}]
        }
    }

    assert is_debug_header_set(request) is False

def test_is_debug_header_set():
    request = {
        'headers': {
            DEBUG_HEADER: [{'key': DEBUG_HEADER, 'value': DEBUG_HEADER_VALUE}]
        }
    }

    assert is_debug_header_set(request) is True

def test_get_querystring_from_request_empty():
    request = dict(
        querystring='',
    )

    querystring = get_querystring_from_request(request)

    assert querystring is None

def test_get_querystring_from_request():
    request = dict(
        querystring='test',
    )

    querystring = get_querystring_from_request(request)

    assert querystring == 'test'

def test_get_encrypted_timestamp_from_querystring_empty():
    token = get_token_from_querystring('', ENC_TIMESTAMP_QUERYSTRING_NAME)

    assert token is None

def test_get_token_from_querystring_no_token():
    token = get_token_from_querystring('test&abc&def', ENC_TIMESTAMP_QUERYSTRING_NAME)

    assert token is None

def test_return_encrypted_timestamp_querystring():
    token = get_token_from_querystring(f'test&abc&def&{ENC_TIMESTAMP_QUERYSTRING_NAME}=1633665600-2-5c2a2c2e', ENC_TIMESTAMP_QUERYSTRING_NAME)
    assert token == '1633665600-2-5c2a2c2e'

def test_return_encrypted_timestamp_querystring_empty():
    token = get_token_from_querystring(f'test&abc&def&{ENC_TIMESTAMP_QUERYSTRING_NAME}=', ENC_TIMESTAMP_QUERYSTRING_NAME)
    assert token == ''

def test_decrypt_timestamp(timestamp_cleartext, timestamp_encrypted):

    assert decrypt_timestamp(timestamp_encrypted, ENC_TIMESTAMP_KEY) == timestamp_cleartext

def test_decrypt_timestamp_empty_string():

        assert decrypt_timestamp('', ENC_TIMESTAMP_KEY) is None
        assert decrypt_timestamp(None, ENC_TIMESTAMP_KEY) is None

def test_is_decrypted_timestamp_valid_too_old(timestamp_cleartext, timestamp_encrypted):

    decrypt_timestamp = datetime.fromisoformat('2023-10-08T00:00:00')
    current_time = datetime.fromisoformat('2023-10-08T00:00:16')

    assert is_decrypted_timestamp_valid(decrypt_timestamp, current_time, max_age=15) is False


def test_is_decrypted_timestamp_valid_too_new(timestamp_cleartext, timestamp_encrypted):

    decrypt_timestamp = datetime.fromisoformat('2023-10-08T00:00:01')
    current_time = datetime.fromisoformat('2023-10-08T00:00:00')

    assert is_decrypted_timestamp_valid(decrypt_timestamp, current_time, max_age=15) is False

def test_is_decrypted_timestamp_valid(timestamp_cleartext, timestamp_encrypted):

    decrypt_timestamp = datetime.fromisoformat('2023-10-08T00:00:00')
    current_time = datetime.fromisoformat('2023-10-08T00:00:15')

    assert is_decrypted_timestamp_valid(decrypt_timestamp, current_time, max_age=15) is True

def test_lambda_handler_current_date_before_minimum_date(monkeypatch):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                    }
                }
            }
        ]
    }

    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2999-01-08T00:00:00")
    assert lambda_handler(event, {}) == {'status': '404', 'statusDescription': 'Not Found'}


def test_lambda_handler_current_date_after_minimum_date(monkeypatch, timestamp_encrypted):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            DEBUG_HEADER: [{'key': DEBUG_HEADER, 'value': DEBUG_HEADER_VALUE}],
                        },
                        'querystring': f'{ENC_TIMESTAMP_QUERYSTRING_NAME}={timestamp_encrypted.decode("utf-8")}'
                    }
                }
            }
        ]
    }

    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2000-01-08T00:00:00")
    assert lambda_handler(event, {}) == event['Records'][0]['cf']['request']

def test_lambda_handler_debug_header_is_set(monkeypatch):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            DEBUG_HEADER: [{'key': DEBUG_HEADER, 'value': DEBUG_HEADER_VALUE}],
                            'cookie': [{'key': 'Cookie', 'value': f'{FINALE_COOKIE_NAME}=true'}]
                        }
                    }
                }
            }
        ]
    }

    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2999-01-08T00:00:00")
    assert lambda_handler(event, {}) == event['Records'][0]['cf']['request']

def test_lambda_handler_debug_header_is_set_with_wrong_value(monkeypatch):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            DEBUG_HEADER: [{'key': DEBUG_HEADER, 'value': 'invalid-value'}]
                        }
                    }
                }
            }
        ]
    }

    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2999-01-08T00:00:00")
    assert lambda_handler(event, {}) == {'status': '404', 'statusDescription': 'Not Found'}

def test_lambda_handler_x_access_timestamp_is_too_old(monkeypatch, timestamp_cleartext, timestamp_encrypted):

    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'querystring': f'{ENC_TIMESTAMP_QUERYSTRING_NAME}={timestamp_encrypted.decode("utf-8")}'
                    }
                }
            }
        ]
    }

    # ensure we are in a valid timewindow
    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2000-01-08T00:00:00")
    # monkeypatch the current time to be 16 seconds after the timestamp
    def mock_get_current_time_in_utc():
        return timestamp_cleartext + timedelta(seconds=16)
    monkeypatch.setattr(handler, 'get_current_time_in_utc', mock_get_current_time_in_utc)

    assert lambda_handler(event, {}) == {'status': '404', 'statusDescription': 'Not Found'}

def test_lambda_handler_x_access_timestamp_is_too_new(monkeypatch, timestamp_cleartext, timestamp_encrypted):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'querystring': f'{ENC_TIMESTAMP_QUERYSTRING_NAME}={timestamp_encrypted.decode("utf-8")}'
                    }
                }
            }
        ]
    }

    # ensure we are in a valid timewindow
    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2000-01-08T00:00:00")
    # monkeypatch the current time to be 16 seconds after the timestamp
    def mock_get_current_time_in_utc():
        return timestamp_cleartext - timedelta(seconds=1)
    monkeypatch.setattr(handler, 'get_current_time_in_utc', mock_get_current_time_in_utc)

    assert lambda_handler(event, {}) == {'status': '404', 'statusDescription': 'Not Found'}

def test_lambda_handler_x_access_timestamp_is_valid(monkeypatch, timestamp_cleartext, timestamp_encrypted):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'querystring': f'{ENC_TIMESTAMP_QUERYSTRING_NAME}={timestamp_encrypted.decode("utf-8")}'
                    }
                }
            }
        ]
    }

    # ensure we are in a valid timewindow
    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2000-01-08T00:00:00")
    # monkeypatch the current time to be 16 seconds after the timestamp
    def mock_get_current_time_in_utc():
        return timestamp_cleartext
    monkeypatch.setattr(handler, 'get_current_time_in_utc', mock_get_current_time_in_utc)

    assert lambda_handler(event, {}) == event['Records'][0]['cf']['request']

def test_lambda_handler_visited_cookie_is_set_but_minimum_date_not_reached(monkeypatch, timestamp_cleartext):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            'cookie': [{'key': 'Cookie', 'value': f'{FINALE_COOKIE_NAME}=true'}]
                        }
                    }
                }
            }
        ]
    }

    # ensure we are in a valid timewindow
    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2999-01-08T00:00:00")
    # monkeypatch the current time to be 16 seconds after the timestamp
    def mock_get_current_time_in_utc():
        return timestamp_cleartext
    monkeypatch.setattr(handler, 'get_current_time_in_utc', mock_get_current_time_in_utc)

    assert lambda_handler(event, {}) == {'status': '404', 'statusDescription': 'Not Found'}

def test_lambda_handler_visited_cookie_is_set(monkeypatch, timestamp_cleartext):
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            'cookie': [{'key': 'Cookie', 'value': f'{FINALE_COOKIE_NAME}=true'}]
                        }
                    }
                }
            }
        ]
    }

    # ensure we are in a valid timewindow
    monkeypatch.setattr(handler, 'MINIMUM_DATE', "2000-01-08T00:00:00")
    # monkeypatch the current time to be 16 seconds after the timestamp
    def mock_get_current_time_in_utc():
        return timestamp_cleartext
    monkeypatch.setattr(handler, 'get_current_time_in_utc', mock_get_current_time_in_utc)

    assert lambda_handler(event, {}) == event['Records'][0]['cf']['request']
