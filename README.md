# docker-sonar-poller

This is a CLI tool that polls the Sonarqube APIs for a given project until analysis is finished. It will exit non-0 (and break the build) if the Quality Gate result is ERROR or timeout (`SONAR_POLLER_TIMEOUT`) is reached

## Usage

```
Usage: sonar-poller.py [OPTIONS]

  Poll Sonarqube API until analysis is finished, exit non-0 if the Quality
  Gate result is ERROR or timeout (SONAR_POLLER_TIMEOUT) is reached

Options:
  --url TEXT       Full URL to your Sonarqube instance, including any context
                   path. e.g. https://sonarqube.example.com  [required]
  --project TEXT   Project name as specified on the dashboard, e.g.
                   com.example:myapp  [required]
  --username TEXT  Username for authentication, optional
  --password TEXT  Password for authentication, optional
  --help           Show this message and exit.
```

The tool also accepts environment variables with the prefix `SONAR_POLLER_*` e.g. `SONAR_POLLER_URL`.

## Docker Image

This tool is available as a Docker image: `aarongorka/sonar-poller:latest`

docker-compose.yml:
```yml
version: '3.7'
services:
  sonar-poller:
    image: aarongorka/sonar-poller:latest
    env_file: .env
    volumes:
      - .:/srv/app:Z
    working_dir: /srv/app
```

Update your `.env` file with the following:

```
SONAR_POLLER_URL
SONAR_POLLER_PROJECT
SONAR_POLLER_USERNAME
SONAR_POLLER_PASSWORD
SONAR_POLLER_TIMEOUT
```

Then it can be called as such:

```bash
docker-compose run --rm sonar-poller
```
