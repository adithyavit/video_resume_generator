FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y \
	python3-pip python-dev

RUN pip3 install --upgrade pip
	
RUN pip3 install futures
RUN pip3 install google-cloud-pubsub
RUN pip3 install -U pip setuptools wheel
RUN pip3 install -U spacy==2.3.5
RUN pip3 install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz
RUN pip3 install nltk

#RUN python3 -m nltk.downloader all -d /usr/local/nltk_data
RUN python3 -m nltk.downloader -d /usr/local/share/nltk_data all

RUN python3 -c "import nltk;nltk.download('words')"
RUN python3 -c "import nltk;nltk.download('stopwords')"

RUN apt-get install -y ffmpeg
RUN pip install pyresparser

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN pwd
RUN pwd
COPY . /app

RUN export GOOGLE_APPLICATION_CREDENTIALS="/app/genuine-box-305122-82de1537afa0.json"


ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

