#!/usr/bin/env python3
import os
import sys
import json
import requests
import backoff
from pprint import pprint
import click
import urllib3

urllib3.disable_warnings()

exceptions = (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.ProxyError, KeyError)

@backoff.on_exception(backoff.expo, exceptions, max_time=os.environ.get('SONAR_POLLER_TIMEOUT', 300))
def poll_sonar(url, project, auth=None):
    """Polling function with exponential backoff, retries on any exception"""

    print(".", end="")  # progress bar
    r = requests.get('{url}/api/qualitygates/project_status?projectKey={project}'.format(url=url, project=project), auth=auth, verify=False)
    r.raise_for_status()
    status = r.json()['projectStatus']['status']
    print("")
    return status


@backoff.on_predicate(backoff.expo, max_time=os.environ.get('SONAR_POLLER_TIMEOUT', 300))  # continue polling if no exception is raised but report is still not ready
@backoff.on_exception(backoff.expo, exceptions, max_time=os.environ.get('SONAR_POLLER_TIMEOUT', 300))
def poll_task(auth=None):
    """Polls the task URL to ensure that this particular commit has been analysed"""

    print(".", end="")  # progress bar
    file_contents = open('target/sonar/report-task.txt', 'r').readlines()
    task_url = [x for x in file_contents if x.startswith('ceTaskUrl')][0].split('=', 1)[1]  # extract value from plaintext key=value file
    r = requests.get(task_url, auth=auth, verify=False)
    r.raise_for_status()
    status = r.json()['task']['status']
    if not status == "SUCCESS":
        return False
    else:
        print("")
        return True


@click.command()
@click.option('--url', envvar='SONAR_POLLER_URL', prompt=True, required=True, help="Full URL to your Sonarqube instance, including any context path. e.g. https://sonarqube.example.com")
@click.option('--project', envvar='SONAR_POLLER_PROJECT', prompt=True, required=True, help="Project name as specified on the dashboard, e.g. com.example:myapp")
@click.option('--username', envvar='SONAR_POLLER_USERNAME', required=False, help="Username for authentication, optional")
@click.option('--password', envvar='SONAR_POLLER_PASSWORD', hide_input=True, required=False, help="Password for authentication, optional")
def check_sonar(url, project, username=None, password=None):
    """Poll Sonarqube API until analysis is finished, exit non-0 if the Quality Gate result is ERROR or timeout (SONAR_POLLER_TIMEOUT) is reached"""

    url = url.rstrip("/")  # fix duplicate trailing slashes

    # credentials are optional
    if username or password:
        auth = (username, password)
    else:
        auth = None

    print('Polling analysis status...', end="")
    poll_task()

    print('Polling Sonarqube for results...', end="")
    status = poll_sonar(url=url, project=project, auth=auth)

    print("Sonarqube Quality Gate is {status}, results: {url}/dashboard/index/{project}".format(status=status, url=url, project=project))
    if status == "OK":
        exit(0)
    else:
        exit(1)

if __name__ == '__main__':
    check_sonar()
