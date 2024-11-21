# -*- coding: utf-8 -*-
import traceback
import os

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
    response = requests.post(f"{URL}", data=data, headers=headers)
    if 'access_token' in response.json():
        return response.json()['access_token']

    return None


def GetToken():
    token = os.environ.get('AI_API_TOKEN')
    if token:
        return token

    offline_token = os.environ.get('AI_OFFLINE_TOKEN')
    if offline_token:
        return _get_refresh_token(offline_token)

    return None
