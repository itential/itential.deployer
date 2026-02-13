# Gateway Roles

The playbook and role in this section install and configure the Itential Automation Gateway (IAG).

## Roles

### Gateway Role

The `gateway` role performs a base install of IAG including any OS packages required. It includes
the appropriate versions of Python, Pip, and Ansible. It creates the appropriate Linux users,
directories, log files, and systemd services. It will start the automation-gateway service when
complete.

## Variables

### Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time based on the IAG release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

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

The following table lists the default variables located in `roles/gateway/defaults/main.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `gateway_enable_ansible` | Boolean | Flag to enable Ansible. | `true` |
| `gateway_enable_nornir` | Boolean | Flag to enable Nornir. | `true` |
| `gateway_enable_netmiko` | Boolean | Flag to enable Netmiko. | `true` |
| `gateway_enable_scripts` | Boolean | Flag to enable scripts. | `true` |
| `gateway_enable_httpreq` | Boolean | Flag to enable HTTP requests. | `true` |
| `gateway_enable_netconf` | Boolean | Flag to enable Netconf requests. | `true` |
| `gateway_enable_python_venv` | Boolean | Flag to enable Python virtual environments. | `true` |
| `gateway_enable_grpc` | Boolean | Flag to enable GRPC requests. | `true` |
| `gateway_enable_git` | Boolean | Flag to enable Git integration. | `true` |
| `gateway_install_dir` | String |  The base directory where to install the IAG files. | `/opt/automation-gateway` |
| `gateway_data_dir` | String | The IAG data directory. | `/opt/automation-gateway` |
| `gateway_log_dir` | String | The IAG log directory. | `/var/log/automation-gateway` |
| `gateway_port` | Integer | The IAG HTTP listen port. | `8083` |
| `gateway_properties_location` | String | The location of the IAG configuration file. | `/etc/automation-gateway` |
| `gateway_user` | String | The IAG Linux user. | `itential` |
| `gateway_group` | String | The IAG Linux group. | `itential` |
| `gateway_https` | Boolean | Flag to enable HTTPS. | `false` |
| `gateway_https_port` | Integer | The IAG HTTPS listen port. | `8443` |
| `gateway_ssl_copy_certs` | Boolean | Flag to enable copying the IAG SSL certificate. | `true` |
| `gateway_ssl_dir` | String | The IAG SSL directory. | `{{ gateway_install_dir }}/conf/certs` |
| `gateway_ssl_cert_src` | String | The SSL cert file. | `server.crt` |
| `gateway_ssl_cert_dest` | String | The SSL cert destination. | `{{ gateway_ssl_dir }}/{{ gateway_ssl_cert_src }}` |
| `gateway_ssl_key_src` | String | The SSL key file. | `server.key` |
| `gateway_ssl_key_dest` | String | The SSL key file destination. | `{{ gateway_ssl_dir }}/{{ gateway_ssl_key_src }}` |
| `gateway_ssl_rootca_src` | String | The SSL root CA file. | `rootCA.crt` |
| `gateway_ssl_rootca_dest` | String | The SSL root CA destination. | `{{ gateway_ssl_dir }}/{{ gateway_ssl_rootca_src }}` |
| `gateway_tlsv1_2` | Boolean | Flag to enable TLS 1.2. | `false` |
| `gateway_http_server_threads` | Integer | The number of http server threads for handling requests. | `{{ ansible_processor_cores * 4 }}` |

## Configuring HTTPS

The Gateway role supports configuring Native HTTPS. The Gateway role does not generate SSL certificates.

To configure IAG Native HTTPS:

* Required
  * Set `gateway_https` to `true` in the inventory.
  * Place the SSL certs and keys in either the playbook or role `files` directory.
* Optional
  * Set SSL-related variables from `roles/gateway/defaults/main.yml` in the inventory.

## Building the Inventory

To install and configure IAG, add a `gateway` group and host(s) to your inventory and configure the
`gateway_release` and `gateway_whl_file`.

## Example Inventory - Single IAG Node

```yaml
all:
  children:
    gateway:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        gateway_release: 4.3
        gateway_whl_file: <wheel-file>
```

To configure IAG Native HTTPS, add the `gateway_https` flag to the `gateway` group and set it to
`true` and configure the SSL-related variables (optional).

## Example Inventory - IAG Native SSL

```yaml
all:
  children:
    gateway:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        gateway_release: 4.3
        gateway_whl_file: <wheel-file>
        gateway_https: true
```

## Running the Playbook

To execute the Gateway role, run the `gateway` playbook:

```bash
ansible-playbook itential.deployer.gateway -i <inventory>
```
