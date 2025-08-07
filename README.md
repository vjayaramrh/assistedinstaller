# assistedinstaller ansible module

## Requirements

- Red Hat account in https://console.redhat.com
- Offline token from  https://console.redhat.com/openshift/token
- ocm-cli client from https://github.com/openshift-online/ocm-cli/releases or https://console.redhat.com/openshift/downloads#tool-ocm-api-token

## Modules

This collection provides the following modules for interacting with the OpenShift Assisted Installer API:

### component_versions
Query supported OpenShift component versions from the Assisted Installer API.

**Options:**
- `openshift_version` (optional): Filter by specific OpenShift version
- `cpu_architecture` (optional): Filter by CPU architecture (x86_64, aarch64, arm64, ppc64le, s390x, multi)

**Example:**
```yaml
- name: List all component versions
  component_versions:
  register: all_versions

- name: List component versions for OpenShift 4.18
  component_versions:
    openshift_version: "4.18"
  register: openshift_418_versions
```

### clusters
Handle AssistedInstall clusters - create, list, and delete clusters.

### events
Query events from the Assisted Installer API.

### infra_envs
Manage infrastructure environments.

### openshift_versions
Query supported OpenShift versions.

### support_levels
Query OpenShift support levels for architectures and features.

### supported_operators
List supported operators.

## References
- Swagger UI -> https://api.openshift.com/?urls.primaryName=assisted-service%20service (next select the `assisted-service service` from the top right drop down menu)
