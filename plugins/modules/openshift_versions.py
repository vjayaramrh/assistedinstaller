#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: openshift_versions

short_description: Query supported OpenShift versions

version_added: "1.0.0"

description: Retrieves the list of supported OpenShift versions.


options:
  version:
    description: Version of OpenShift
    required: False
    type: str

  only_latest:
    description: Retrieve only latest minor version
    required: False
    default: False
    type: bool

author:
    - Michele Costa  (@nocturnalstro)
"""

EXAMPLES = r"""
- name: Query OpenShift architectures
  openshift_versions:
    version: 4.18
    only_latest: true
"""

RETURN = r"""
versions:
  description: A collection of supported OpenShift versions
  type: dict
  returned: always
  sample: {
    "4.18.1": {
        "cpu_architectures": [
            "ppc64le",
            "x86_64",
            "arm64",
            "s390x"
        ],
        "default": true,
        "display_name": "4.18.1",
        "support_level": "production"
    },
    "4.18.1-multi": {
        "cpu_architectures": [
            "x86_64",
            "arm64",
            "s390x",
            "ppc64le"
        ],
        "display_name": "4.18.1-multi",
        "support_level": "production"
    }
  }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

import traceback

try:
    from ansible_collections.openshift_lab.assisted_installer.plugins.module_utils import apitoken, apiurl
except ImportError:
    from ansible.module_utils import apitoken, apiurl

try:
    import requests
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_REQUESTS = True
    REQUESTS_IMPORT_ERROR = None

QUERY_PARAMS_LIST = [
    "version",
    "only_latest",
]


def run_module():
    module_args = dict(
        version=dict(type="str", required=False),
        only_latest=dict(type="bool", required=False, default=False)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Fail if requests is not installed
    if not HAS_REQUESTS:
        module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {apitoken.GetToken()}'
    }

    query_params = {}

    for k in QUERY_PARAMS_LIST:
        val = module.params.get(k)
        if val:
            query_params = query_params | {k: val}

    response = requests.get(
        apiurl.GetURL("/openshift-versions"),
        params=query_params,
        headers=headers,
    )

    if not response.ok:
        result = dict(changed=True, response=response.text)
        module.fail_json(msg="Error querying openshift versions", **result)

    module.exit_json(versions=response.json())


def main():
    run_module()


if __name__ == "__main__":
    main()
