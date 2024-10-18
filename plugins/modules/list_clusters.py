#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os
import requests


__metaclass__ = type

DOCUMENTATION = r"""
---
module: list_clusters

short_description: lists ocp clusters

version_added: "1.0.0"

description: Given the API token, returns list of clusters in the account

options:
    fail:
        description: Trigger a failure
        default: false
        type: bool

author:
    - Name (@vjayaramrh)
"""

EXAMPLES = r"""
# Use argument
- name: Trigger a failure
  list_clusters
    fail: true
"""

RETURN = r"""
list_clusters_msg:
    description: A message with the status
    type: str
    returned: always
    sample: "Success!"
"""

from ansible.module_utils.basic import AnsibleModule

BASE_URL = "https://api.openshift.com/api/assisted-install/v2/clusters"

def run_module():
    module_args = dict(
        fail=dict(type="bool", required=False, default=False),
    )
    token = os.environ.get('AI_API_TOKEN')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    response = requests.get( BASE_URL, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'} )

    if not response.ok:
        result = dict(changed=True, list_clusters_msg=response.text)
        module.fail_json(msg=f"Error triggered by fail={module.params.get('fail')}", **result)

    resp_json = response.json()

    result = dict(changed=True, list_clusters_msg=resp_json)

    result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
