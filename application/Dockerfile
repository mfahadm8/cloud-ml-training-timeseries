FROM nvidia/cuda:11.0.3-base-ubuntu20.04

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install python3-pip -y
COPY . .

RUN pip3 install -r requirements.txt

COPY training.py .
RUN mkdir data

HEALTHCHECK NONE

CMD ["python3", "-u", "training.py"]