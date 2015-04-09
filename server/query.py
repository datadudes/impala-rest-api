from flask import current_app
from impala.dbapi import connect


def query_impala(sql):
    cursor = query_impala_cursor(sql)
    result = cursor.fetchall()
    field_names = [f[0] for f in cursor.description]
    return result, field_names


def query_impala_cursor(sql, params=None):
    conn = connect(host=current_app.config['IMPALA_HOST'], port=current_app.config['IMPALA_PORT'])
    cursor = conn.cursor()
    cursor.execute(sql.encode('utf-8'), params)
    return cursor
