#!/usr/bin/env python


from datetime import datetime, timedelta
from handler import get_request_from_event, get_domainname_header_and_timezone_from_request, is_nightmare, NIGHTMARE_DOMAIN, lambda_handler, get_hour_and_minute
from handler import DEBUG_HEADER, DEBUG_HEADER_VALUE

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
                    'clientIp': '137.22.176.102',
                    'headers': {
                        'host': [{'key': 'Host', 'value': 'bonzo-static-website.s3.eu-west-2.amazonaws.com'}],
                        'cloudfront-is-mobile-viewer': [{'key': 'CloudFront-Is-Mobile-Viewer', 'value': 'false'}],
                        'cloudfront-is-tablet-viewer': [{'key': 'CloudFront-Is-Tablet-Viewer', 'value': 'false'}],
                        'cloudfront-is-smarttv-viewer': [{'key': 'CloudFront-Is-SmartTV-Viewer', 'value': 'false'}],
                        'cloudfront-is-desktop-viewer': [{'key': 'CloudFront-Is-Desktop-Viewer', 'value': 'true'}],
                        'cloudfront-is-ios-viewer': [{'key': 'CloudFront-Is-IOS-Viewer', 'value': 'false'}],
                        'cloudfront-is-android-viewer': [{'key': 'CloudFront-Is-Android-Viewer', 'value': 'false'}],
                        'accept-language': [{'key': 'Accept-Language', 'value': 'en-US,en;q=0.5'}],
                        'accept': [{'key': 'Accept', 'value': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}],
                        'te': [{'key': 'TE', 'value': 'trailers'}],
                        'cloudfront-forwarded-proto': [{'key': 'CloudFront-Forwarded-Proto', 'value': 'https'}],
                        'x-forwarded-for': [{'key': 'X-Forwarded-For', 'value': '137.22.176.102'}],
                        'user-agent': [{'key': 'User-Agent', 'value': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0'}],
                        'via': [{'key': 'Via', 'value': '1.1 a5a437fd8aae10e73421b238277aaafa.cloudfront.net (CloudFront)'}],
                        'accept-encoding': [{'key': 'accept-encoding', 'value': 'gzip, deflate, br'}],
                        'upgrade-insecure-requests': [{'key': 'upgrade-insecure-requests', 'value': '1'}],
                        'sec-fetch-dest': [{'key': 'sec-fetch-dest', 'value': 'document'}],
                        'sec-fetch-mode': [{'key': 'sec-fetch-mode', 'value': 'navigate'}],
                        'sec-fetch-site': [{'key': 'sec-fetch-site', 'value': 'none'}],
                        'sec-fetch-user': [{'key': 'sec-fetch-user', 'value': '?1'}],
                        'cloudfront-viewer-http-version': [{'key': 'CloudFront-Viewer-HTTP-Version', 'value': '2.0'}],
                        'cloudfront-viewer-country': [{'key': 'CloudFront-Viewer-Country', 'value': 'GB'}],
                        'cloudfront-viewer-country-name': [{'key': 'CloudFront-Viewer-Country-Name', 'value': 'United Kingdom'}],
                        'cloudfront-viewer-country-region': [{'key': 'CloudFront-Viewer-Country-Region', 'value': 'WLS'}],
                        'cloudfront-viewer-country-region-name': [{'key': 'CloudFront-Viewer-Country-Region-Name', 'value': 'Wales'}],
                        'cloudfront-viewer-city': [{'key': 'CloudFront-Viewer-City', 'value': 'Ewloe'}],
                        'cloudfront-viewer-postal-code': [{'key': 'CloudFront-Viewer-Postal-Code', 'value': 'CH5'}],
                        'cloudfront-viewer-time-zone': [{'key': 'CloudFront-Viewer-Time-Zone', 'value': 'Europe/London'}],
                        'cloudfront-viewer-latitude': [{'key': 'CloudFront-Viewer-Latitude', 'value': '53.19630'}],
                        'cloudfront-viewer-longitude': [{'key': 'CloudFront-Viewer-Longitude', 'value': '-3.05530'}],
                        'cloudfront-viewer-address': [{'key': 'CloudFront-Viewer-Address', 'value': '137.22.176.102:60955'}],
                        'cloudfront-viewer-tls': [{'key': 'CloudFront-Viewer-TLS', 'value': 'TLSv1.3:TLS_AES_128_GCM_SHA256:fullHandshake'}],
                        'cloudfront-viewer-asn': [{'key': 'CloudFront-Viewer-ASN', 'value': '26557'}]
                    },
                    'method': 'GET',
                    'origin': {
                        's3': {
                            'authMethod': 'origin-access-identity',
                            'customHeaders': {},
                            'domainName': 'bonzo-static-website.s3.eu-west-2.amazonaws.com',
                            'path': '',
                            'region': 'eu-west-2'
                        }
                    },
                    'querystring': 'thisis-a-query-param=123&another=param',
                    'uri': '/index.html'
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


def test_get_domainname_header_and_timezone_from_request_empty_request():

    domainname, header, timezone = get_domainname_header_and_timezone_from_request({
    })
    assert domainname is None
    assert header is False
    assert timezone is None


def test_get_domainname_header_and_timezone_from_request_no_timezone_no_querystring():
    request = {
        'origin': {
            's3': {
                'domainName': 'domainName'
            }
        }
    }

    domainname, header, timezone = get_domainname_header_and_timezone_from_request(
        request)

    assert domainname == 'domainName'
    assert header is False
    assert timezone is None


def test_get_domainname_header_and_timezone_from_request_no_uri_no_querystring():
    request = {
        'headers': {
            'cloudfront-viewer-time-zone': [{'key': 'CloudFront-Viewer-Time-Zone', 'value': 'Europe/London'}],
        }
    }

    domainname, header, timezone = get_domainname_header_and_timezone_from_request(
        request)
    assert domainname is None
    assert header is False
    assert timezone == 'Europe/London'


def test_get_domainname_header_and_timezone_from_request_no_uri_no_timestamp():
    request = {
        'headers': {
            f'{DEBUG_HEADER}': [{'key': DEBUG_HEADER, 'value': DEBUG_HEADER_VALUE}],
        }
    }

    domainname, header, timezone = get_domainname_header_and_timezone_from_request(
        request)
    assert domainname is None
    assert header is True
    assert timezone is None


def test_get_domainname_header_and_timezone_from_request_no_uri_no_timestamp_wrong_header_value():
    request = {
        'headers': {
            'x-enable-nightmare-mode': [{'key': 'x-enable-nightmare-mode', 'value': 'Not the correct value!'}],
        }
    }

    domainname, header, timezone = get_domainname_header_and_timezone_from_request(
        request)
    assert domainname is None
    assert header is False
    assert timezone is None


def test_get_domainname_header_and_timezone_found():
    request = {
        'origin': {
            's3': {
                'domainName': 'domainName'
            }
        },
        'headers': {
            'cloudfront-viewer-time-zone': [{'key': 'CloudFront-Viewer-Time-Zone', 'value': 'Europe/London'}],
            f'{DEBUG_HEADER}': [{'key': DEBUG_HEADER, 'value': DEBUG_HEADER_VALUE}],
        },
    }

    domainname, header, timezone = get_domainname_header_and_timezone_from_request(
        request)
    assert domainname == 'domainName'
    assert header is True
    assert timezone == 'Europe/London'


def test_is_nightmare_querystring():
    nightmare = is_nightmare(
        nightmare_header=True,
        timezone=None,
        nightmare_start='00:00',
        nightmare_end='00:00'
    )

    assert nightmare is True


def test_is_nightmare_in_time():
    current_time = datetime.utcnow()
    start_time = current_time - timedelta(minutes=5)
    end_time = current_time + timedelta(minutes=5)

    nightmare = is_nightmare(
        nightmare_header=False,
        timezone='UTC',
        nightmare_start=start_time.strftime('%H:%M'),
        nightmare_end=end_time.strftime('%H:%M'))

    assert nightmare == True


def test_is_nightmare_out_time():
    current_time = datetime.utcnow()
    start_time = current_time - timedelta(minutes=10)
    end_time = current_time - timedelta(minutes=5)

    nightmare = is_nightmare(
        nightmare_header=False,
        timezone='UTC',
        nightmare_start=start_time.strftime('%H:%M'),
        nightmare_end=end_time.strftime('%H:%M'))

    assert nightmare == False


def test_get_hour_and_minute():
    hour, minute = get_hour_and_minute('03:00')

    assert hour == 3
    assert minute == 0


def test_nightmare_domain():
    assert NIGHTMARE_DOMAIN == 'bonzo-land-website-nightmare.s3.eu-west-2.amazonaws.com'


def test_lambda_handler():
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            'host': [{'key': 'Host', 'value': 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com'}],
                            'cloudfront-viewer-time-zone': [{'key': 'CloudFront-Viewer-Time-Zone', 'value': 'Europe/London'}],
                        },
                        'origin': {
                            's3': {
                                'domainName': 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com',
                            }
                        },
                    }
                }
            }
        ]
    }

    request = lambda_handler(event, {})
    assert request['origin']['s3']['domainName'] == 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com'
    assert request['headers']['host'][0]['value'] == 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com'


def test_lambda_handler_header():
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            'host': [{'key': 'Host', 'value': 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com'}],
                            'cloudfront-viewer-time-zone': [{'key': 'CloudFront-Viewer-Time-Zone', 'value': 'Europe/London'}],
                            'x-enable-nightmare-mode': [{'key': 'x-enable-nightmare-mode', 'value': 'Not the correct value'}],
                        },
                        'origin': {
                            's3': {
                                'domainName': 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com',
                            }
                        },
                    }
                }
            }
        ]
    }

    request = lambda_handler(event, {})
    assert request['origin']['s3']['domainName'] == 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com'
    assert request['headers']['host'][0]['value'] == 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com'


def test_lambda_handler_header_nightmare():
    event = {
        'Records': [
            {
                'cf': {
                    'request': {
                        'headers': {
                            'host': [{'key': 'Host', 'value': 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com'}],
                            'cloudfront-viewer-time-zone': [{'key': 'CloudFront-Viewer-Time-Zone', 'value': 'Europe/London'}],
                            f'{DEBUG_HEADER}': [{'key': DEBUG_HEADER, 'value': DEBUG_HEADER_VALUE}],
                        },
                        'origin': {
                            's3': {
                                'domainName': 'bonzo-land-website-active.s3.eu-west-2.amazonaws.com',
                            }
                        }
                    }
                }
            }
        ]
    }

    request = lambda_handler(event, {})
    assert request['origin']['s3']['domainName'] == 'bonzo-land-website-nightmare.s3.eu-west-2.amazonaws.com'
    assert request['headers']['host'][0]['value'] == 'bonzo-land-website-nightmare.s3.eu-west-2.amazonaws.com'
