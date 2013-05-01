from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from doc_insert_working import *
import time


# setup Simple Queue Service
SQSconn = SQSConnection('SQS_Key', 'SQS_PASSWORD')
q = SQSconn.create_queue('nlp_corpus_queue')

# setup S3
s3conn = S3Connection('S3_Key', 'S3_PASSWORD')
bucket = s3conn.get_bucket('S3_BUCKET')
s3Data = Key(bucket)

#initialize a new NLP helper
nlp = nltkHelper()

while(True): # create the never ending loop...
	try:
		rs = q.get_messages(visibility_timeout=60*60*12) # gets one message by default - also set the visibility_timeout (in seconds) - so hours here...
	except:
		continue
	
	if(len(rs) > 0): # check to make sure that there actually is a message to process
		m = rs[0]
		s3Data.key = m.get_body()
		if nlp.insertRaw(s3Data.key):
			q.delete_message(m)	
	
	else:
		pass
	time.sleep(1)