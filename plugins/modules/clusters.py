#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
---
module: clusters

short_description: Handle AssistedInstall clusters

version_added: "1.0.0"

description: Interact with clusters through the AssistedInstall API

options:
    state:
        description: The state to perform (present, absent, none for list). Note that this is required for create, delete and update operations.
        required: false
        choices: ["absent", "present"]
        default: null
        type: str
    cluster_id:
        description: The cluster ID to perform the action on
        required: false
        type: str
    with_hosts:
        description: Include hosts in the returned list
        required: false
        default: false
        type: bool
    name:
        description: Name used to register a cluster (required for present). Note that is required for cluster create operations.
        required: false
        type: str
    openshift_version:
        description: OpenShift version used to register a cluster (required for present). Note that is required for cluster create operations.
        required: false
        type: str

author:
    - Vishwanath Jayaraman (@vjayaramrh)
    - Tony García (@tonyskapunk)
    - Daniel Kostecki (@dkosteck)
"""

EXAMPLES = r"""
# Use argument
- name: List clusters
  clusters:

- name: Delete cluster
  clusters:
    state: absent
    cluster_id: "deadbeef-dead-beef-dead-beefdeadbeef"
"""

RETURN = r"""
clusters:
    description: A message with the status
    type: list
    returned: always
    sample: []
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
QUERY_PARAMS_LIST = ["with_hosts"]


def run_module():

    module_args = dict(
        state=dict(
            type="str", required=False, choices=["absent", "present"], default=None
        ),
        cluster_id=dict(type="str", required=False),
        # any API query parameters may have to be added here
        with_hosts=dict(type="bool", required=False, default=False),
        name=dict(type="str", required=False),
        openshift_version=dict(type="str", required=False),
    )
    token = os.environ.get("AI_API_TOKEN")
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ("state", "present", ["name", "openshift_version"]),
            ("state", "absent", ["cluster_id"]),
        ],
        supports_check_mode=False,
    )

    # Fail if requests is not installed
    if not HAS_REQUESTS:
        module.fail_json(
            msg=missing_required_lib("requests"), exception=REQUESTS_IMPORT_ERROR
        )

    # Set headers
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    # Delete cluster
    if module.params.get("state") == "absent":
        if not module.params.get("cluster_id"):
            module.fail_json(msg="cluster_id is required for delete action")

        response = requests.delete(
            f"{API_URL}/clusters/{module.params.get('cluster_id')}", headers=headers
        )

        if response.status_code != 204:
            result = dict(response=response.text)
            module.fail_json(
                msg=f"Error deleting cluster_id: {module.params.get('cluster_id')}",
                **result,
            )

        result = dict(changed=True, clusters=[])

    # Register cluster
    elif module.params.get("state") == "present":
        pull_secret = os.environ.get("AI_PULL_SECRET")

        data = remove_module_fields(module)
        data["pull_secret"] = pull_secret

        response = requests.post(f"{API_URL}/clusters", headers=headers, json=data)

        if not response.ok:
            result = dict(changed=True, response=response.text)
            module.fail_json(msg="Error registering cluster", **result)

        result = dict(clusters=response.json())

    # List clusters
    else:
        list_params = {}
        for k in QUERY_PARAMS_LIST:
            val = module.params.get(k)
            if val:
                list_params = list_params | {k: val}

        response = requests.get(
            f"{API_URL}/clusters", params=list_params, headers=headers
        )

        if not response.ok:
            result = dict(changed=True, response=response.text)
            module.fail_json(msg="Error listing clusters", **result)

        result = dict(clusters=response.json())

    module.exit_json(**result)


def remove_module_fields(module):
    data = module.params.copy()
    data.pop("state")
    data.pop("with_hosts")
    data.pop("cluster_id")

    return data


def main():
    run_module()


if __name__ == "__main__":
    main()
