#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: events

short_description: Handle AssistedInstall cluster events

version_added: "1.0.0"

description: Interact with cluster events through the AssistedInstall API

options:
    action:
        description: The action to perform.
        required: false
        default: "list"
    cluster_id:
        description: The cluster ID to perform the action on.
        type: string
    limit:
        description: The maximum number of records/events to retrieve.
        required: false
        type: integer
    order:
        description: Retrieval order for cluster events based on time of events.
        default: ascending
        required: false
        type: string
        choices: [ ascending, descending ]
    offset:
        description: Number of events to skip before events retrieval.
        required: false
        type: integer
        default: 0
    severities:
        description: Retrieve events mapped to the severity value.
        required: false
        type: array
        items:
            type: string
        choices: [ info, warning, error, critical ]

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
    order: descending
    offset: 10
    severities: critical, info
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

# add additional query parameters to the query_params_list
QUERY_PARAMS_LIST = ["cluster_id","limit", "order", "offset", "severities"]

def run_module():
    module_args = dict(
        action=dict(type="str", required=False, default="list"),
        cluster_id=dict(type="str", required=False),
        # any API query parameters may have to be added here
        limit=dict(type="int", required=False, default=10),
        offset=dict(type="int", required=False, default=0),        
        order=dict(type="str",required=False, default="ascending", choices=["ascending", "descending"]),
        severities=dict(type="list",required=False, choices=["info", "warning", "error", "critical"]),
    )

    token = os.environ.get('AI_API_TOKEN')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Fail if requests is not installed
    module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # List cluster events
    if module.params.get('action') == "list":
        if not module.params.get('cluster_id'):
            module.fail_json(msg="cluster_id is required for list cluster events action")
        
        list_params = {}
        for k in QUERY_PARAMS_LIST:
            val = module.params.get(k)
            if val:
                if isinstance(val, list):
                    list_params = list_params | {k: ",".join(val)}
                else:
                    list_params = list_params | {k: val}
            
        response = requests.get(f"{API_URL}/events", params=list_params, headers=headers)

        if not response.ok:
            result = dict(changed=True, response=response.text)
            module.fail_json(msg="Error listing cluster events", **result)

        result = dict(changed=False,cluster_events=response.json())

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
