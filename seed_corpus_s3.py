from boto.s3.connection import S3Connection
from boto.s3.key import Key
import uuid


f = open('YOUR_FILE.txt')
raw = f.read()

# Now that we have the file read in - we need to move it to Amazon S3

s3conn = S3Connection('S3_KEY_ID', 'S3_SECRET_KEY')
bucket = s3conn.get_bucket('S3_BUCKET')

k = Key(bucket)
k.key = uuid.uuid4() # create a unique key from Python uuid library

k.set_contents_from_string(raw)

# Now that the file has been uploaded to S3 - they key needs to be placed in the amazon Queue service
# so the worker nodes can process it when they are available

from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

SQSconn = SQSConnection('SQS_KEY_ID', 'SQS_SECRET_KEY')
q = SQSconn.create_queue('SQS_QUEUE')

m = Message() # create a new message object
m.set_body(str(k.key)) # set the body of the message to be the key for the amazon s3 resource

status = q.write(m)