#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: release_sources

short_description: Query release source configurations

version_added: "1.0.0"

description: Retrieves the list of release source configurations from the Assisted Service API.

options: {}

author:
    - Chris Wheeler (@clwheel)
"""

EXAMPLES = r"""
# List all release source configurations
- name: List release sources
  release_sources:
  register: sources_result

- name: Display release sources
  debug:
    var: sources_result.release_sources
"""

RETURN = r"""
release_sources:
    description: A list of release source configurations
    type: list
    returned: always
    sample: [
        {
            "op_shift_version": "4.19.0",
            "url": "https://example.com/release-images/4.19.0",
            "version": "4.19.0"
        }
    ]
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

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


def run_module():
    module_args = dict()

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    # Fail if requests is not installed
    if not HAS_REQUESTS:
        module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMPORT_ERROR)

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {apitoken.GetToken()}'
    }

    response = requests.get(
        apiurl.GetURL("/release-sources"),
        headers=headers,
    )

    if not response.ok:
        result = dict(changed=False, response=response.text)
        module.fail_json(msg="Error querying release sources", **result)

    module.exit_json(release_sources=response.json())


def main():
    run_module()


if __name__ == "__main__":
    main() 