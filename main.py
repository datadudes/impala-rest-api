import json
import os.path

from flask import Flask, request, Response
from impala.dbapi import connect
from impala.error import Error
from mime_utils import request_accepts_csv


app = Flask(__name__)
config = app.config


def query_impala(sql):
    cursor = query_impala_cursor(sql)
    result = cursor.fetchall()
    field_names = [f[0] for f in cursor.description]
    return result, field_names


def query_impala_cursor(sql, params=None):
    conn = connect(host=config['IMPALA_HOST'], port=config['IMPALA_PORT'])
    cursor = conn.cursor()
    cursor.execute(sql.encode('utf-8'), params)
    return cursor


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
    if token != config['SECURITY_TOKEN']:
        return "Unauthorized", 401


@app.route("/impala")
def impala():
    sql_query = request.args.get('q', '')
    include_column_names = str_is_true(request.args.get('header', ''))

    # FIXME: Use proper permission setting, e.g. Apache Sentry
    if not is_select(sql_query):
        return "Only SELECT queries are allowed", 403

    records, column_names = query_impala(sql_query)

    if len(records) > config['MAX_RECORDS_IN_RESPONSE']:
        raise ValueError(
            'Response contains {0} records, max allowed is {1}.'
                .format(len(records), config['MAX_RECORDS_IN_RESPONSE']))

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


def load_config_if_exists(fname):
    if os.path.isfile(fname):
        app.config.from_pyfile(fname)
    else:
        print "Config file {0} does not exist, skipping".format(fname)


if __name__ == "__main__":
    load_config_if_exists('reference.cfg')
    load_config_if_exists('application.cfg')

    print "Connecting to Impala on {0}:{1}".format(
        config['IMPALA_HOST'], config['IMPALA_PORT'])

    app.run(
        host=config['HOST'],
        port=config['PORT'],
        debug=config['DEBUG_MODE'])
