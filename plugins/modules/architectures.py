#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: architectures

short_description: Query OpenShift architectures

version_added: "1.0.0"

description: Query supported architectures for a given OpenShift version

options:
  openshift_version:
    description: Version of OpenShift
    required: True
    type: str

author:
    - Chris Wheeler (@clwheel)
"""

EXAMPLES = r"""
- name: Query OpenShift architectures
  architectures:
    openshift_version: 4.16.19
"""

RETURN = r"""
architectures:
  description: A list of supported OpenShift architectures
  type: dict
  returned: always
  sample: { "ARM64_ARCHITECTURE": "supported",
            "MULTIARCH_RELEASE_IMAGE": "tech-preview",
            "PPC64LE_ARCHITECTURE": "supported",
            "S390X_ARCHITECTURE": "supported",
            "X86_64_ARCHITECTURE": "supported" }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

import os
import traceback

try:
    import requests
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_REQUESTS = True
    REQUESTS_IMPORT_ERROR = None

API_VERSION = "v2"
API_URL = f"https://api.openshift.com/api/assisted-install/{API_VERSION}"
QUERY_PARAMS_LIST = ["openshift_version"]


def run_module():
    module_args = dict(
        openshift_version=dict(type="str", required=True),
    )

    token = os.environ.get('AI_API_TOKEN')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Fail if requests is not installed
    if not HAS_REQUESTS:
      module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    query_params = {}

    for k in QUERY_PARAMS_LIST:
        val = module.params.get(k)
        if val:
            query_params = query_params | {k: val}

    response = requests.get(f"{API_URL}/support-levels/architectures", params=query_params, headers=headers)

    if not response.ok:
        result = dict(changed=True, response=response.text)
        module.fail_json(msg="Error querying architectures", **result)

    result = response.json()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
