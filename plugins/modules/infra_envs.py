#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
---
module: infra_envs

short_description: Handle AssistedInstall infra-envs resources

version_added: "1.0.0"

description: Interact with infra-envs resources through the AssistedInstall API

options:
    state:
        description: The state to perform (present, absent, none for list). Note that this is required for create, delete and update operations.
        required: false
        choices: ["absent", "present"]
        default: null
        type: str
    name:
        description: Name used to create a infra-envs resource. Note that this is required for infra-envs resource create operations.
        required: false
        type: str
    pull_secret:
        description: A secret object that stores credentials to pull container images from private registries. Note that is is required for create operations.
        required: false
        type: str

author:
    - Vishwanath Jayaraman (@vjayaramrh)

"""

EXAMPLES = r"""
# Use argument
- name: create infra-envs
  infra_envs:
    state: present
    name: infra1
    pull_secret: blah

- name: List infra-envs
  infra_envs: {}

- name: Retrieve details of a specific infra-envs resource
  infra_envs:
    infra_env_id: "deadbeef-dead-beef-dead-beefdeadbeef"

- name: Delete infra-envs
  infra_envs:
    state: absent
    infra_env_id: "deadbeef-dead-beef-dead-beefdeadbeef"
"""

RETURN = r"""
result:
    description: Result from the API POST call
    type: dict
    returned: always
    sample: {
        "infra-envs": {
            "cpu_architecture": "x86_64",
            "created_at": "2025-02-28T15:39:40.008442Z",
            "download_url": "https://api.openshift.com/api/assisted-images/bytoken/tokenval/4.19/x86_64/minimal.iso",
            "email_domain": "redhat.com",
            "expires_at": "2025-02-28T19:39:40.000Z",
            "href": "/api/assisted-install/v2/infra-envs/7d4618af-d367-4c47-ab3f-49e0822a4cf7",
            "id": "7d4618af-d367-4c47-ab3f-49e0822a4cf7",
            "kind": "InfraEnv",
            "name": "testinfra",
            "openshift_version": "4.19",
            "org_id": "13125439",
            "proxy": {},
            "pull_secret_set": true,
            "type": "minimal-iso",
            "updated_at": "2025-02-28T15:39:40.035846Z",
            "user_name": "vjayaram@redhat.com"
        }
    }
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

# add additional query parameters to the query_params_list
QUERY_PARAMS_LIST = []


def run_module():

    module_args = dict(
        state=dict(
            type="str", required=False, choices=["absent", "present"], default=None
        ),
        # any API query parameters may have to be added here
        name=dict(type="str", required=False),
        pull_secret=dict(type="str", required=False, no_log=True),
    )
    token = apitoken.GetToken()
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ("state", "present", ["name", "pull_secret"])
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

    # Create infra-envs
    if module.params.get("state") == "present":

        data = remove_module_fields(module)

        response = requests.post(f"{API_URL}/infra-envs", headers=headers, json=data)

        if not response.ok:
            result = dict(changed=True, response=response.text)
            module.fail_json(msg="Error creating infra-envs", **result)

        result = {"infra_envs": response.json()}

    module.exit_json(**result)


def remove_module_fields(module):
    data = module.params.copy()
    data.pop("state")

    return data


def main():
    run_module()


if __name__ == "__main__":
    main()
