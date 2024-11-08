#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os
import requests


__metaclass__ = type

DOCUMENTATION = r"""
---
module: events

short_description: Handle AssistedInstall cluster events

version_added: "1.0.0"

description: Interact with cluster events through the AssistedInstall API

options:
    action:
      description: The action to perform
      required: false
      default: "list"
    cluster_id:
        description: The cluster ID to perform the action on
        required: false
    limit:
        description: The maximum number of records/events to retrieve
        default: 10
        required: false
        type: integer

author:
    - Akash Gopalakrishnan (@agopalak)
"""

EXAMPLES = r"""
# Use argument
- name: List cluster events
  events
    action: list
    cluster_id: "deadmeat-dead-meat-dead-meatdeadmeat"
    limit: 50
"""

RETURN = r"""
cluster_events:
    description: A list of cluster events
    type: dict
    returned: always
    sample: [
            {
                "cluster_id": "46f3094d-8967-4f1d-ad09-d5fdfda3830a",
                "event_time": "2024-11-08T20:15:44.447Z",
                "message": "Successfully registered cluster",
                "name": "cluster_registration_succeeded",
                "severity": "info"
            },
            {
                "cluster_id": "46f3094d-8967-4f1d-ad09-d5fdfda3830a",
                "event_time": "2024-11-08T20:15:44.652Z",
                "infra_env_id": "33f1638b-0419-4bc9-ac20-4baddcf14a30",
                "message": "Updated image information (Image type is \"minimal-iso\", SSH public key is not set)",
                "name": "image_info_updated",
                "severity": "info"
            },
            {
                "cluster_id": "46f3094d-8967-4f1d-ad09-d5fdfda3830a",
                "event_time": "2024-11-08T20:15:52.436Z",
                "message": "Updated status of the cluster to pending-for-input",
                "name": "cluster_status_updated",
                "severity": "info"
            }
        ]
"""

from ansible.module_utils.basic import AnsibleModule

API_VERSION = "v2"
API_URL = f"https://api.openshift.com/api/assisted-install/{API_VERSION}"

# add additional query parameters to the query_params_list
QUERY_PARAMS_LIST = ["limit"]

def run_module():
    module_args = dict(
        action=dict(type="str", required=False, default="list"),
        cluster_id=dict(type="str", required=False),
        # any API query parameters may have to be added here
        limit=dict(type="int", required=False, default=10),
    )

    token = os.environ.get('AI_API_TOKEN')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # List cluster events
    if module.params.get('action') == "list":
        list_params = {}
        for k in QUERY_PARAMS_LIST:
            val = module.params.get(k)
            if val:
                list_params = list_params | { k: val }

        response = requests.get(f"{API_URL}/events?cluster_id={module.params.get('cluster_id')}", params=list_params, headers=headers)

        if not response.ok:
            result = dict(changed=True, response=response.text)
            module.fail_json(msg="Error listing cluster events", **result)

        result = dict(changed=False,cluster_events=response.json())

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
