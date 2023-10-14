#!/usr/bin/env python3

import asyncio
import click
import logging
from lib.telnet import TelnetServer


@click.command()
@click.option('--host', default='0.0.0.0', help='Host to listen on', envvar='HOST')
@click.option('--port', default=23, help='Port to listen on', envvar='PORT')
@click.option('--log-level', default='info', help='Log level', envvar='LOG_LEVEL')
@click.option('--threshold', default=35, help='how many commands until the system seems broken?', envvar='THRESHOLD')
@click.option('--remove-threshold', default=0.4, help='how many commands until a random char is removed?', envvar='REMOVE_HRESHOLD')
@click.option('--replace-threshold', default=0.75, help='how many commands until a random char is replaced?', envvar='REPLACE_THRESHOLD')
def main(host: str, port: int, log_level: str, threshold: int, remove_threshold: float, replace_threshold: float) -> None:
    """ start the telnet server """

    logging.basicConfig(level=logging.getLevelName(log_level.upper()))
    server = TelnetServer(host=host, port=port, threshold=threshold, remove_random_char_threshold=remove_threshold, replace_random_char_threshold=replace_threshold)
    asyncio.run(server.run())

if __name__ == '__main__':
    main()
