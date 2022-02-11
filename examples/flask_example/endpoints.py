from http import HTTPStatus
from flask import jsonify


def get_index():
    return jsonify({}), HTTPStatus.NO_CONTENT


def get_welcome():
    return jsonify({"welcome": "user"}), HTTPStatus.OK
