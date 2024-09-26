#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = r"""
---
module: skel

short_description: A dummy module to work as a skeleton

version_added: "1.0.0"

description: A short module to be used as a skeleton for creation of modules

options:
    fail:
        description: Trigger a failure
        default: false
        type: bool

author:
    - Name (@username)
"""

EXAMPLES = r"""
# Use argument
- name: Trigger a failure
  skel
    fail: true
"""

RETURN = r"""
skel_msg:
    description: A message with the status
    type: str
    returned: always
    sample: "Success!"
"""

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        fail=dict(type="bool", required=False, default=False),
    )
    result = dict(changed=True, skel_msg="Success!")
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    if module.params['fail']:
        result["skel_msg"]="Fail!"
        module.fail_json(msg=f"Error triggered by fail={module.params.get('fail')}", **result)
    else:
        result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
