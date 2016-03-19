FROM informaticsmatters/rdkit:latest
MAINTAINER Anthony Bradley
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y  python-psycopg2 \
libffi-dev \
python-pip \
python-scipy
# this section is very important to keep a separate layer for the dependencies
RUN mkdir /code/requirements
ADD requirements.txt /code/
ADD requirements/* /code/requirements/
RUN pip install -r requirements.txt

ADD . /code/

# Docker specific config
RUN mv proj/settings/docker.py proj/settings/local.py

# build static assets
RUN SECRET_KEY=temp_value python manage.py collectstatic -v 0 --clear --noinput
