#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: infra_envs

short_description: Handle AssistedInstall infra-envs resources

version_added: "1.0.0"

description: 
    - Interact with infra-envs resources through the AssistedInstall API
    - Supports all CRUD operations for infra-envs
    - RegisterInfraEnv (POST), ListInfraEnvs (GET), GetInfraEnv (GET by ID), UpdateInfraEnv (PATCH), DeregisterInfraEnv (DELETE)

options:
    state:
        description: The state to perform (present, absent, none for list). Note that this is required for create, delete and update operations.
        required: false
        choices: ["absent", "present"]
        default: null
        type: str
    infra_env_id:
        description: The infra-env ID to perform the action on (required for get, update, delete operations)
        required: false
        type: str
    name:
        description: Name used to create a infra-envs resource. Note that this is required for infra-envs resource create operations.
        required: false
        type: str
    pull_secret:
        description: A secret object that stores credentials to pull container images from private registries. Note that this is required for create operations.
        required: false
        type: str
        no_log: true
    openshift_version:
        description: OpenShift version to be used for the infra-env
        required: false
        type: str
    cpu_architecture:
        description: The CPU architecture of the infra-env
        required: false
        type: str
        choices: ["x86_64", "aarch64", "arm64", "ppc64le", "s390x", "multi"]
        default: "x86_64"
    ssh_authorized_key:
        description: SSH public key for debugging the installation
        required: false
        type: str
    cluster_id:
        description: The cluster ID to associate with the infra-env
        required: false
        type: str
    image_type:
        description: The type of image to generate
        required: false
        type: str
        choices: ["full-iso", "minimal-iso"]
        default: "minimal-iso"
    proxy:
        description: Proxy settings for the infra-env
        required: false
        type: dict
        suboptions:
            http_proxy:
                description: HTTP proxy URL
                type: str
            https_proxy:
                description: HTTPS proxy URL
                type: str
            no_proxy:
                description: Comma-separated list of hosts that should not use proxy
                type: str
    static_network_config:
        description: Static network configuration for the infra-env
        required: false
        type: list
        elements: dict
    ignition_config_override:
        description: Ignition config override for the infra-env
        required: false
        type: str
    kernel_arguments:
        description: Additional kernel arguments for the infra-env
        required: false
        type: list
        elements: dict

author:
    - Vishwanath Jayaraman (@vjayaramrh)
"""

EXAMPLES = r"""
# Create infra-env
- name: Create infra-env
  infra_envs:
    state: present
    name: my-infra-env
    pull_secret: "{{ pull_secret }}"
    openshift_version: "4.19"
    cpu_architecture: "x86_64"
    ssh_authorized_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ..."
    image_type: "minimal-iso"
    proxy:
      http_proxy: "http://proxy.example.com:8080"
      https_proxy: "https://proxy.example.com:8080"
      no_proxy: "localhost,127.0.0.1"

# List all infra-envs
- name: List infra-envs
  infra_envs:
  register: infra_envs_list

# Get details of a specific infra-env
- name: Get infra-env details
  infra_envs:
    infra_env_id: "deadbeef-dead-beef-dead-beefdeadbeef"
  register: infra_env_details

# Update infra-env
- name: Update infra-env
  infra_envs:
    state: present
    infra_env_id: "deadbeef-dead-beef-dead-beefdeadbeef"
    ssh_authorized_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ..."
    proxy:
      http_proxy: "http://newproxy.example.com:8080"

# Delete infra-env
- name: Delete infra-env
  infra_envs:
    state: absent
    infra_env_id: "deadbeef-dead-beef-dead-beefdeadbeef"
"""

RETURN = r"""
infra_envs:
    description: List of infra-envs or single infra-env details
    type: list or dict
    returned: always
    sample: [
        {
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
    ]
changed:
    description: Whether the operation resulted in changes
    type: bool
    returned: always
    sample: true
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

# Query parameters that should be passed to the API
QUERY_PARAMS_LIST = []


def run_module():
    proxy_spec = dict(
        http_proxy=dict(type="str", required=False),
        https_proxy=dict(type="str", required=False),
        no_proxy=dict(type="str", required=False),
    )
    
    kernel_arg_spec = dict(
        operation=dict(type="str", required=False, choices=["append", "replace", "delete"]),
        value=dict(type="str", required=False),
    )

    module_args = dict(
        state=dict(
            type="str", required=False, choices=["absent", "present"], default=None
        ),
        infra_env_id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        pull_secret=dict(type="str", required=False, no_log=True),
        openshift_version=dict(type="str", required=False),
        cpu_architecture=dict(
            type="str", 
            required=False, 
            choices=["x86_64", "aarch64", "arm64", "ppc64le", "s390x", "multi"],
            default="x86_64"
        ),
        ssh_authorized_key=dict(type="str", required=False),
        cluster_id=dict(type="str", required=False),
        image_type=dict(
            type="str", 
            required=False, 
            choices=["full-iso", "minimal-iso"],
            default="minimal-iso"
        ),
        proxy=dict(type="dict", required=False, options=proxy_spec),
        static_network_config=dict(type="list", required=False, elements="dict"),
        ignition_config_override=dict(type="str", required=False),
        kernel_arguments=dict(type="list", required=False, elements="dict", options=kernel_arg_spec),
    )

    token = apitoken.GetToken()
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ("state", "present", ["name"], True),  # name required for create, optional for update
            ("state", "absent", ["infra_env_id"]),
        ],
        supports_check_mode=False,
    )

    # Fail if requests is not installed
    if not HAS_REQUESTS:
        module.fail_json(
            msg=missing_required_lib("requests"), exception=REQUESTS_IMPORT_ERROR
        )

    if not token:
        module.fail_json(msg="API token is required. Set AI_API_TOKEN or AI_OFFLINE_TOKEN environment variable.")

    # Set headers
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    # Determine operation based on parameters
    infra_env_id = module.params.get("infra_env_id")
    state = module.params.get("state")

    try:
        if state == "absent":
            # Delete infra-env
            result = delete_infra_env(module, headers, infra_env_id)
        elif state == "present":
            if infra_env_id:
                # Update existing infra-env
                result = update_infra_env(module, headers, infra_env_id)
            else:
                # Create new infra-env
                result = create_infra_env(module, headers)
        elif infra_env_id:
            # Get specific infra-env
            result = get_infra_env(module, headers, infra_env_id)
        else:
            # List all infra-envs
            result = list_infra_envs(module, headers)

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}", exception=traceback.format_exc())


def create_infra_env(module, headers):
    """Create a new infra-env (RegisterInfraEnv)"""
    data = prepare_infra_env_data(module)
    
    response = requests.post(f"{API_URL}/infra-envs", headers=headers, json=data)
    
    if response.status_code == 201:
        return dict(changed=True, infra_envs=response.json())
    else:
        handle_error_response(module, response, "Error creating infra-env")


def list_infra_envs(module, headers):
    """List all infra-envs (ListInfraEnvs)"""
    response = requests.get(f"{API_URL}/infra-envs", headers=headers)
    
    if response.status_code == 200:
        return dict(changed=False, infra_envs=response.json())
    else:
        handle_error_response(module, response, "Error listing infra-envs")


def get_infra_env(module, headers, infra_env_id):
    """Get specific infra-env (GetInfraEnv)"""
    response = requests.get(f"{API_URL}/infra-envs/{infra_env_id}", headers=headers)
    
    if response.status_code == 200:
        return dict(changed=False, infra_envs=response.json())
    elif response.status_code == 404:
        module.fail_json(msg=f"Infra-env with ID {infra_env_id} not found")
    else:
        handle_error_response(module, response, f"Error getting infra-env {infra_env_id}")


def update_infra_env(module, headers, infra_env_id):
    """Update existing infra-env (UpdateInfraEnv)"""
    data = prepare_infra_env_data(module, update=True)
    
    response = requests.patch(f"{API_URL}/infra-envs/{infra_env_id}", headers=headers, json=data)
    
    if response.status_code == 200:
        return dict(changed=True, infra_envs=response.json())
    elif response.status_code == 404:
        module.fail_json(msg=f"Infra-env with ID {infra_env_id} not found")
    else:
        handle_error_response(module, response, f"Error updating infra-env {infra_env_id}")


def delete_infra_env(module, headers, infra_env_id):
    """Delete infra-env (DeregisterInfraEnv)"""
    response = requests.delete(f"{API_URL}/infra-envs/{infra_env_id}", headers=headers)
    
    if response.status_code == 204:
        return dict(changed=True, infra_envs=[])
    elif response.status_code == 404:
        module.fail_json(msg=f"Infra-env with ID {infra_env_id} not found")
    else:
        handle_error_response(module, response, f"Error deleting infra-env {infra_env_id}")


def prepare_infra_env_data(module, update=False):
    """Prepare data for API request"""
    data = {}
    
    # Required fields for creation
    if not update:
        if module.params.get("name"):
            data["name"] = module.params.get("name")
        if module.params.get("pull_secret"):
            data["pull_secret"] = module.params.get("pull_secret")
    
    # Optional fields
    if module.params.get("openshift_version"):
        data["openshift_version"] = module.params.get("openshift_version")
    
    if module.params.get("cpu_architecture"):
        data["cpu_architecture"] = module.params.get("cpu_architecture")
    
    if module.params.get("ssh_authorized_key"):
        data["ssh_authorized_key"] = module.params.get("ssh_authorized_key")
    
    if module.params.get("cluster_id"):
        data["cluster_id"] = module.params.get("cluster_id")
    
    if module.params.get("image_type"):
        data["image_type"] = module.params.get("image_type")
    
    if module.params.get("proxy"):
        data["proxy"] = module.params.get("proxy")
    
    if module.params.get("static_network_config"):
        data["static_network_config"] = module.params.get("static_network_config")
    
    if module.params.get("ignition_config_override"):
        data["ignition_config_override"] = module.params.get("ignition_config_override")
    
    if module.params.get("kernel_arguments"):
        data["kernel_arguments"] = module.params.get("kernel_arguments")
    
    return data


def handle_error_response(module, response, error_msg):
    """Handle API error responses"""
    try:
        error_details = response.json()
    except ValueError:
        error_details = response.text
    
    module.fail_json(
        msg=error_msg,
        changed=False,
        response=error_details,
        status_code=response.status_code,
        infra_envs=[]
    )


def main():
    run_module()


if __name__ == "__main__":
    main()
