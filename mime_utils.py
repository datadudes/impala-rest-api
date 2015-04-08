from flask import request


def request_accepts(mimetype):
    best = request.accept_mimetypes.best_match([mimetype, 'text/html'])
    return best == mimetype and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


def request_accepts_json():
    return request_accepts('application/json')


def request_accepts_csv():
    return request_accepts('text/csv')
