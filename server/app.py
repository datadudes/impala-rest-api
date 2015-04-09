import json
import os.path

from flask import Flask, request, Response
from impala.error import Error
from mime_utils import request_accepts_csv
from server.query import query_impala


def init_config(application):
    application.config.from_object('server.reference_config')
    application.config.from_envvar('IMPALA_API_CONFIG', silent=True)
    application.config['IMPALA_HOST'] = os.environ.get('IMPALA_HOST', application.config['IMPALA_HOST'])
    application.config['IMPALA_PORT'] = os.environ.get('IMPALA_PORT', application.config['IMPALA_PORT'])
    application.config['SECURITY_TOKEN'] = os.environ.get('SECURITY_TOKEN', application.config['SECURITY_TOKEN'])


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
    return sql.strip().upper().startswith("SELECT")


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

    records, column_names = query_impala(sql_query)

    if len(records) > app.config['MAX_RECORDS_IN_RESPONSE']:
        raise ValueError(
            'Response contains {0} records, max allowed is {1}.'.format(
                len(records),
                app.config['MAX_RECORDS_IN_RESPONSE']
            )
        )

    if request_accepts_csv():
        csv = result2csv(records, column_names, include_column_names)
        return Response(csv, mimetype='text/csv')
    else:
        j = result2json(records, column_names)
        return Response(j, mimetype='application/json')


@app.errorhandler(Error)
@app.errorhandler(Exception)
def handle_invalid_usage(error):
    return error.message.replace('AnalysisException: ', ''), 400

