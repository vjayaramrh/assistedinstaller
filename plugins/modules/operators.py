#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
---
module: operators

short_description: Information regarding supported operators

version_added: "1.0.0"

description: Assisted Service API to retrieve supported operators

author:
    - Tony García (@tonyskapunk)
"""

EXAMPLES = r"""
# Use argument
- name: List supported operators
  operators:
"""

RETURN = r"""
operators:
    description: List of supported operators
    type: list
    returned: always
    sample: ["lso", "odf", "cnv", "lvm", "mce"]
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

try:
    from ansible_collections.openshift_lab.assisted_installer.plugins.module_utils import apitoken
except ImportError:
    from ansible.module_utils import apitoken

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
    module_args = dict()
    token = apitoken.GetToken()
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Fail if requests is not installed
    if not HAS_REQUESTS:
        module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # List supported operators
    response = requests.get(f"{API_URL}/supported-operators", headers=headers)

    if not response.ok:
        try:
            res = response.json()
        except requests.JSONDecodeError:
            res = response.text

        result = dict(changed=False, response=res, operators=[])
        module.fail_json(msg="Error listing supported operators", **result)

    result = dict(changed=False, operators=response.json())

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
