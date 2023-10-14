from telnetlib3 import create_server, TelnetReader, TelnetWriter, TelnetServer
from .prompt import TelnetPrompt
from .session import TelnetSession
from .commands import on_command

import asyncio
import logging
import signal

class TelnetServer():
    host: str
    port: int
    threhsold: int

    def __init__(self, host: str, port: int, threshold: int, remove_random_char_threshold: float, replace_random_char_threshold) -> None:
        """ initialize the telnet server """

        self.host = host
        self.port = port
        self.threhsold = threshold
        self.remove_random_char_threshold = remove_random_char_threshold
        self.replace_random_char_threshold = replace_random_char_threshold

    async def _sigterm_handler(self) -> None:
        """ handle shutdown more or less gracefully """

        logging.warning("SIGTERM received, closing server.")

        self.server.close()

    async def _get_user_input(self, reader: TelnetReader, session: TelnetSession) -> None:
        """ handle the user input, store the last input if available """

        # if last input is empty, current input is empty and current line is empty
        # we can be kinda sure that the user is freshly connected.abs
        is_first_input = False
        if session.last_input_is_empty() and session.current_input_is_empty() and session.current_line_is_empty():
            is_first_input = True

        session.last_input = session.input
        session.input = await reader.read(1)
        # if first input the input is the last input
        if is_first_input:
            session.last_input = session.input

    async def _handle_user_input(self, reader: TelnetReader, writer: TelnetWriter, session: TelnetSession, prompt: TelnetPrompt) -> None:
        """ handle the users input """

        if session.input_is_carriage_return():
            if session.current_line_is_empty():
                logging.debug('Hit enter on empty line')
                return
            prompt.print_new_line()
            await on_command(session=session, prompt=prompt)
            session.clear_current_line()
        # if player hits ctrl-c clear the screen
        elif session.input_is_ctrl_c():
            session.clear_current_line()
            session.clear_input()
            prompt.flush()
        # if a player hits backspace remove the last char from the current line
        elif session.input_is_backspace():
            if session.current_line_is_empty():
                return
            prompt.backspace()
            session.remove_last_char_from_current_line()
        # else print the current user input
        else:
            prompt.print_message(message=session.input.upper(), command_count=0, newline=False)
            session.append_input_to_current_line()

    async def shell(self, reader: TelnetReader, writer: TelnetWriter) -> None:
        """ telnet program provided by server """

        prompt = TelnetPrompt(writer=writer, remove_random_char_threshold=self.remove_random_char_threshold, replace_random_char_threshold=self.replace_random_char_threshold)
        session = TelnetSession(threshold=self.threhsold)
        prompt.print_welcome_message()
        try:
            while not writer.transport.is_closing():
                try:
                    logging.debug(f'Current line: {session.current_line}, last input: {ord(session.last_input)}, current input: {ord(session.input)}')
                except Exception:
                    pass

                # if no user input is given just print an empty command prompt
                if session.current_line_is_empty() and not session.last_input_is_crlf_or_backspace() and not session.input_is_backspace():
                    prompt.print_command_prompt()

                await self._get_user_input(reader=reader, session=session)
                await self._handle_user_input(reader=reader, writer=writer, session=session, prompt=prompt)

        except AttributeError as ae:
            # ugly exception when the stream closes. we just ignore it
            # perfectly fine for our use case ;-)
            if str(ae) != "'NoneType' object has no attribute 'is_closing'":
                raise ae
            else:
                pass


    async def run(self) -> None:
        """ run the telnet server """

        logging.info(f"Starting telnet server on {self.host}:{self.port}")

        loop = asyncio.get_event_loop()
        # self.server = await create_server(host=self.host, port=self.port, shell=self.shell)
        self.server = await create_server(host=self.host, port=self.port, shell=self.shell)
        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self._sigterm_handler()))

        try:
            await self.server.wait_closed()
        finally:
            loop.remove_signal_handler(signal.SIGTERM)

        logging.info("telnet server stopped.")


