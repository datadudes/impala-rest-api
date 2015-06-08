#  Impala REST API

This is a thin REST API for Cloudera Impala, written in Python. It provides a simple endpoint to send queries to, 
returning the results either in CSV format or as JSON. It also caches the results for later usage. Currently the whole 
cache is expired at 9 o'clock in the morning.

Impala REST API was built using [Flask](http://flask.pocoo.org/) and [Impyla](https://github.com/cloudera/impyla).

## Example usage

Assume the server is running on `impala-api.example.com`.

Retrieve top 10 customers in CSV format, including the table header in CSV:

```
$ curl -G 'http://impala-api.example.com/impala?header=true&token=12345' \
  --data-urlencode 'q=select * from customers limit 5' \
  --header 'Accept: text/csv'

name,city,age  
Peter,Dublin,55
Daan,Harlem,34
Jan,Amsterdam,15
Adam,Zurich,22
Marcel,Amsterdam,89
```

## Installation

The easiest way to get run the Impala REST API is by using the published 
[Docker images](https://registry.hub.docker.com/u/datadudes/impala-rest-api/). Impala REST API needs a Redis instance 
for caching results, which can also conveniently be run inside a Docker container. To get up and running, do the 
following:

```bash
$ docker run --name impala-api-redis -d redis # start a Redis container
$ docker run -e IMPALA_HOST=<ip-or-host-of-impala> \
    -e SECURITY_TOKEN=<choose-a-random-token> \
    -p <desired-port-on-docker-host>:5000 \
    --name impala-api --link impala-api-redis:redis \
    -d datadudes/impala-rest-api:latest # start Impala REST API and link it to your Redis instance
```

That's all!

#### Building a Docker image of the latest version

To build a Docker image of the latest version of Impala REST API, run the following command:

```bash
$ docker build -t "impala-rest-api:latest" .
```

You can give it any name you want. Use that samen name when running the container.

#### Running without Docker

To run Impala REST API without Docker, you should make sure there is a Redis instance running and reachable by 
Impala REST API. You can then run the application using the built-in Flask server (not recommended for production use) 
with `python wsgy.py`. The better option is to use any WSGI-compliant server, such as [Gunicorn](http://gunicorn.org/), 
and pass it the `wsgi:app` object. See the Dockerfile for an example using Gunicorn.

## Configuration

Impala REST API requires some configuration to get going. Everything can be configured using environment variables. 
If you're using Docker as in the aforementioned example, you only need to set the following environment variables: 
`IMPALA_HOST` pointing to a host where an Impala daemon is running, and `SECURITY_TOKEN` that secures the API endpoint.

If you run Impala REST API without Docker, or you have Redis running on another host, you also have to provide the 
`REDIS_URL` variable. See the _reference_config.py` in the `server` package for examples and default values for all 
configuration options.

Lastly, you can also copy the `reference_config.py` and change it to your liking, and then point to it by setting the 
`IMPALA_API_CONFIG` variable.

## Development

If you want to hack on Impala REST API, this is easy to do with [Docker Compose](https://docs.docker.com/compose/). 
Install Docker Compose and run

```bash
$ docker-compose up
```

Docker Compose will setup a local environment for you using Docker containers, and will link the source code to the 
container. Because of Flask's hot-restart ability, you can hack away at the code and immediately see the results!

Before you run the app, make sure to have at least the `IMPALA_HOST` and `SECURITY_TOKEN` set in your environment.

### Contributions:

Please create an issue if you spot any problem or bug.
We'll try to get back to you as soon as possible.

### Authors:

Created with passion by [Marcel](https://github.com/mkrcah)
and [Daan](https://github.com/DandyDev).
