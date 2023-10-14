# this file defines the different emails that are sent out
# depending on the recipient, subject and body of the email

from typing import List, Dict, Any
import yaml
import boto3
from botocore.config import Config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

class EmailFilter:
    """
    defines a simple text filter
    it simply checks if a given string contains the given filter string
    """
    filter: List[str]

    def __init__(self, filter: List[str]):
        self.filter = filter

    def matches(self, text: str) -> bool:
        # return a match if no filter is defined
        # or if the given text matches any of the given filters

        if len(self.filter) == 0:
            return True

        for f in self.filter:
            if f.lower() in text.lower():
                return True


        return False

class EmailAttachment:
    """
    defines an email attachment stored in s3
    """

    name: str
    bucket: str
    key: str
    region: str

    def __init__(self, name: str, bucket: str, region: str, key: str):
        self.name = name
        self.bucket = bucket
        self.key = key
        self.region = region


    def download(self) -> str:
        """
        download the attachment from s3
        """

        # retrieve from s3 bucket
        try:
            s3 = boto3.client('s3', config=Config(region_name=self.region))
            return s3.get_object(Bucket=self.bucket, Key=self.key)['Body'].read()
        except Exception as ex:
            raise Exception(f'could not retrieve attachment from s3: {ex}')

class Email:
    filters = Dict[str, EmailFilter]
    attachments = List[EmailAttachment]

    subject = str
    body = str


    def message(self, from_email: str, to_email: str) -> MIMEMultipart:
        """ returns a mime email message """

        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = from_email
        msg['To'] = to_email

        msg.attach(MIMEText(self.body, 'html'))

        for attachment in self.attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.download())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment.name}')
            msg.attach(part)

        return msg


def return_email_from_email_template(email_template: Dict[str, Any]) -> Email:
    """
    takes an email templates loaded from yaml and returns a Email object
    """

    template = Email()
    template.attachments = []
    template.subject = email_template.get('subject', '')
    template.body = email_template.get('body', '')
    template.filters = dict(
            sender=EmailFilter(email_template.get('filters', {}).get('sender', [])),
            recipient=EmailFilter(email_template.get('filters', {}).get('recipient', [])),
            subject=EmailFilter(email_template.get('filters', {}).get('subject', [])),
            body=EmailFilter(email_template.get('filters', {}).get('body', []))
    )

    for attachment in email_template.get('attachments', []):
        template.attachments.append(
            EmailAttachment(
                name=attachment.get('name', ''),
                bucket=attachment.get('bucket', ''),
                key=attachment.get('key', ''),
                region=attachment.get('region', '')
            )
        )

    return template

def load_email_templates(yaml_file: str) -> List[Email]:
    """
    parse the given yaml file and return a list of Email objects
    """

    email_templates = []

    with open(yaml_file, 'r') as stream:
        try:
            f = yaml.safe_load(stream)
            for e in f.get('emails', []):
                email_templates.append(
                    return_email_from_email_template(e)
                )
        except yaml.YAMLError as exc:
            raise(exc)

    return email_templates

