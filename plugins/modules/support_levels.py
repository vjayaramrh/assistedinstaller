#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: support_levels

short_description: Query OpenShift support levels

version_added: "1.0.0"

description: Query supported architectures or features for a given OpenShift version

options:
  resource_type:
    description: Type of resource to query
    required: True
    choices: [architectures, features]
    type: str

  openshift_version:
    description: Version of OpenShift
    required: True
    type: str

  cpu_architecture:
    description: The CPU architecture of the OpenShift version
    required: False
    choices: [x86_64, aarch64, arm64, ppc64le, s390x, multi]
    default: x86_64
    type: str

  platform_type:
    description: The provider platform type
    required: False
    choices: [baremetal, none, nutanix, vsphere, external]
    type: str

  external_platform_name:
    description: External platform name when platform_type is external
    required: False
    type: str

author:
    - Chris Wheeler (@clwheel)
"""

EXAMPLES = r"""
- name: Query OpenShift architectures
  support_levels:
    resource_type: architectures
    openshift_version: 4.16.19
  register: architectures_result

- name: Query OpenShift features
  support_levels:
    resource_type: features
    openshift_version: 4.16.19
    cpu_architecture: x86_64
    platform_type: baremetal
  register: features_result
"""

RETURN = r"""
architectures:
  description: A list of supported OpenShift architectures
  type: dict
  returned: always
  sample: { "ARM64_ARCHITECTURE": "supported",
            "MULTIARCH_RELEASE_IMAGE": "tech-preview",
            "PPC64LE_ARCHITECTURE": "supported",
            "S390X_ARCHITECTURE": "supported",
            "X86_64_ARCHITECTURE": "supported" }

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
from ansible.module_utils.basic import missing_required_lib

import traceback

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
QUERY_PARAMS_LIST = ["openshift_version", "cpu_architecture", "platform_type", "external_platform_name"]


def run_module():
    module_args = dict(
        resource_type=dict(type="str", required=True, choices=["architectures", "features"]),
        openshift_version=dict(type="str", required=True),
        cpu_architecture=dict(type="str", required=False, default="x86_64", choices=["x86_64", "aarch64", "arm64", "ppc64le", "s390x", "multi"]),
        platform_type=dict(type="str", required=False, choices=["baremetal", "none", "nutanix", "vsphere", "external"]),
        external_platform_name=dict(type="str", required=False)
    )

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

    resource_type = module.params.get('resource_type')
    query_params = {}

    for k in QUERY_PARAMS_LIST:
        val = module.params.get(k)
        if val:
            query_params = query_params | {k: val}

    response = requests.get(f"{API_URL}/support-levels/{resource_type}", params=query_params, headers=headers)

    if not response.ok:
        result = dict(changed=True, response=response.text)
        module.fail_json(msg=f"Error querying {resource_type}", **result)

    result = response.json()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
