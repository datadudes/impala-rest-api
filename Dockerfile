# start with a base image
FROM ubuntu:14.10

# install dependencies
RUN apt-get -y update
RUN apt-get install -y python python-dev python-pip

# add requirements.txt and install
COPY requirements.txt /code/requirements.txt
COPY *.cfg /code/
COPY *.py /code/
RUN pip install -r /code/requirements.txt

WORKDIR /code/

# Run that shit
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8000"]