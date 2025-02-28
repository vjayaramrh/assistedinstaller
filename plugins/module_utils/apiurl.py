# -*- coding: utf-8 -*-

API_VERSION = "v2"
API_URL = f"https://api.openshift.com/api/assisted-install/{API_VERSION}"


def GetURL(url_path):
    if not url_path.startswith("/"):
        url_path = "/" + url_path
    return API_URL + url_path
