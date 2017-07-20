import simplejson, boto, uuid
sqs = boto.connect_sqs()

q = sqs.create_queue('my_message_pump')
data = simplejson.dumps('python main.py')

s3 = boto.connect_s3()
bucket = s3.get_bucket('message_pump')

key = bucket.new_key('%s.json' % str(uuid.uuid4())
key.set_contents_from_string(data)

message = q.new_message(body=simplejson.dumps({'bucket': bucket.name, 'key': key.name}))
q.write(message)