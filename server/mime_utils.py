from flask import request


def request_accepts():
    return request.accept_mimetypes.best_match(['application/json', 'text/csv'])

