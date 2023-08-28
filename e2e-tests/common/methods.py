import base64
import json
import os

import requests

from common.constants import (
    ANALYZER_BASE_URL,
)

DEFAULT_HEADERS = {"Content-Type": "application/json"}
MULTIPART_HEADERS = {"Content-Type": "multipart/form-data"}
ANALYZER_BASE_URL = os.environ.get("ANALYZER_BASE_URL", ANALYZER_BASE_URL)


def analyze(data):
    response = requests.post(
        f"{ANALYZER_BASE_URL}/analyze", data=data, headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content


def analyzer_supported_entities(data):
    response = requests.get(
        f"{ANALYZER_BASE_URL}/supportedentities?{data}", headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content


def __get_redact_payload(color_fill):
    payload = {}
    if color_fill:
        payload = {"data": "{'color_fill':'" + str(color_fill) + "'}"}
    return payload


def __get_multipart_form_data(file):
    multipart_form_data = {}
    if file:
        multipart_form_data = {
            "image": (file.name, file, "multipart/form-data"),
        }
    return multipart_form_data
