FROM python:3.7.3
MAINTAINER Computer Science House Drink Admins <drink@csh.rit.edu>

RUN apt-get update && \
    apt-get install -y libldap-dev libsasl2-dev && \
    apt-get autoremove --yes && \
    apt-get clean autoclean 

WORKDIR /opt/mizu
ADD . /opt/mizu

RUN pip install \
    --no-warn-script-location \ 
    --no-cache-dir \
    pipenv

RUN pipenv install --system

CMD python wsgi.py

