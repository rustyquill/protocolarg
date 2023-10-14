import logging
from typing import Callable, List, Optional
from .session  import TelnetSession
from .prompt import TelnetPrompt
from .types import Command

AVAILABLE_COMMANDS: List[Command] = [
    Command(
        command="AUTH",
        help_text="Authenticate with the server",
        usage_text="AUTH <username> <password>",
        parameter_count=2,
    ),
    Command(
        command="CLEAR",
        help_text="Clears the screen",
        usage_text="CLEAR",
        parameter_count=0,
    ),
    Command(
        command="EXIT",
        help_text="Exits the program",
        usage_text="EXIT",
        parameter_count=0,
    ),
    Command(
        command="HELP",
        help_text="Shows all available commands",
        usage_text="HELP",
        parameter_count=0,
    ),
    Command(
        command="NETSTAT",
        help_text="Shows the current network status",
        usage_text="NETSTAT",
        parameter_count=0,
    ),
    Command(
        command="PING",
        help_text="Ping a host",
        usage_text="PING <host>",
        parameter_count=1,
    ),
    Command(
        command="PRINT",
        help_text="Print a file to a network printer",
        usage_text="PRINT <printer id> <file id>",
        parameter_count=2,
    ),
    Command(
        command="PRINTER",
        help_text="Show available network printers",
        usage_text="PRINTER",
        parameter_count=0,
    ),
    Command(
        command="LIST",
        help_text="List all files on the system",
        usage_text="LIST",
        parameter_count=0,
    ),
    Command(
        command="WHOAMI",
        help_text="Shows the current user",
        usage_text="WHOAMI",
        parameter_count=0,
    ),
    Command(
        command="SESSION",
        help_text="Print session information",
        usage_text="SESSION",
        parameter_count=0,
    ),
]

def parse_command_line(command_line: str) -> Command:
    """ parse the given command line """

    command_line = command_line.strip()
    name = command_line.split(' ')[0].upper()
    parameters = command_line.split(' ')[1:]

    command: Command = None
    try:
        command = [command for command in AVAILABLE_COMMANDS if command.command == name][0]
    except IndexError:
        raise Exception(f"Unknown command: {name}")

    command.parameters = parameters
    return command


async def on_command(prompt: TelnetPrompt, session: TelnetSession) -> None:
    """ execute the given commmand if found """

    # parse the given command
    command = None
    try:
        command = parse_command_line(session.current_line)
    except Exception:
        # if no command is found print unknown command messahe
        prompt.print_unknown_command(session.current_line.upper(), command_count=session.player_command_count)
        return

    # if the command is not valid print the usage text
    if not command.is_valid_syntax():
        prompt.print_message(message=f'USAGE: {command.usage_text}', command_count=session.player_command_count)
        return

    # increase command count
    session.player_command_count.increase_command_count(command.command)
    logging.debug(session.player_command_count)

    if command.command == "AUTH":
        prompt.print_auth(command_count=session.player_command_count, parameters=command.parameters)
    elif command.command == "CLEAR":
        prompt.flush()
    elif command.command == "EXIT":
        prompt.print_goodbye_message(command_count=session.player_command_count)
        await prompt.writer.drain()
        prompt.writer.close()
    elif command.command == "HELP":
        command_help_texts = {}
        for command in AVAILABLE_COMMANDS:
            command_help_texts[command.command] = command.help_text
        prompt.print_help_message(command_count=session.player_command_count, commands=command_help_texts)
    elif command.command == "NETSTAT":
        prompt.print_netstat(command_count=session.player_command_count)
    elif command.command == "PING":
        prompt.print_ping(command_count=session.player_command_count, parameters=command.parameters)
    elif command.command == "PRINT":
        prompt.print_print(command_count=session.player_command_count, parameters=command.parameters)
    elif command.command == "PRINTER":
        prompt.print_printer(command_count=session.player_command_count)
    elif command.command == "LIST":
        prompt.print_list(command_count=session.player_command_count)
    elif command.command == "WHOAMI":
        prompt.print_whoami(command_count=session.player_command_count)
    elif command.command == "SESSION":
        prompt.print_session(command_count=session.player_command_count, start_time=session.start_time, session_id=session.session_id)
