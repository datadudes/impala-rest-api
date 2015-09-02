import os.path

from flask import Flask, request, Response
from impala.error import Error
from mime_utils import request_accepts
from server.query import query_impala
from server.cache import RedisCache
from server.serialization import result2csv, result2json
from flask.ext.cors import CORS


def init_config(application):
    application.config.from_object('server.reference_config')
    application.config.from_envvar('IMPALA_API_CONFIG', silent=True)
    application.config['IMPALA_HOST'] = os.environ.get('IMPALA_HOST') if os.environ.get('IMPALA_HOST') else application.config['IMPALA_HOST']
    application.config['IMPALA_PORT'] = os.environ.get('IMPALA_PORT') if os.environ.get('IMPALA_PORT') else application.config['IMPALA_PORT']
    application.config['REDIS_URL'] = os.environ.get('REDIS_URL') if os.environ.get('REDIS_URL') else application.config['REDIS_URL']
    application.config['SECURITY_TOKEN'] = os.environ.get('SECURITY_TOKEN') if os.environ.get('SECURITY_TOKEN') else application.config['SECURITY_TOKEN']


def create_app():
    application = Flask(__name__)
    init_config(application)
    CORS(application)
    print "Connecting to Impala on {0}:{1}".format(
        application.config['IMPALA_HOST'], application.config['IMPALA_PORT'])
    return application

app = create_app()


def is_select(sql):
    clean_sql = sql.strip().upper()
    return clean_sql.startswith("SELECT") or clean_sql.startswith("WITH")


def str_is_true(string):
    return string.lower() in ['true', '1', 't', 'y', 'yes']


@app.before_request
def authenticate():
    token = request.args.get('token', '')
    if token != app.config['SECURITY_TOKEN']:
        return "Unauthorized", 401


@app.route("/impala")
def impala():
    sql_query = request.args.get('q', '')
    include_column_names = str_is_true(request.args.get('header', ''))

    # FIXME: Use proper permission setting, e.g. Apache Sentry
    if not is_select(sql_query):
        return "Only SELECT queries are allowed", 403

    cache = RedisCache(app.config['REDIS_URL'])
    mimetype = request_accepts()
    payload = cache.get(sql_query, mimetype)

    if not payload:
        records, column_names = query_impala(sql_query)

        if len(records) > app.config['MAX_RECORDS_IN_RESPONSE']:
            raise ValueError(
                'Response contains {0} records, max allowed is {1}.'.format(
                    len(records),
                    app.config['MAX_RECORDS_IN_RESPONSE']
                )
            )
        if mimetype == 'text/csv':
            payload = result2csv(records, column_names, include_column_names)
        elif mimetype == 'application/json':
            payload = result2json(records, column_names)
        else:
            return Response("The Impala REST API only supports responses in with mimetype 'text/csv' or 'application/json'", status=406)

        cache.set_and_expire(sql_query, mimetype, payload)

    return Response(payload, mimetype=mimetype)


@app.errorhandler(Error)
def handle_invalid_usage(error):
    return error.message.replace('AnalysisException: ', ''), 400

