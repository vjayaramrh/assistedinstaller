# Infra-Envs Module Guide

## Overview

The `infra_envs` module provides comprehensive support for managing Infrastructure Environments (infra-envs) through the OpenShift Assisted Installer API. This module supports all CRUD operations for infra-envs including:

- **RegisterInfraEnv** (POST) - Create new infra-envs
- **ListInfraEnvs** (GET) - List all infra-envs
- **GetInfraEnv** (GET by ID) - Retrieve specific infra-env details
- **UpdateInfraEnv** (PATCH) - Update existing infra-envs
- **DeregisterInfraEnv** (DELETE) - Delete infra-envs

## Prerequisites

### Environment Variables

Set one of the following environment variables for authentication:

```bash
# Option 1: Direct API token
export AI_API_TOKEN="your-api-token"

# Option 2: Offline token (will be exchanged for API token)
export AI_OFFLINE_TOKEN="your-offline-token"

# For create operations, you'll also need:
export AI_PULL_SECRET="your-pull-secret-json"
```

### Dependencies

- Python 3.6+
- `requests` library
- Ansible 2.9+

## Module Parameters

### Required Parameters

| Parameter | Type | Description | Required For |
|-----------|------|-------------|--------------|
| `state` | str | State of the resource (`present`, `absent`) | Create, Update, Delete |
| `name` | str | Name of the infra-env | Create |
| `pull_secret` | str | Pull secret for container registry access | Create |
| `infra_env_id` | str | UUID of the infra-env | Get, Update, Delete |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `openshift_version` | str | - | OpenShift version (e.g., "4.19") |
| `cpu_architecture` | str | "x86_64" | CPU architecture (`x86_64`, `aarch64`, `arm64`, `ppc64le`, `s390x`, `multi`) |
| `image_type` | str | "minimal-iso" | Image type (`full-iso`, `minimal-iso`) |
| `ssh_authorized_key` | str | - | SSH public key for debugging |
| `cluster_id` | str | - | Cluster ID to associate with the infra-env |
| `proxy` | dict | - | Proxy configuration |
| `static_network_config` | list | - | Static network configuration |
| `ignition_config_override` | str | - | Ignition config override |
| `kernel_arguments` | list | - | Additional kernel arguments |

### Proxy Configuration

```yaml
proxy:
  http_proxy: "http://proxy.example.com:8080"
  https_proxy: "https://proxy.example.com:8080"
  no_proxy: "localhost,127.0.0.1,.example.com"
```

### Static Network Configuration

```yaml
static_network_config:
  - interface: "eth0"
    ip: "192.168.1.100"
    netmask: "255.255.255.0"
    gateway: "192.168.1.1"
    dns: ["8.8.8.8", "8.8.4.4"]
```

### Kernel Arguments

```yaml
kernel_arguments:
  - operation: "append"
    value: "console=ttyS0"
  - operation: "replace"
    value: "quiet"
  - operation: "delete"
    value: "rhgb"
```

## Usage Examples

### 1. Create Basic Infra-Env

```yaml
- name: Create basic infra-env
  infra_envs:
    state: present
    name: "my-infra-env"
    pull_secret: "{{ lookup('env', 'AI_PULL_SECRET') }}"
    openshift_version: "4.19"
    cpu_architecture: "x86_64"
  register: created_infra_env
```

### 2. Create Advanced Infra-Env

```yaml
- name: Create advanced infra-env with proxy and SSH
  infra_envs:
    state: present
    name: "advanced-infra-env"
    pull_secret: "{{ lookup('env', 'AI_PULL_SECRET') }}"
    openshift_version: "4.19"
    cpu_architecture: "x86_64"
    image_type: "full-iso"
    ssh_authorized_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ..."
    proxy:
      http_proxy: "http://proxy.example.com:8080"
      https_proxy: "https://proxy.example.com:8080"
      no_proxy: "localhost,127.0.0.1"
    static_network_config:
      - interface: "eth0"
        ip: "192.168.1.100"
        netmask: "255.255.255.0"
        gateway: "192.168.1.1"
    kernel_arguments:
      - operation: "append"
        value: "console=ttyS0"
```

### 3. List All Infra-Envs

```yaml
- name: List all infra-envs
  infra_envs:
  register: all_infra_envs

- name: Display infra-envs
  debug:
    var: all_infra_envs.infra_envs
```

### 4. Get Specific Infra-Env

```yaml
- name: Get specific infra-env
  infra_envs:
    infra_env_id: "{{ infra_env_id }}"
  register: infra_env_details
```

### 5. Update Infra-Env

```yaml
- name: Update infra-env SSH key
  infra_envs:
    state: present
    infra_env_id: "{{ infra_env_id }}"
    ssh_authorized_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... new-key"
    proxy:
      http_proxy: "http://newproxy.example.com:8080"
```

### 6. Delete Infra-Env

```yaml
- name: Delete infra-env
  infra_envs:
    state: absent
    infra_env_id: "{{ infra_env_id }}"
```

## Error Handling

The module provides comprehensive error handling:

```yaml
- name: Create infra-env with error handling
  infra_envs:
    state: present
    name: "test-infra-env"
    pull_secret: "{{ pull_secret }}"
  register: result
  failed_when: false

- name: Handle errors
  debug:
    msg: "Error: {{ result.msg }}"
  when: result.failed

- name: Handle success
  debug:
    msg: "Created infra-env: {{ result.infra_envs.id }}"
  when: not result.failed
```

## Return Values

### Success Response

```json
{
  "changed": true,
  "infra_envs": {
    "id": "uuid-of-infra-env",
    "name": "infra-env-name",
    "cpu_architecture": "x86_64",
    "created_at": "2025-02-28T15:39:40.008442Z",
    "download_url": "https://api.openshift.com/api/assisted-images/...",
    "openshift_version": "4.19",
    "proxy": {},
    "pull_secret_set": true,
    "type": "minimal-iso",
    "updated_at": "2025-02-28T15:39:40.035846Z"
  }
}
```

### Error Response

```json
{
  "changed": false,
  "failed": true,
  "msg": "Error message",
  "status_code": 400,
  "response": {
    "error": "Detailed error information"
  }
}
```

## Testing

### Unit Tests

Run the comprehensive unit tests:

```bash
# Install test dependencies
pip install -r tests/unit/requirements.txt

# Run tests
./tests/run_tests.sh
```

### Integration Tests

For integration testing against a real API:

```bash
# Set environment variables
export AI_API_TOKEN="your-token"
export AI_PULL_SECRET="your-pull-secret"

# Run the example playbook
ansible-playbook infra_envs.yml
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```
   Error: API token is required
   ```
   Solution: Set `AI_API_TOKEN` or `AI_OFFLINE_TOKEN` environment variable.

2. **Invalid Pull Secret**
   ```
   Error: pull secret is required for create operations
   ```
   Solution: Ensure pull secret is properly formatted JSON.

3. **Network Connectivity**
   ```
   Error: Connection timeout
   ```
   Solution: Check network connectivity to `api.openshift.com`.

4. **Invalid Parameters**
   ```
   Error: Bad request
   ```
   Solution: Verify parameter values against API documentation.

### Debug Mode

Enable debug output:

```yaml
- name: Debug infra-env creation
  infra_envs:
    state: present
    name: "debug-infra-env"
    pull_secret: "{{ pull_secret }}"
  register: result
  
- name: Show debug info
  debug:
    var: result
    verbosity: 2
```

## API Mapping

| Ansible Operation | HTTP Method | API Endpoint |
|------------------|-------------|--------------|
| Create (`state: present`, no `infra_env_id`) | POST | `/api/assisted-install/v2/infra-envs` |
| List (no parameters) | GET | `/api/assisted-install/v2/infra-envs` |
| Get (`infra_env_id` only) | GET | `/api/assisted-install/v2/infra-envs/{id}` |
| Update (`state: present`, with `infra_env_id`) | PATCH | `/api/assisted-install/v2/infra-envs/{id}` |
| Delete (`state: absent`) | DELETE | `/api/assisted-install/v2/infra-envs/{id}` |

## Best Practices

1. **Use Variables**: Store sensitive data like pull secrets in variables or environment variables.

2. **Error Handling**: Always register results and check for errors.

3. **Idempotency**: The module is designed to be idempotent. Running the same task multiple times should produce the same result.

4. **Resource Management**: Always clean up test resources to avoid quota issues.

5. **Version Compatibility**: Specify OpenShift versions explicitly for consistent behavior.

## Examples Repository

See the `infra_envs.yml` playbook for comprehensive examples demonstrating all operations.

## Contributing

To add support for additional infra-envs REST APIs:

1. Add new parameters to the module arguments
2. Update the `prepare_infra_env_data` function
3. Add new operation functions if needed
4. Update documentation and examples
5. Add unit tests for new functionality

## Support

For issues related to the module:
- Check the troubleshooting section
- Review the unit tests for usage patterns
- Consult the OpenShift Assisted Installer API documentation 