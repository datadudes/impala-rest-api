import json
import os.path

from flask import Flask, request, Response
from impala.error import Error
from mime_utils import request_accepts
from server.query import query_impala
from server.cache import get_redis_conn, set_and_expire


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
    print "Connecting to Impala on {0}:{1}".format(
        application.config['IMPALA_HOST'], application.config['IMPALA_PORT'])
    return application

app = create_app()


def result2csv(records, column_names, include_header):
    if include_header:
        records.insert(0, column_names)
    list_of_str = [','.join(map(str, rec)) for rec in records]
    csv = '\n'.join(list_of_str)
    return csv


def result2json(records, column_names):
    results = []
    for record in records:
        results.append({c: str(record[i]) for (i, c) in enumerate(column_names)})
    return json.dumps(results)


def is_select(sql):
    clean_sql = sql.strip().upper()
    return clean_sql.startswith("SELECT") or clean_sql.startswith("WITH")


def str_is_true(string):
    return string.lower() in ['true', '1', 't', 'y', 'yes']


@app.before_request
def authenticate():
    token = request.args.get('token', '')
    # FIXME: Use Google API authentication instead
    if token != app.config['SECURITY_TOKEN']:
        return "Unauthorized", 401


@app.route("/impala")
def impala():
    sql_query = request.args.get('q', '')
    include_column_names = str_is_true(request.args.get('header', ''))

    # FIXME: Use proper permission setting, e.g. Apache Sentry
    if not is_select(sql_query):
        return "Only SELECT queries are allowed", 403

    redis_conn = get_redis_conn()
    mimetype = request_accepts()
    key = '{}${}'.format(sql_query, mimetype)
    payload = redis_conn.get(key)

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
        else:
            payload = result2json(records, column_names)

        set_and_expire(key, payload)

    return Response(payload, mimetype=mimetype)


@app.errorhandler(Error)
def handle_invalid_usage(error):
    return error.message.replace('AnalysisException: ', ''), 400

