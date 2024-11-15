#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: register_cluster

short_description: Register AssistedInstaller cluster

version_added: "1.0.0"

description: Register an AssistedInstaller Cluster

options:
    data:
        description: JSON data for AssistedInstaller
        type: dict
        required: true
    ## Note: AI_API_TOKEN and AI_PULL_SECRET env variables must be set

author:
    - Daniel Kostecki (@dkosteck)
"""

EXAMPLES = r"""
# Use argument
- name: Register cluster
  register_cluster
    data: {
        'name': 'testcluster',
        'openshift_version': '4.16',
    }
"""

RETURN = r"""
register_clusters:
    description: A dict with the AssistedInstaller results
    type: dict
    returned: always
"""

import os
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

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


def run_module():
    module_args = dict(
        data=dict(type="dict", required=True),
    )
    token = os.environ.get('AI_API_TOKEN')
    pull_secret = os.environ.get('AI_PULL_SECRET')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Fail if requests is not installed
    if not HAS_REQUESTS:
        module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    data = module.params.get('data')
    data['pull_secret'] = pull_secret

    response = requests.post(f"{API_URL}/clusters", headers=headers, json=data)

    if not response.ok:
        result = dict(changed=True, response=response.text)
        module.fail_json(msg="Error registering cluster", **result)

    result = dict(clusters=response.json())

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
