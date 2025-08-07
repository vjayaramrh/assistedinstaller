#!/usr/bin/python
# -*- coding: utf-8 -*-

# assisted-by: Claude 3.5 Sonnet (Cursor)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: component_versions

short_description: List OpenShift component versions

version_added: "1.0.0"

description: Retrieves the list of supported OpenShift component versions from the Assisted Installer API.

options:
  openshift_version:
    description: Filter by specific OpenShift version
    required: false
    type: str

  cpu_architecture:
    description: Filter by CPU architecture
    required: false
    choices: [x86_64, aarch64, arm64, ppc64le, s390x, multi]
    type: str

author:
    - Daniel Kostecki (@dkosteck)
"""

EXAMPLES = r"""
# List all component versions
- name: List all component versions
  component_versions:
  register: all_component_versions

# List component versions for specific OpenShift version
- name: List component versions for OpenShift 4.18
  component_versions:
    openshift_version: "4.18"
  register: openshift_418_component_versions

# List component versions for specific architecture
- name: List component versions for x86_64 architecture
  component_versions:
    cpu_architecture: x86_64
  register: x86_64_component_versions

# List component versions for specific OpenShift version and architecture
- name: List component versions for OpenShift 4.18 on x86_64
  component_versions:
    openshift_version: "4.18"
    cpu_architecture: x86_64
  register: filtered_component_versions
"""

RETURN = r"""
component_versions:
  description: A list of supported OpenShift component versions
  type: dict
  returned: always
  sample: {
    "4.18.1": {
      "components": {
        "cluster-version-operator": "4.18.1",
        "machine-config-operator": "4.18.1",
        "cluster-network-operator": "4.18.1",
        "cluster-storage-operator": "4.18.1"
      },
      "openshift_version": "4.18.1",
      "cpu_architecture": "x86_64",
      "release_image": "quay.io/openshift-release-dev/ocp-release:4.18.1-x86_64"
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
    "openshift_version",
    "cpu_architecture",
]


def run_module():
    module_args = dict(
        openshift_version=dict(type="str", required=False),
        cpu_architecture=dict(type="str", required=False, choices=["x86_64", "aarch64", "arm64", "ppc64le", "s390x", "multi"])
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
        apiurl.GetURL("/component-versions"),
        params=query_params,
        headers=headers,
    )

    if not response.ok:
        try:
            res = response.json()
        except requests.JSONDecodeError:
            res = response.text

        result = dict(changed=False, response=res, component_versions={})
        module.fail_json(msg="Error querying component versions", **result)

    result = dict(changed=False, component_versions=response.json())

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
