from dataclasses import dataclass, field
from typing import Dict, List
import random

@dataclass
class Command():
    """ a command """

    command: str
    help_text: str
    usage_text: str
    parameter_count: int
    parameters: List[str] = field(default_factory=list)

    def is_valid_syntax(self) -> bool:
        """ check if the syntax is valid """

        return len(self.parameters) == self.parameter_count


@dataclass
class PlayerCommandCount():
    """ representa all possible command counts of a pluer """

    threshold: int
    command_count: Dict[str, int] = field(default_factory=dict)

    def increase_command_count(self, command: str) -> None:
        """ increase the command count """

        if command not in self.command_count:
            self.command_count[command] = 0

        self.command_count[command] += 1

    def get_command_count(self, command: str = None) -> int:
        """ get the command count """

        if command is None:
            return sum(self.command_count.values())

        if command not in self.command_count:
            return 0

        return self.command_count[command]

    def is_threshold_reached(self) -> bool:
        """ check if the threshold is reached """

        return self.get_command_count() > self.threshold

    def threshold_reached_normalized(self) -> float:
        """ get the normalized threshold """

        n = self.get_command_count() / self.threshold
        if n > 1:
            return 1

        return n

@dataclass
class TelnetMessage():
    """ a telnet message, depending on the given count it will print a different message """

    # if the count is below this threshold only print normal messages
    # if the count is above this threshold print normal and creepy messages
    mixed_threshold: int
    # if the count is above this threshold only print creepy messages
    creepy_threshold: int

    normal_messages: List[str] = field(default_factory=list)
    creepy_messages: List[str] = field(default_factory=list)


    def get_message(self, count: int = 0) -> str:
        """ get the message """

        if count > self.mixed_threshold and count <= self.creepy_threshold:
            return random.choice(self.normal_messages + self.creepy_messages)

        if count > self.creepy_threshold:
            if self.creepy_messages:
                return random.choice(self.creepy_messages)

        return random.choice(self.normal_messages)



