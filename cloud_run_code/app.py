from flask import Flask
app = Flask(__name__)
import os
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from google.cloud import storage
from google.api_core import retry
import gc
# pip3 install google-cloud-pubsub
# pip3 install -U pip setuptools wheel
# pip3 install -U spacy==2.3.5
# pip3 install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz
# python3 -m nltk.downloader words
# python3 -m nltk.downloader stopwords
# sudo snap install ffmpeg

from pyresparser import ResumeParser
import subprocess

app.config['PUBSUB_VERIFICATION_TOKEN'] = 'adithya2021' #os.environ['PUBSUB_VERIFICATION_TOKEN']
app.config['PUBSUB_TOPIC'] = 'resumesqueue' #os.environ['PUBSUB_TOPIC']
app.config['GOOGLE_CLOUD_PROJECT'] = 'genuine-box-305122'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "genuine-box-305122-4aae0c84886f.json"


filename_global = ""

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


def callback(message):
    print(f"Received {message.data}.")
    global filename_global 
    filename_global = message.data
    if message.attributes:
        print("Attributes:")
        for key in message.attributes:
            value = message.attributes.get(key)
            print(f"{key}: {value}")
    message.ack()
    download_blob("activestorage-adithya", message.data, message.data)
    print("downloading completed")


@app.route('/',methods = ['POST'])
def hello_world():
		# print(os.environ)
	
	print("hi")
	project_id = "genuine-box-305122"
	subscription_id = "resumesqueue-sub"
	timeout = 60.0
	
	subscriber = pubsub_v1.SubscriberClient()
	subscription_path = subscriber.subscription_path(project_id, subscription_id)

	NUM_MESSAGES = 1
	# streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
	with subscriber:
		# The subscriber pulls a specific number of messages. The actual
		# number of messages pulled may be smaller than max_messages.
		response = subscriber.pull(
			request={"subscription": subscription_path, "max_messages": NUM_MESSAGES},
			retry=retry.Retry(deadline=300),
		)

		ack_ids = []
		for received_message in response.received_messages:
			print(f"Received: {received_message.message.data}.")
			ack_ids.append(received_message.ack_id)
			download_blob("activestorage-adithya", received_message.message.data, received_message.message.data)
			global filename_global 
			filename_global = received_message.message.data
			print("downloading complete")



		print(
			f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}."
		)

		# with subscriber:
		#     try:
		#         # When `timeout` is not set, result() will block indefinitely,
		#         # unless an exception is encountered first.
		#         streaming_pull_future.result(timeout=timeout)
		#     except TimeoutError:
		#         streaming_pull_future.cancel()
		
		# filename = "hi0"
		# print(filename)
		# filename = 'The Madison - Sample (Download-Only).docx'
		filename = filename_global.decode("utf-8") 
		print("the above is filename")
		#filename = 'adithya_2021.docx'
		print(filename)
		data = ResumeParser(filename).get_extracted_data()
		print(data)
		applicant_name = data["name"]
		# print(applicant_name)
		skillset = '\n'.join([i for i in data["skills"]])
		# print(skillset)
		degreeset = '\n'.join([i for i in data["degree"]])
		# print(degreeset)
		designationset = '\n'.join([i for i in data["designation"]])
		universityset = data["email"]


		
		
		p = subprocess.Popen('ls', stderr=subprocess.PIPE, stdin=subprocess.PIPE, 
		stdout=subprocess.PIPE)

		output, _ = p.communicate()

		print("break1")
		print(_)

		print("break2")
		print(output)

		# command = ["ffmpeg", "-f", "lavfi", "-i", "color=size=1280x720:duration=10:rate=25:color=blue", "-vf", "drawtext=fontfile=/path/to/font.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='Stack Overflow'", "output.mp4"]
		command_name = "ffmpeg -y -f lavfi -i color=size=1280x720:duration=3:rate=25:color=#FF9AA2 -vf \"drawtext=fontfile=/path/to/font.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='"+applicant_name+"'\" name.mp4"
		command_skills = "ffmpeg -y -f lavfi -i color=size=1280x720:duration=6:rate=25:color=#FFB7B2 -vf \"drawtext=fontfile=/path/to/font.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='"+ skillset+"'\" skills.mp4"
		command_degrees = "ffmpeg -y -f lavfi -i color=size=1280x720:duration=3:rate=25:color=#FFDAC1 -vf \"drawtext=fontfile=/path/to/font.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='"+degreeset+"'\" degree.mp4"
		command_worked = "ffmpeg -f lavfi -y -i color=size=1280x720:duration=3:rate=25:color=#E2F0CB -vf \"drawtext=fontfile=/path/to/font.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='"+designationset+"'\" designation.mp4"
		command_universities = "ffmpeg -f lavfi -y -i color=size=1280x720:duration=3:rate=25:color=#B5EAD7 -vf \"drawtext=fontfile=/path/to/font.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='"+universityset+"'\" universities.mp4"
		
		print("hi1")
		# name
		# skills
		# achievements
		# studied at: college name
		# worked as, at: designation, company
		# experience

		data = ['name.mp4', 'skills.mp4', 'degree.mp4', 'designation.mp4', 'universities.mp4']
		print("hi2")
		with open("mylist.txt", "w") as txt_file:
			for line in data:
				txt_file.write("file "+line + "\n")
		print("hi3")

		combine_command = "ffmpeg -y -f concat -safe 0 -i mylist.txt -c copy no_audio.mp4"
		print("hi3")
		add_audio_command = "ffmpeg -i no_audio.mp4 -i audio.mp3 -map 0 -map 1:a -c:v copy -shortest output.mp4"
		p=subprocess.check_call(command_name, shell=True)
		p=subprocess.check_call(command_skills, shell=True)
		p=subprocess.check_call(command_degrees, shell=True)
		p=subprocess.check_call(command_worked, shell=True)
		p=subprocess.check_call(command_universities, shell=True)
		p=subprocess.check_call(combine_command, shell=True)
		# p=subprocess.check_call(add_audio_command, shell=True)

		print("hi4")
		upload_blob("activestorage-adithya-outputs", "no_audio.mp4", filename+"_output"+".mp4")
		# Acknowledges the received messages so they will not be sent again.
		subscriber.acknowledge(
			request={"subscription": subscription_path, "ack_ids": ack_ids}
			)
		gc.collect()
	return 'Hey, we have Flask in a Docker container!'

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
      app.run(threaded=True, host='0.0.0.0', port=port)

# if __name__ == '__main__':
	# app.run(debug=True, host='0.0.0.0')








