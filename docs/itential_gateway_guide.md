# Gateway Role

The playbook and role in this section install and configure the Itential Automation Gateway (IAG).

## Role

### Gateway Role

The `gateway` role performs a base install of IAG including any OS packages required. It includes
the appropriate versions of Python, Pip, and Ansible. It creates the appropriate Linux users,
directories, log files, and systemd services. It will start the automation-gateway service when
complete.

## Variables

### Static Variables

The variables located in the `vars` directory of the role are "static" and not meant to be overridden by the user. Since these variable files are included at run-time based on the IAG release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

### Gateway Role Variables

The variables in this section may be overridden in the inventory in the `gateway` group vars.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `gateway_release` | Fixed-point | Designates which major release version of IAG to install. | N/A |
| `gateway_whl_file` | String | The name of the IAG wheel file to install. | N/A |
| `gateway_archive_download_url` | String | The URL for the download of the iag whl file from a repository. | N/A |
| `repository_username` | String | The username for authentication of the repository from gateway_archive_download_url. | N/A |
| `repository_password` | String | The password for authentication of the repository from gateway_archive_download_url. | N/A |
| `repository_api_key` | String | The API for authentication of the repository from gateway_archive_download_url. Can be used instead of username/password for authentication.| N/A |

The `gateway_release` and either `gateway_whl_file` or `gateway_archive_download_url` must be
configured in the inventory. When `gateway_archive_download_url` is configured, the
`repository_username`/`repository_password` or `repository_api_key` must be defined.

The following table lists the default variables located in `roles/gateway/defaults/main/gateway.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `gateway_enable_ansible` | Boolean | Flag to enable Ansible. | `true` |
| `gateway_enable_nornir` | Boolean | Flag to enable Nornir. | `true` |
| `gateway_enable_netmiko` | Boolean | Flag to enable Netmiko. | `true` |
| `gateway_enable_scripts` | Boolean | Flag to enable scripts. | `true` |
| `gateway_enable_netconf` | Boolean | Flag to enable Netconf requests. | `true` |
| `gateway_enable_httpreq` | Boolean | Flag to enable HTTP requests. | `true` |
| `gateway_enable_python_venv` | Boolean | Flag to enable Python virtual environments. | `true` |
| `gateway_enable_grpc` | Boolean | Flag to enable GRPC requests. | `true` |
| `gateway_enable_git` | Boolean | Flag to enable Git integration. | `true` |
| `gateway_install_dir` | String | The base directory where to install the IAG files. | `/opt/automation-gateway` |
| `gateway_ansible_collections_path` | String | The location of IAG Ansible collections. | `{{ gateway_install_dir }}/ansible/collections` |
| `gateway_data_dir` | String | The IAG data directory. | `/var/lib/automation-gateway` |
| `gateway_log_dir` | String | The IAG log directory. | `/var/log/automation-gateway` |
| `gateway_port` | Integer | The IAG HTTP listen port. | `8083` |
| `gateway_properties_location` | String | The location of the IAG configuration file. | `/etc/automation-gateway` |
| `gateway_user` | String | The IAG Linux user. | `itential` |
| `gateway_group` | String | The IAG Linux group. | `itential` |
| `gateway_user_home_dir` | String | The home directory for the IAG user. | `/home/{{ gateway_user }}` |
| `gateway_user_shell_rc_file` | String | The shell RC file for the IAG user. | `{{ gateway_user_home_dir }}/.bashrc` |
| `gateway_https_enabled` | Boolean | Flag to enable HTTPS in Gateway configuration. | `true` |
| `gateway_https_port` | Integer | The IAG HTTPS listen port. | `8443` |
| `gateway_pki_copy_certs` | Boolean | Flag to manage PKI infrastructure (create directories and copy certificates). | `true` |
| `gateway_tlsv1_2` | Boolean | Flag to enable TLS 1.2. | `false` |
| `gateway_http_server_threads` | Integer | The number of http server threads for handling requests. | `{{ ansible_processor_cores * 4 }}` |
| `gateway_venv_name` | String | The name of the Python virtual environment. | `venv` |
| `gateway_python_venv` | String | The full path to the Python virtual environment. | `{{ gateway_install_dir }}/{{ gateway_venv_name }}` |

### Gateway PKI Variables

The following table lists the PKI-related variables located in `roles/gateway/defaults/main/pki.yml`. These variables define the PKI infrastructure and certificate file locations.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `gateway_pki_base_dir` | String | Base directory for Gateway PKI files. | `/etc/pki/automation-gateway` |
| `gateway_pki_private_subdir` | String | Subdirectory name for private keys. | `private` |
| `gateway_pki_https_subdir` | String | Subdirectory name for HTTPS certificates. | `https` |
| `gateway_pki_private_dir` | String | Full path to private keys directory. | `{{ gateway_pki_base_dir }}/{{ gateway_pki_private_subdir }}` |
| `gateway_pki_https_dir` | String | Full path to HTTPS certificates directory. | `{{ gateway_pki_base_dir }}/{{ gateway_pki_https_subdir }}` |
| `gateway_pki_src_dir` | String | Source directory on Ansible controller containing certificates. Must be set in inventory when copying certificates. | `""` |
| `gateway_https_cert_file` | String | HTTPS certificate filename (supports per-host certificates). | `{{ inventory_hostname }}.crt` |
| `gateway_https_key_file` | String | HTTPS private key filename (supports per-host certificates). | `{{ inventory_hostname }}.key` |
| `gateway_https_ca_file` | String | CA bundle filename. | `ca-bundle.crt` |
| `gateway_https_cert_dest` | String | Full destination path for HTTPS certificate. | `{{ gateway_pki_https_dir }}/{{ gateway_https_cert_file }}` |
| `gateway_https_key_dest` | String | Full destination path for HTTPS private key. | `{{ gateway_pki_private_dir }}/{{ gateway_https_key_file }}` |
| `gateway_https_ca_dest` | String | Full destination path for CA bundle. | `{{ gateway_pki_https_dir }}/{{ gateway_https_ca_file }}` |
| `gateway_https_cert_src` | String | Full source path for HTTPS certificate on controller. | `{{ gateway_pki_src_dir }}/{{ gateway_https_cert_file }}` |
| `gateway_https_key_src` | String | Full source path for HTTPS private key on controller. | `{{ gateway_pki_src_dir }}/{{ gateway_https_key_file }}` |
| `gateway_https_ca_src` | String | Full source path for CA bundle on controller. | `{{ gateway_pki_src_dir }}/{{ gateway_https_ca_file }}` |

## Configuring HTTPS

Gateway supports flexible HTTPS configuration with independent control over infrastructure preparation and HTTPS enablement. The Gateway role does not generate SSL certificates.

### Configuration Variables

Two variables control Gateway HTTPS behavior:

* `gateway_pki_copy_certs` - Controls PKI infrastructure (directories and certificate files)
* `gateway_https_enabled` - Controls HTTPS enablement in Gateway configuration

### Use Cases

**Use Case 1: Full HTTPS Deployment (Standard)**

Deploy Gateway with HTTPS enabled and automated certificate management.

```yaml
gateway_pki_copy_certs: true        # Prepare infrastructure and copy certificates
gateway_https_enabled: true         # Enable HTTPS in Gateway
gateway_pki_src_dir: "<path/to/local/gateway/certs>"
```

**Use Case 2: Prepare Certificates Only (Staged Deployment)**

Prepare PKI infrastructure and deploy certificates without enabling HTTPS. Useful for staged rollouts or pre-deployment preparation.

```yaml
gateway_pki_copy_certs: true        # Prepare infrastructure and copy certificates
gateway_https_enabled: false        # Keep HTTPS disabled for now
gateway_pki_src_dir: "<path/to/local/gateway/certs>"
```

Gateway will run on HTTP. Enable HTTPS later by setting `gateway_https_enabled: true` and re-running the playbook.

**Use Case 3: HTTP Only (Development)**

Deploy Gateway with HTTP only, no certificate infrastructure.

```yaml
gateway_pki_copy_certs: false       # No certificate infrastructure
gateway_https_enabled: false        # HTTP only
```

**Use Case 4: External Certificate Management**

Use externally managed certificates (cert-manager, Vault, manual placement) with HTTPS enabled.

```yaml
gateway_pki_copy_certs: false       # Don't copy certificates (managed externally)
gateway_https_enabled: true         # Enable HTTPS
```

**Important:** Certificates must exist at expected paths:
* `/etc/pki/automation-gateway/https/{{ inventory_hostname }}.crt`
* `/etc/pki/automation-gateway/private/{{ inventory_hostname }}.key`
* `/etc/pki/automation-gateway/https/ca-bundle.crt`

**Note:** All these paths are configurable in `roles/gateway/defaults/main/pki.yml` file or in inventory file

### Certificate Organization

The deployer expects certificates organized in a flat directory structure:

```
<path/to/local/gateway/certs>/
    ├─ gateway-server1.example.com.crt
    ├─ gateway-server1.example.com.key
    ├─ gateway-server2.example.com.crt
    ├─ gateway-server2.example.com.key
    └─ ca-bundle.crt
```

Set `gateway_pki_src_dir` to point to this directory. The deployer will automatically select the correct certificate file for each host using `{{ inventory_hostname }}`.

### Certificate Naming

By default, certificates are named using `{{ inventory_hostname }}`:
* Certificate: `{{ inventory_hostname }}.crt`
* Key: `{{ inventory_hostname }}.key`
* CA bundle: `ca-bundle.crt` (shared across all hosts)

To use different naming:

```yaml
# Use a shared certificate for all Gateway servers
gateway_https_cert_file: "gateway.crt"
gateway_https_key_file: "gateway.key"
```

## Building the Inventory

To install and configure IAG, add a `gateway` group and host(s) to your inventory and configure the
`gateway_release` and `gateway_whl_file`.

## Example Inventory - Single IAG Node

```yaml
all:
  children:
    gateway:
      hosts:
        gateway-server1.example.com:
          ansible_host: 10.1.1.10
      vars:
        gateway_release: 4.3
        gateway_whl_file: automation_gateway-4.3.0-py3-none-any.whl
```

## Example Inventory - IAG Native HTTPS (Full Deployment)

```yaml
all:
  children:
    gateway:
      hosts:
        gateway-server1.example.com:
          ansible_host: 10.1.1.10
      vars:
        gateway_release: 4.3
        gateway_whl_file: automation_gateway-4.3.0-py3-none-any.whl
        gateway_https_enabled: true
        gateway_pki_copy_certs: true
        gateway_pki_src_dir: "<path/to/local/gateway/certs>"
```

Certificate directory structure:
```
<path/to/local/gateway/certs>/
    ├─ gateway-server1.example.com.crt
    ├─ gateway-server1.example.com.key
    └─ ca-bundle.crt
```

## Example Inventory - Multiple Gateway Servers with HTTPS

```yaml
all:
  children:
    gateway:
      hosts:
        gateway-server1.example.com:
          ansible_host: 10.1.1.10
        gateway-server2.example.com:
          ansible_host: 10.1.1.11
        gateway-server3.example.com:
          ansible_host: 10.1.1.12
      vars:
        gateway_release: 4.3
        gateway_whl_file: automation_gateway-4.3.0-py3-none-any.whl
        gateway_https_enabled: true
        gateway_pki_copy_certs: true
        gateway_pki_src_dir: "<path/to/local/gateway/certs>"
```

Certificate directory structure:
```
<path/to/local/gateway/certs>/
    ├─ gateway-server1.example.com.crt
    ├─ gateway-server1.example.com.key
    ├─ gateway-server2.example.com.crt
    ├─ gateway-server2.example.com.key
    ├─ gateway-server3.example.com.crt
    ├─ gateway-server3.example.com.key
    └─ ca-bundle.crt
```

Each Gateway server will receive its unique certificate automatically based on its hostname.

## Example Inventory - Staged Deployment (Prepare Certificates First)

```yaml
all:
  children:
    gateway:
      hosts:
        gateway-server1.example.com:
          ansible_host: 10.1.1.10
      vars:
        gateway_release: 4.3
        gateway_whl_file: automation_gateway-4.3.0-py3-none-any.whl
        gateway_https_enabled: false        # Deploy without HTTPS initially
        gateway_pki_copy_certs: true        # But prepare certificates
        gateway_pki_src_dir: "<path/to/local/gateway/certs>"
```

Later, enable HTTPS by changing `gateway_https_enabled: true` and re-running the playbook.

## Running the Playbook

To execute the Gateway role, run the `gateway` playbook:

```bash
ansible-playbook itential.deployer.gateway -i <inventory>
```

You can also use the following tags:

* `upload_gateway_certificates` - Only manage certificate infrastructure
* `install_python` - Only install Python
* `install_python_dependencies` - Only install Python dependencies
* `install_gateway_build_packages` - Only install Gateway build packages
* `uninstall_gateway_build_packages` - Only uninstall Gateway build packages

To execute only certificate management tasks:

```bash
ansible-playbook itential.deployer.gateway -i <inventory> --tags upload_gateway_certificates
```

To skip certificate management:

```bash
ansible-playbook itential.deployer.gateway -i <inventory> --skip-tags upload_gateway_certificates
```