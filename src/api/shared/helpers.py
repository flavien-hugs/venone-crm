from functools import wraps

from flask import jsonify, make_response


def jsonify_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = make_response(jsonify(func(*args, **kwargs)))
        response.headers["Content-Type"] = "application/json"
        return response

    return wrapper
