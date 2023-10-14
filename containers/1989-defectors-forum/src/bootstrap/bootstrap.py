#!/usr/bin/env python3

"""
add usenet articles to the usenet server
"""

import os
import sys
import time
import subprocess
import signal
import datetime
from nntplib import NNTP, NNTPError
from typing import Optional, List, Any
import hashlib
import yaml
from dateutil.parser import parse
import psutil
import random
import base64
import textwrap

# hacky solution to collect all messges and replies
# instead of doing some fancy recursive function ;-)
MESSAGES: List[Any] = []

# env var to disable posting messages for local message rendering tests
NO_POSTING = os.getenv("NO_POSTING", 'False').lower() in ('true', '1', 't')

class NntpMessage():
    message_type: Optional[str] = 'plain'
    path: str = 'internetnews!not-for-mail'
    sender: str
    newsgroups: str
    subject: str
    in_reply_to: Optional[str] = None
    references: str = ""
    organization: Optional[str] = None
    date: datetime.datetime
    message: str
    message_id: str
    attachment: Optional[str] = None
    attachment_content: Optional[str] = None

    def __init__(self, sender: str, newsgroups: str, subject: str, message: str, date: datetime.datetime, in_reply_to: Optional[str] = None, organization: Optional[str] = None, replies: Optional[List[Any]] = None, references: str = None, message_type: str = 'plain', attachment: str = None):
        """ initialize message """
        self.message_type = message_type
        self.sender = sender
        self.newsgroups = newsgroups
        self.subject = subject
        self.message = message
        self.organization = organization
        self.attachment = attachment

        if not isinstance(date, datetime.datetime):
            self.date = parse(date)
        else:
            self.date = date

        # generate message id
        message_id = hashlib.md5(f"{self.sender}{self.newsgroups}{self.subject}{self.message}{self.date}".encode()).hexdigest()
        self.message_id = f'{message_id}@internetnews'

        # set reply message
        if in_reply_to:
            self.in_reply_to = in_reply_to
            self.references = f'<{self.in_reply_to}>'

        # setup references in order to create a thread
        if references:
            self.references = f'{references} {self.references}'

        # if message has an attachment, try to load it and encode it as base64
        if self.attachment:
            try:
                with open(os.path.join('messages', 'attachments', attachment), 'rb') as f:
                    self.attachment_content = '\n'.join(textwrap.wrap(base64.b64encode(f.read()).decode('utf-8'), 72))
            except Exception as e:
                print(f'could not load attachment {attachment}: {e}')
                self.message_type = 'plain'

        # if message has replies
        # create a new list with modified reply object and pass it allong
        if replies:
            replies_to_message = []
            for reply in replies:
                reply['in_reply_to'] = self.message_id
                reply['newsgroups'] = self.newsgroups
                reply['references'] = self.references
                replies_to_message.append(reply)
                # if no custom subject is set use the original subject with RE: as prefix
                if not reply.get('subject'):
                    reply['subject'] = f'RE: {self.subject}'

                if self.message_type == 'plain':
                    # add message history
                    history = f'On {self.date.strftime("%Y-%m-%d %H:%M")}, f{self.sender} wrote:\n'
                    for l in self.message.splitlines():
                        history += f'> {l}\n'
                    # usually the history is displayed on top of the message
                    # as most of our messages are short and people will be more used to email like history
                    # we attach the history to the end of the message
                    reply['message'] = f'{reply["message"]}\n\n---\n{history}'

            for reply in replies_to_message:
                MESSAGES.append(
                    NntpMessage(**reply)
                )

    def _plain_message(self) -> str:
        message: str = ""
        message += f"Path: {self.path}\n"
        message += f"From: {self.sender}\n"
        if self.organization:
            message += f"Organization: {self.organization}\n"
        message += f"Newsgroups: {self.newsgroups}\n"
        message += f"Subject: {self.subject}\n"
        message += f"Message-ID: <{self.message_id}>\n"
        message += f"Date: {self.date.strftime('%a, %d %b %Y %H:%M:%S %z')}\n"
        if self.in_reply_to:
            message += f"In-Reply-To: <{self.in_reply_to}>\n"
        if self.references:
            message += f"References: {self.references}\n"
        message += f"\n{self.message}\n"

        return message

    def _mixed_message(self) -> str:
        """
            returns a multipart/mixed message with a text/plain part and an picture attachment
            only used by our cat pictures!
            thanks to: https://github.com/majestrate/nntpchan/blob/master/doc/developer/protocol.md
        """
        boundary = '----------'
        boundary += ''.join(random.choice('0123456789ABCDEF') for i in range(24))

        message: str = ""
        message += f"Path: {self.path}\n"
        message += f"From: {self.sender}\n"
        if self.organization:
            message += f"Organization: {self.organization}\n"
        message += f"Newsgroups: {self.newsgroups}\n"
        message += f"Subject: {self.subject}\n"
        message += f"Message-ID: <{self.message_id}>\n"
        message += f"Date: {self.date.strftime('%a, %d %b %Y %H:%M:%S %z')}\n"
        if self.in_reply_to:
            message += f"In-Reply-To: <{self.in_reply_to}>\n"
        if self.references:
            message += f"References: {self.references}\n"
        message += f"Mime-Version: 1.0\n"
        message += f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\n"
        message += f"\nThis is a multi-part message in MIME format.\n"
        message += f"--{boundary}\n"
        message += f"Content-Type: text/plain; charset=utf-8\n"
        message += f"\n{self.message}"
        if self.attachment_content:
            message += f"\n--{boundary}\n"
            if self.attachment.endswith('.png'):
                message += f"Content-Type: image/png name=\"{self.attachment}\"\n"
            else:
                message += f"Content-Type: image/jpeg name=\"{self.attachment}\"\n"
            message += f"Content-Disposition: attachment; filename=\"{self.attachment}\"\n"
            message += f"Content-Transfer-Encoding: base64\n"
            message += f"\n{self.attachment_content}\n"
        message += f"\n{boundary}--\n"

        return message


    def __str__(self) -> str:
        """ return a valid innd message """

        if self.message_type == 'plain':
            return self._plain_message()

        if self.message_type == 'mixed':
            return self._mixed_message()


class NntpClient():
    """
    nntp client
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 119, readermode: bool = True):
        """
        initialize nntp client
        """

        self.host = host
        self.port = port
        self.readermode = readermode

    def post(self, message: NntpMessage):
        """
        post a message to the server
        """

        try:
            with(NNTP(host=self.host, port=self.port, readermode=self.readermode)) as nntp:
                nntp.post(str.encode(str(message)))
        except NNTPError as e:
            print(e)

class Innd():
    innd = None

    def start(self, timestamp: datetime.datetime):
        """
        start the innd process in a subprocess
        """
        innd_environ = os.environ.copy()
        innd_environ["FAKETIME"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # try to stop porcess before starting it
        self.stop()

        # start innd with fake date and time
        self.innd = subprocess.Popen(
            ["/usr/sbin/innd"],
            env=innd_environ,
        )

        # wait for innd to start
        self.wait_for_innd()

    def stop(self):
        """
        stop the innd process
        """

        try:
            with open("/run/innd/innd.pid", "r") as f:
                pid = int(f.read())
                os.kill(pid, signal.SIGKILL)
                wait_kill_counter = 0
                # ensure the process is killed before continuing
                while psutil.pid_exists(pid) and wait_kill_counter < 100:
                    time.sleep(0.1)
                    wait_kill_counter += 1

        except Exception:
            # pid file not found, so process may not be running
            pass

    def wait_for_innd(self):
        """
        wait for the innd process to accept connections
        """

        wait_counter = 0
        while wait_counter < 100:
            time.sleep(0.1)
            try:
                with(NNTP(host='127.0.0.1', port=119, readermode=True)) as nntp:
                    groups = nntp.list()
                    if len(groups) > 0:
                        return
            except Exception:
                pass
            wait_counter += 1

def post_message(message: NntpMessage):
    """ start innd with timestamp, post message and stop innd """

    innd = Innd()
    nntp_client = NntpClient()
    innd.stop()
    innd.start(timestamp=message.date)
    nntp_client.post(message)
    innd.stop()

def parse_messages(yaml_file: str = 'messages.yaml') -> None:
    """ parse messages from yaml file """

    with open(yaml_file, 'r') as f:
        messages = yaml.safe_load(f)['messages']

    for message in messages:
        MESSAGES.append(NntpMessage(**message))

    # sort messages by date
    MESSAGES.sort(key=lambda x: x.date)

def parse_messages_for_group(yaml_file: str, group: str):
    """ parse messages from yaml file and extend messages with newsgroup """

    MESSAGES.clear()
    with open(yaml_file, 'r') as f:
        messages = yaml.safe_load(f)['messages']

    for message in messages:
        message['newsgroups'] = group
        MESSAGES.append(NntpMessage(**message))

    # sort messages by date
    MESSAGES.sort(key=lambda x: x.date)

def main():
    """ main function, parse and load the different messages for the differnt forums """

    groups: Dict[str, str] = {
        'internetnews.anleitungen': 'messages/internetnews.anleitungen.yaml',
        'internetnews.berlin': 'messages/internetnews.berlin.yaml',
        'internetnews.ddr': 'messages/internetnews.ddr.yaml',
        'internetnews.mitglieder': 'messages/internetnews.mitglieder.yaml',
        'internetnews.regeln': 'messages/internetnews.regeln.yaml',
        'internetnews.ressourcen': 'messages/internetnews.ressourcen.yaml',
        'internetnews.sonstiges': 'messages/internetnews.sonstiges.yaml',
    }

    for group, filename in groups.items():
        parse_messages_for_group(yaml_file=filename, group=group)
        for i, message in enumerate(MESSAGES):
            print(f'posting message {i+1} of {len(MESSAGES)}: {message.message_id} - {message.sender} - {message.in_reply_to} - {message.references} - {message.date} - {message.subject}')
            post_message(message)

if __name__ == '__main__':
    main()
