FROM python:3-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /srv/app
RUN apk add --no-cache openssl-dev libffi-dev build-base
COPY requirements.txt /srv/app/requirements.txt
RUN pip3 install -r requirements.txt
COPY /sonar-poller /sonar-poller
CMD ["python3", "/sonar-poller/sonar-poller.py"]
