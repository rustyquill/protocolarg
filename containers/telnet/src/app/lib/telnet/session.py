from .types import PlayerCommandCount
from datetime import datetime
from random import randint
class TelnetSession():
    last_input: str
    input: str
    current_line: str
    session_id: str
    start_time: datetime
    player_command_count: PlayerCommandCount

    def __init__(self, threshold: int) -> None:
        """ initialize the telnet session """

        self.input = ''
        self.last_input = ''
        self.current_line = ''
        self.session_id = randint(100000, 999999)
        self.start_time = datetime.utcnow()
        self.player_command_count = PlayerCommandCount(threshold=threshold)

    def clear_current_line(self) -> None:
        """ clear the current line """

        self.current_line = ''

    def clear_input(self) -> None:
        """ clear the input """

        self.input = ''
        self.last_input = ''

    def current_line_is_empty(self) -> bool:
        """ check if the current line is empty """

        return self.current_line == ''

    def last_input_is_empty(self) -> bool:
        """ check if the last input is empty """

        return self.last_input == ''

    def current_input_is_empty(self) -> bool:
        """ check if the current input is empty """

        return self.input == ''

    def input_is_carriage_return(self) -> bool:
        """ check if the current command is a carriage return """

        return self.input == '\r'

    def input_is_ctrl_c(self) -> bool:
        """ check if the current command is a ctrl-c """

        return self.input == '\x03'

    def input_is_backspace(self) -> bool:
        """ check if the current command is a backspace """

        return self.input == '\x7f'

    def append_input_to_current_line(self) -> None:
        """ append the input to the current line """

        self.current_line += self.input

    def remove_last_char_from_current_line(self) -> None:
        """ remove the last char from the current line """

        self.current_line = self.current_line[:-1]

    def last_input_is_crlf_or_backspace(self) -> bool:
        """ check if the last input is not a crlf or backspace """

        return self.last_input in ['\r', '\x7f']

    def increase_command_count(self, command: str) -> None:
        """ increase the command count """

        if command not in self.current_command_count:
            self.current_command_count[command] = 0

        self.current_command_count[command] += 1

    def get_command_count(self, command: str = None) -> int:
        """ return the command count of all commands or a specific command """

        if command not in self.current_command_count:
            total = 0
            for command, count in self.current_command_count.items():
                total += count
            return total

        return self.current_command_count[command]
