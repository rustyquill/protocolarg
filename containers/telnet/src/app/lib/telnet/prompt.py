from telnetlib3 import TelnetWriter
import logging
from typing import Dict, List
from .messages import WELCOME_PROMPT, LIST_RESPONSE, ERROR_PROMPT, KEY_PROMPT, SESSION_PROMPT
from .messages import WRONG_PRINTER_PROMPT, WRONG_FILE_PROMPT, AUTH_SYSTEM_BROKEN_PROMPT
from .messages import AUTH_RESPONSE, NETSTAT_RESPONSE, PING_RESPONSE
from .messages import PRINT_RESPONSE, PRINTER_RESPONSE, WHOAMI_RESPONSE
from .types import PlayerCommandCount
import random
import textwrap
from datetime import datetime

class TelnetPrompt():
    """ custom telnet prompt used by a telnet server """

    def __init__(self, writer: TelnetWriter, remove_random_char_threshold: float, replace_random_char_threshold: float) -> None:
        """ initialize the telnet prompt """

        self.writer: TelnetWriter = writer
        self.remove_random_char_threshold = remove_random_char_threshold
        self.replace_random_char_threshold = replace_random_char_threshold

    def _print(self, message: str, command_count: PlayerCommandCount = None, newline: bool = True, mangle_message = True) -> None:
        """ print a message to the telnet prompt """

        msg = message
        if command_count and mangle_message:
            msg = self._mangle_message(message=message, threshold_percentage=command_count.threshold_reached_normalized(), remove_random_char_threshold=self.remove_random_char_threshold, replace_random_char_threshold=self.replace_random_char_threshold)

        if command_count and command_count.is_threshold_reached():
            msg = f'{ERROR_PROMPT}{msg}'
        if newline:
            msg += '\r\n'
        self.writer.write(msg)

    def _remove_random_chars(self, message: str, range_start: int, range_end: int, characters: List[str]) -> str:
        """ remove a random amount of characters from the message """

        msg = ''
        for idx, char in enumerate(message):
            if idx % random.randint(a=range_start, b=range_end) == 0 and idx != 0:
                msg += random.choice(characters)
            else:
                msg += char

        return msg

    def _mangle_message(self, message: str, threshold_percentage: float, remove_random_char_threshold: float, replace_random_char_threshold: float) -> str:
        """ mangles the given message depending on the command count """

        # calculate mangling thresholds
        # if 30% of the threshold is reached, start mangling by removing a random amount of characters from the message
        # if 575% of the threshold is reached, start mangling by replacing a random amount of characters from the message with a random character

        msg = message
        if threshold_percentage > remove_random_char_threshold:
            msg = self._remove_random_chars(message=msg, range_start=10, range_end=12, characters=[' '])
        if threshold_percentage > replace_random_char_threshold:
            msg = self._remove_random_chars(message=msg, range_start=4, range_end=8, characters=['X', '$', '%', '#', '!', '&', '@', '-', '_',  '?', '.'])

        return msg

    def print_welcome_message(self) -> None:
        """ print a welcome message to the telnet prompt """

        self._print(message=WELCOME_PROMPT)

    def print_unknown_command(self, command: str, command_count: PlayerCommandCount) -> None:
        """ print a message to the telnet prompt """

        self._print(message=f'Unknown command: {command}\r\nType HELP for a list of commands', command_count=command_count)

    def print_help_message(self, command_count: PlayerCommandCount, commands: Dict[str, str]) -> None:
        """ print the help message """

        msg = 'Available commands:\r\n'
        for command, description in sorted(commands.items()):
            msg += f"{command} - {description}\r\n"

        self._print(message=msg, command_count=command_count)

    def print_goodbye_message(self, command_count: PlayerCommandCount) -> None:
        """ print a goodbye message to the telnet prompt """

        # no goodbye message for you!
        # self._print(message="", command_count=command_count)
        pass

    def print_command_prompt(self) -> None:
        """ print a command prompt to the telnet prompt """

        self._print(message='>>> ', newline=False)

    def print_message(self, message: str, newline: bool = True, command_count: PlayerCommandCount = 0) -> None:
        """ print a message to the telnet prompt """

        self._print(message=message, command_count=command_count, newline=newline)

    def flush(self) -> None:
        """ flush the telnet prompt """

        self._print(message='\x1b[2J\x1b[H', newline=False)

    def backspace(self) -> None:
        """ remove the last char from the telnet prompt """

        self._print(message='\b \b', newline=False)

    def print_new_line(self) -> None:
        """ print a new line to the telnet prompt """

        self._print(message='\r\n', newline=False)

    def print_auth(self, command_count: PlayerCommandCount, parameters: List[str]) -> None:
        """ print a auth message to the telnet prompt """

        if command_count.is_threshold_reached():
            self._print(message=AUTH_SYSTEM_BROKEN_PROMPT, command_count=command_count)
            return

        msg = AUTH_RESPONSE.get_message(count=command_count.get_command_count('AUTH'))
        self._print(message=msg, command_count=command_count)

    def print_netstat(self, command_count: PlayerCommandCount) -> None:
        """ print a netstat message to the telnet prompt """

        msg = NETSTAT_RESPONSE.get_message(count=0)

        self._print(message=msg, command_count=command_count)

    def print_ping(self, command_count: PlayerCommandCount, parameters: List[str]) -> None:
        """ print a ping message to the telnet prompt """

        msg = PING_RESPONSE.get_message(count=0).format(ip=parameters[0])

        self._print(message=msg, command_count=command_count)

    def print_print(self, command_count: PlayerCommandCount, parameters: List[str]) -> None:
        """ print a printerp message to the telnet prompt """

        # if players try to print something before threshold is reached and authentication is broken
        # print auth required message
        if not command_count.is_threshold_reached():
            self._print(message=PRINT_RESPONSE.get_message(count=0), command_count=command_count)
            return

        # the print command is the solution for our players
        # if they are trying to print anything which is not the solution they just get an error message
        # if they print the key they receive the key as base64 encoded string
        if parameters[0] != '4':
            self._print(message=WRONG_PRINTER_PROMPT, command_count=command_count)
            return
        if parameters[1] != '7':
            self._print(message=WRONG_FILE_PROMPT, command_count=command_count)
            return

        logging.warning('player discovered key')
        self._print(message='\r\n'.join(textwrap.wrap(KEY_PROMPT, 64)), mangle_message=False, command_count=command_count)


    def print_printer(self, command_count: PlayerCommandCount) -> None:
        """ print a printer message to the telnet prompt """

        msg = PRINTER_RESPONSE.get_message(count=0)

        self._print(message=msg, command_count=command_count)

    def print_whoami(self, command_count: PlayerCommandCount) -> None:
        """ print a whoami message to the telnet prompt """

        if command_count.is_threshold_reached():
            self._print(message=AUTH_SYSTEM_BROKEN_PROMPT, command_count=command_count)
            return

        msg = WHOAMI_RESPONSE.get_message(count=command_count.get_command_count('WHOAMI'))

        self._print(message=msg, command_count=command_count)

    def print_list(self, command_count: PlayerCommandCount) -> None:
        """ print a list message to the telnet prompt """

        msg = LIST_RESPONSE.get_message(count=0)
        self._print(message=msg, command_count=command_count)

    def print_session(self, command_count: PlayerCommandCount, session_id: int, start_time: datetime) -> None:
        """ print a session message to the telnet prompt """

        resource_usage = 'OK'
        if command_count.is_threshold_reached():
            resource_usage = 'ERROR'
        elif command_count.threshold_reached_normalized() >= self.replace_random_char_threshold:
            resource_usage = 'CRITICAL'
        elif command_count.threshold_reached_normalized() >= self.remove_random_char_threshold:
            resource_usage = 'HIGH'

        msg = SESSION_PROMPT.format(
            id=session_id,
            start=int(start_time.timestamp()),
            duration=int((datetime.utcnow() - start_time).total_seconds()),
            resource=resource_usage
        )
        self._print(message=msg, command_count=command_count)
