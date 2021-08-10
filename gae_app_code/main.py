# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]



# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
import logging
from flask import Flask
from google.cloud import pubsub_v1
from flask import Flask, render_template, request, redirect, url_for
import json
import os 
from time import sleep
from google.cloud import storage


app = Flask(__name__)

# print(os.environ)
app.config['PUBSUB_VERIFICATION_TOKEN'] = 'adithya2021' #os.environ['PUBSUB_VERIFICATION_TOKEN']
app.config['PUBSUB_TOPIC'] = 'resumesqueue' #os.environ['PUBSUB_TOPIC']
app.config['GOOGLE_CLOUD_PROJECT'] = os.environ['GOOGLE_CLOUD_PROJECT']

from google.cloud import storage

def list_files(bucketName):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket("activestorage-adithya-outputs")
    """List all files in GCP bucket."""
    files = bucket.list_blobs()
    fileList = ["https://storage.googleapis.com/activestorage-adithya-outputs/"+file.name for file in files if '.' in file.name]
    return fileList

@app.route('/',methods=['GET'])
def ans_index():
    ans = list_files("activestorage-adithya-outputs")


    # ans = ["https://www.youtube.com/embed/wgqaoAS8lcg"]
  	
    return render_template('index.html', ans = ans)
@app.route('/', methods=['POST'])
def upload_file():
    bucket_name = "activestorage-adithya"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    publisher = pubsub_v1.PublisherClient()
    print("hi")
    for source_file in request.files.getlist('file'):
        print(source_file)
        if source_file.filename != '':
            destination_blob_name  = source_file.filename
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_file(source_file)
            topic_path = publisher.topic_path(app.config['GOOGLE_CLOUD_PROJECT'],app.config['PUBSUB_TOPIC'])
            print(topic_path)
            # publisher.publish(topic_path, data=source_file.filename.encode('utf-8'))
            publisher.publish("projects/genuine-box-305122/topics/resumesqueue", data=source_file.filename.encode('utf-8'))
            

            print(
                "File {} uploaded to {}.".format(
                    source_file.filename, destination_blob_name
                )
            )

            print(type(source_file.filename))
    return redirect(url_for('ans_index'))
  
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

 
def upload_blob(bucket_name, source_file, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_file(source_file)

    print(
        "File {} uploaded to {}.".format(
            source_file.filename, destination_blob_name
        )
    )



if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_quickstart]
