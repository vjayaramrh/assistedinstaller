#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os
import requests


__metaclass__ = type

DOCUMENTATION = r"""
---
module: features

short_description: Query OpenShift features

version_added: "1.0.0"

description: Query supported features for a given OpenShift version

options:
  openshift_version:
    description: Version of OpenShift
    required: True
    type: string

  cpu_architecture:
    description: The CPU architecture of the OpenShift version
    required: False
    choices: [x86_64, aarch64, arm64, ppc64le, s390x, multi]
    default: x86_64
    type: string

  platform_type:
    description: The provider platform type
    required: False
    choices: [baremetal, none, nutanix, vsphere, external]
    type: string

  external_platform:
    description: External platform name when platform_type is external
    required: False
    type: string

author:
    - Chris Wheeler (@clwheel)
"""

EXAMPLES = r"""
# Use argument
- name: Query OpenShift features
  features:
    openshift_version: 4.16.19
    cpu_architecture: x86_64
    platform_type: baremetal
"""

RETURN = r"""
features:
  description: A list of supported OpenShift features
  type: dict
  returned: always
  sample: { "CLUSTER_MANAGED_NETWORKING": "supported",
            "CNV": "supported",
            "CUSTOM_MANIFEST": "supported",
            "DUAL_STACK": "supported",
            "DUAL_STACK_VIPS": "supported",
            "FULL_ISO": "supported",
            "LSO": "supported",
            "LVM": "supported",
            "MCE": "supported",
            "MINIMAL_ISO": "supported",
            "ODF": "supported",
            "OVN_NETWORK_TYPE": "supported",
            "PLATFORM_MANAGED_NETWORKING": "unsupported",
            "SDN_NETWORK_TYPE": "unavailable",
            "SINGLE_NODE_EXPANSION": "supported",
            "SKIP_MCO_REBOOT": "supported",
            "SNO": "supported",
            "USER_MANAGED_NETWORKING": "supported",
            "VIP_AUTO_ALLOC": "unavailable" }

"""

from ansible.module_utils.basic import AnsibleModule

API_VERSION = "v2"
API_URL = f"https://api.openshift.com/api/assisted-install/{API_VERSION}"
QUERY_PARAMS_LIST = ["openshift_version", "cpu_architecture", "platform_type", "external_platform_name"]

def run_module():
    module_args = dict(
        openshift_version = dict(type="str", required=True),
        cpu_architecture = dict(type="str", required=False, default="x86_64", choices=["x86_64", "aarch64", "arm64", "ppc64le", "s390x", "multi"]),
        platform_type = dict(type="str", required=False, choices=["baremetal", "none", "nutanix", "vsphere", "external"]),
        external_platform_name = dict(type="str", required=False)
    )

    token = os.environ.get('AI_API_TOKEN')
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    query_params = {}

    for k in QUERY_PARAMS_LIST:
        val = module.params.get(k)
        if val:
            query_params = query_params | { k: val }

    response = requests.get(f"{API_URL}/support-levels/features", params=query_params, headers=headers)

    if not response.ok:
        result = dict(changed=True, response=response.text)
        module.fail_json(msg="Error querying features", **result)

    result = response.json()
    
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
