# -*- coding: utf-8 -*-
import traceback

try:
    import requests
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_REQUESTS = True
    REQUESTS_IMPORT_ERROR = None

URL = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"


def _get_refresh_token(offline_token):
    # Set headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    # set data
    data = {
        "grant_type": "refresh_token",
        "client_id": "cloud-services",
        "refresh_token": offline_token,
    }

    # Generate API token
    response = requests.post(f"{URL}", data=data, json=None, headers=headers)
    return response
