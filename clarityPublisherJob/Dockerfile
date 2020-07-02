FROM python:3.6

COPY clarityPublisherJob/ /task/
COPY keyscredentials/*.json /google-keys/

WORKDIR /task/
RUN pip install -r requirements.txt
RUN python setup.py install
