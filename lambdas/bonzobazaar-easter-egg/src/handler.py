#!/usr/bin/env python
import os
import json


EASTER_EGG_DOMAIN = 'protocalarg-easter-eggs.s3.eu-west-2.amazonaws.com'
EASTER_EGG_FILE = '/bonzo-brigade/index.html'

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


def get_request_from_event(event: dict):
    """
    returns the request from the event
    """

    request = None
    records = event.get('Records')

    if records:
        request = records[0].get('cf', {}).get('request', None)

    return request


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
    client_ip = get_client_ip_from_request(request=request)

    emit_event(reason='easter-egg', status='allowed', client_ip=client_ip)
    request['uri'] = EASTER_EGG_FILE
    request['origin']['s3']['domainName'] = EASTER_EGG_DOMAIN
    request['headers']['host'] = [
        {'key': 'host', 'value': EASTER_EGG_DOMAIN}]
    return request
