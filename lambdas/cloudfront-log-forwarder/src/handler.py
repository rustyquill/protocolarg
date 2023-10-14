import urllib.parse
import botocore
import boto3
import os
from gzip import GzipFile
from io import BytesIO
from datetime import datetime
from operator import itemgetter, attrgetter

# Create an Amazon S3 and an Amazon CloudWatch Logs Client
s3 = boto3.client('s3')
logs = boto3.client('logs')

# Set Log Group name from env var, and use the same log stream name for the AWS Lambda funciton
log_group_name = os.environ['LOG_GROUP_NAME']
log_stream_name = os.environ['AWS_LAMBDA_LOG_STREAM_NAME']

# Debug logging if we need it
#boto3.set_stream_logger(name='botocore')

# Create a new log stream for this function container
try:
    create_log_stream_response = logs.create_log_stream(
    logGroupName=log_group_name,
    logStreamName=log_stream_name
    )
except botocore.exceptions.ClientError as error:
    print('Error Creating log stream')
    raise error

except botocore.exceptions.ParamValidationError as error:
    print('Param Validation error - creating log stream')



def put_log(records, *sequence_token ):
    # Put log event, hanlde error to get sequence token, returns up to date sequence token.

    # Sort the list by timestamp, since the log events in the batch must be in chronological ordered
    records = sorted(records,key=itemgetter('timestamp'))

    put_log_events_kwargs = {
        'logGroupName': log_group_name,
        'logStreamName': log_stream_name,
        'logEvents': records
    }

    try:
        if not sequence_token:
            print("no sequence token provided in args")
        else:
            print("sequence token provided in args")
            put_log_events_kwargs['sequenceToken'] = sequence_token[0]

        put_log_events_response = logs.put_log_events(**put_log_events_kwargs)
        sequence_token = put_log_events_response['nextSequenceToken']
        return put_log_events_response['nextSequenceToken']

    # Catch the missing or invalid sequence token error, this is one way to get the sequence token
    # The only place the sequence token is returned in the error is in the message, we have to parse out the token from the message.
    except (logs.exceptions.InvalidSequenceTokenException, logs.exceptions.DataAlreadyAcceptedException) as e:

        if e.response['Error']['Code'] == 'DataAlreadyAcceptedException':
            error_msg = e.response['Error']['Message']
            sequence_token = error_msg[len('The given batch of log events has already been accepted. The next batch can be sent with sequenceToken: '):]


        if e.response['Error']['Code'] == 'InvalidSequenceTokenException':
            error_msg = e.response['Error']['Message']
            sequence_token = error_msg[len('The given sequenceToken is invalid. The next expected sequenceToken is: '):]


        # Try again with the updated sequence token
        try:
            put_log_events_kwargs['sequenceToken'] = sequence_token
            put_log_events_response = logs.put_log_events(**put_log_events_kwargs)
            return put_log_events_response['nextSequenceToken']
        except Exception as e:
            print(e)
            print("Error putting log event")

    except Exception as e:
        print(e)
        print("Error putting log event")




def lambda_handler(event, context):
    records = []
    sequence_token = None
    records_byte_size = 0

    # Get our S3 bucket and key from the event context, URL decode the keyname
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')


    # Get S3 object, read the bytestream from the response and uncompress the body
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        bytestream = BytesIO(response['Body'].read())
        data = GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.')
        raise e

    for line in data.strip().split("\n"):
        # get rid of the column headers in the log
        if not line.startswith("#") and not "OhDear.app" in line:
            try:
                # Create a timestamp from the first 2 fields, and convert to ms
                split_line = line.split(sep="\t")
                timestamp = datetime.strptime(
                    '%s %s' % (split_line[0], split_line[1]),
                    '%Y-%m-%d %H:%M:%S'
                ).timestamp()

                time_in_ms = int(float(timestamp)*1000)

            except Exception as e:
                print(e)
                print("Failed to Covnert Time")

            # Check records array to see if we exceed payload limits if so, we need to publish the records, and clear out the records array:
            try:
                # size is calculated as the sum of all event messages in UTF-8, plus 26 bytes for each log event.
                line_count = len(records) +1
                bytes_overhead = line_count * 26

                # Get the total number of bytes for even in UTF-8
                line_encoded = line.strip().encode("utf-8", "ignore")

                # UTF 8 size of event
                line_byte_size = (line_encoded.__sizeof__())

                # UTF-8 size of records array
                records_byte_size = line_byte_size + records_byte_size

                # Total Payload Size
                payload_size = records_byte_size + bytes_overhead

            except Exception as e:
                print(e)
                print("Exception during utf8 conversion")


            if  payload_size >= 1048576 or line_count >= 10000 :
                try:
                    #payload size will be over 1 MB, or over the 10,000 record limit

                    # Write what we have now to CW Logs
                    if sequence_token is not  None:
                        sequence_token = put_log(records, sequence_token)
                    else:
                        sequence_token = put_log(records)

                    #Clear out the records list
                    records = []

                    #reset Records_byte_size
                    records_byte_size = line_byte_size
                except Exception as e:
                    print(e)
                    print("Error sorting or sending records to CW Logs")


            try:
                # Add Log Event to Records List
                # Log Event Record == dict with key 'timestamp' and 'message'
                # https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_InputLogEvent.html
                input_log_event = {
                    'timestamp': time_in_ms,
                    'message': line
                }
                records.insert(len(records), input_log_event)

            except Exception as e:
                print(e)
                print("error adding Log Record to List")

    put_records_response = put_log(records)
    return(put_records_response)
