#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os
import requests


__metaclass__ = type

DOCUMENTATION = r"""
---
module: operators

short_description: Information regarding supported operators

version_added: "1.0.0"

description: Assisted Service API to retrieve supported operators

options:

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
    sample: []
"""

from ansible.module_utils.basic import AnsibleModule

API_VERSION = "v2"
API_URL = f"https://api.openshift.com/api/assisted-install/{API_VERSION}"

def run_module():
    module_args = dict(
        name=dict(type="str", required=False),
    )
    token = os.environ.get('AI_API_TOKEN')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

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
