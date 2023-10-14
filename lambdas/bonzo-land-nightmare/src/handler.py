#!/usr/bin/env python
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import json
# the s3 bucket for the nightmare content!
# hardcoded to speed up delivery at the edge
NIGHTMARE_DOMAIN = 'bonzo-land-website-nightmare.s3.eu-west-2.amazonaws.com'

# the times in between the nightmare mode is active
# attention: make sure nightmare_end ends after nightmare_start
# the code is not handling it well if this is not the case ;-)
DEFAULT_NIGHTMARE_START = '03:00'
DEFAULT_NIGHTMARE_END = '03:03'

# header the nigtmare mode testing
# if the header is set to the value below the nightmare mode will be active
DEBUG_HEADER = 'x-enable-dread-for-all-rustyquill-employees'
DEBUG_HEADER_VALUE = 'DREAD-FOR-ALL-BECAUSE-WE-ARE-ALL-LIKE-THIS'

def emit_event(reason: str, status: str, client_ip: str, timezone: str, lambda_time: str):
    """
    emit json formatted log event
    """

    print(json.dumps(
        dict(
            reason=reason,
            status=status,
            client_ip=client_ip,
            timezoe=timezone,
            lambda_time=lambda_time,
        )
    ))


def is_nightmare(nightmare_header: bool, timezone: str, nightmare_start: str, nightmare_end: str):
    """
    returns true if nightmare mode is active
    """

    # nightmare mode is active if the custom header 'X-ENABLE-NIGHTMARE-MODE'
    # is set with the value 'DREAD-FOR-ALL'
    if nightmare_header:
        return True

    # if there is no timezone info given we assume the timezone is london!
    if not timezone:
        print('WARNING: no timezone found. defaulting to europe/london')
        timezone = 'Europe/London'

    # and nightmare mode is active if the client is visiting during the witching hour
    # first we get the current time in the clients timezone (without microseconds, we dont need that kind of precision)
    current_time = datetime.now(tz=ZoneInfo(timezone)).replace(microsecond=0)

    nightmare_start_hour, nightmare_start_minute = get_hour_and_minute(
        nightmare_start)
    nightmare_end_hour, nightmare_end_minute = get_hour_and_minute(
        nightmare_end)

    start_time = current_time.replace(
        minute=nightmare_start_minute, hour=nightmare_start_hour, second=0)
    end_time = current_time.replace(
        minute=nightmare_end_minute, hour=nightmare_end_hour, second=0)

    if start_time <= current_time and current_time < end_time:
        return True

    return False


def get_hour_and_minute(timestring: str):
    """
    splits the given timestring and returns its hour and minute as int
    """

    return int(timestring.split(':')[0]), int(timestring.split(':')[1])


def get_request_from_event(event: dict):
    """
    returns the request from the event
    """

    request = None
    records = event.get('Records')

    if records:
        request = records[0].get('cf', {}).get('request', None)

    return request


def get_domainname_header_and_timezone_from_request(request: dict):
    """
    returns the domainname, querystring and timezone from the given event
    """

    timezone = None
    timezone_header = request.get('headers', {}).get(
        'cloudfront-viewer-time-zone', [])
    if timezone_header:
        timezone = timezone_header[0].get('value', None)

    header = False
    nightmare_header = request.get('headers', {}).get(
        DEBUG_HEADER, [])
    if nightmare_header:
        if nightmare_header[0].get('value', '') == DEBUG_HEADER_VALUE:
            header = True

    domainname = request.get('origin', {}).get(
        's3', {}).get('domainName', None)

    return domainname, header, timezone

def get_client_ip_from_request(request: dict) -> str:
    """
    returns the client ip from the given event
    """

    client_ip = request.get('clientIp', '')

    if not client_ip:
        return None

    return client_ip

def lambda_handler(event, context):
    """
    serve the "normal" website or the "nightmare" version
    depending on the clients current time
    """

    request = get_request_from_event(event=event)
    domainname, header, timezone = get_domainname_header_and_timezone_from_request(
        request=request)
    client_ip = get_client_ip_from_request(request=request)

    # this case shouldnt happen but if the domain name is already pointing to
    # the nightmare domain just return the request as is
    if domainname == NIGHTMARE_DOMAIN:
        print('WARNING: domainname is already nightmare domain. returning request as is')
        return request

    # setup nightmare times
    nightmare_start = os.getenv('NIGHTMARE_START', DEFAULT_NIGHTMARE_START)
    nightmare_end = os.getenv('NIGHTMARE_END', DEFAULT_NIGHTMARE_END)

    # time reported in event log
    lambda_time = datetime.now(tz=ZoneInfo(timezone)).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

    # if we are in the nightmare lets switch origins around ;-)
    if is_nightmare(nightmare_header=header, timezone=timezone, nightmare_start=nightmare_start, nightmare_end=nightmare_end):
        try:
            emit_event(reason='nightmare', status='active', client_ip=client_ip, timezone=timezone, lambda_time=lambda_time)
            request['origin']['s3']['domainName'] = NIGHTMARE_DOMAIN
            request['headers']['host'] = [
                {'key': 'host', 'value': NIGHTMARE_DOMAIN}]
        except BaseException as ex:
            print(f'ERROR: {ex}')

    emit_event(reason='normal', status='active', client_ip=client_ip, timezone=timezone, lambda_time=lambda_time)
    return request
