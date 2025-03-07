# Overview

The playbook and roles in this section install and configure the Itential Automation Gateway (IAG).  There are currently two IAG-related roles:

* `gateway` – Installs IAG and performs a base configuration.
* `gateway_haproxy` – Installs and configures HAProxy.

# Roles

## Gateway Role

The `gateway` role performs a base install of IAG including any OS packages required. It includes the appropriate versions of Python, Pip, and Ansible. It creates the appropriate Linux users, directories, log files, and systemd services. It will start the automation-gateway service when complete.

## Gateway HAProxy Role

The `gateway_haproxy` role will install and configure an HAProxy instance as an HTTPS proxy for IAG.

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time based on the IAG release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Gateway Role Variables

The variables in this section may be overridden in the inventory in the `gateway` group vars.

| Variable | Group | Type | Description | Default Value | Required?
| :------- | :---- | :--- | :---------- | :------------ | :--------
| `gateway_release` | `gateway` | Fixed-point | Designates which major release version of IAG to install. | N/A | Yes
| `gateway_whl_file` | `gateway` | String | The name of the IAG wheel file to install. | N/A | Yes*
| `gateway_archive_download_url` | `gateway` | String | The URL for the download of the iag whl file from a repository. | N/A | Yes*
| `repository_username` | `gateway` | String | The username for authentication of the repository from gateway_archive_download_url. | N/A | No
| `repository_password` | `gateway` | String | The password for authentication of the repository from gateway_archive_download_url. | N/A | No
| `repository_api_key` | `gateway` | String | The API for authentication of the repository from gateway_archive_download_url. Can be used instead of username/password for authentication.| N/A | No

The `gateway_release` and either `gateway_whl_file` or `gateway_archive_download_url` must be configured in the inventory.
When `gateway_archive_download_url` is configured, the `repository_username`/`repository_password` or `repository_api_key` must be defined.

The following table lists the default variables located in `roles/gateway/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `gateway_enable_ansible` | `gateway` | Boolean | Flag to enable Ansible. | `true`
| `gateway_enable_nornir` | `gateway` | Boolean | Flag to enable Nornir. | `true`
| `gateway_enable_netmiko` | `gateway` | Boolean | Flag to enable Netmiko. | `true`
| `gateway_enable_scripts` | `gateway` | Boolean | Flag to enable scripts. | `true`
| `gateway_enable_httpreq` | `gateway` | Boolean | Flag to enable HTTP requests. | `true`
| `gateway_enable_netconf` | `gateway` | Boolean | Flag to enable Netconf requests. | `true`
| `gateway_enable_python_venv` | `gateway` | Boolean | Flag to enable Python virtual environments. | `true`
| `gateway_enable_grpc` | `gateway` | Boolean | Flag to enable GRPC requests. | `true`
| `gateway_enable_git` | `gateway` | Boolean | Flag to enable Git integration. | `true`
| `gateway_install_dir` | `gateway` | String |  The base directory where to install the IAG files. | `/opt/automation-gateway`
| `gateway_data_dir` | `gateway` | String | The IAG data directory. | `/opt/automation-gateway`
| `gateway_log_dir` | `gateway` | String | The IAG log directory. | `/var/log/automation-gateway`
| `gateway_port` | `gateway` | Integer | The IAG HTTP listen port. | `8083`
| `gateway_properties_location` | `gateway` | String | The location of the IAG configuration file. | `/etc/automation-gateway`
| `gateway_user` | `gateway` | String | The IAG Linux user. | `itential`
| `gateway_group` | `gateway` | String | The IAG Linux group. | `itential`
| `gateway_https` | `gateway` | Boolean | Flag to enable HTTPS. | `false`
| `gateway_https_port` | `gateway` | Integer | The IAG or HAProxy HTTPS listen port. | `8443`
| `gateway_ssl_copy_certs` | `gateway` | Boolean | Flag to enable copying the IAG SSL certificate. | `true`
| `gateway_ssl_dir` | `gateway` | String | The IAG SSL directory. | `{{ gateway_install_dir }}/conf/certs`
| `gateway_ssl_cert_src` | `gateway` | String | The SSL cert file. | `server.crt`
| `gateway_ssl_cert_dest` | `gateway` | String | The SSL cert destination. | `{{ gateway_ssl_dir }}/{{ gateway_ssl_cert_src }}`
| `gateway_ssl_key_src` | `gateway` | String | The SSL key file. | `server.key`
| `gateway_ssl_key_dest` | `gateway` | String | The SSL key file destination. | `{{ gateway_ssl_dir }}/{{ gateway_ssl_key_src }}`
| `gateway_ssl_rootca_src` | `gateway` | String | The SSL root CA file. | `rootCA.crt`
| `gateway_ssl_rootca_dest` | `gateway` | String | The SSL root CA destination. | `{{ gateway_ssl_dir }}/{{ gateway_ssl_rootca_src }}`
| `gateway_tlsv1_2` | `gateway` | Boolean | Flag to enable TLS 1.2. | `false`
| `gateway_http_server_threads` | `gateway` | Integer | The number of http server threads for handling requests. | `{{ ansible_processor_cores * 4 }}`

## Gateway HAProxy Role Variables

The variables in this section may be overridden in the inventory in the `gateway` group vars.

The following table lists the default variables located in `roles/gateway_haproxy/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `gateway_haproxy_enabled` | `gateway` | Boolean | Flag to enable HAProxy. | `false`
| `gateway_haproxy_conf_file` | `gateway` | String | The location of the HAProxy configuration file. | `/etc/haproxy/haproxy.cfg`
| `gateway_haproxy_ssl_cert_src` | `gateway` | String | The HAProxy SSL certificate file. | `server.pem`
| `gateway_haproxy_ssl_cert_dest` | `gateway` | String | The HAProxy SSL certificate destination. | `"/etc/ssl/certs{{ gateway_haproxy_ssl_cert_src }}"`

# Configuring HTTPS

The Gateway roles support two methods for configuring HTTPS - IAG Native HTTPS and HTTPS via HAProxy.  The Gateway roles do not generate SSL certificates.

## IAG Native HTTPS

To configure IAG Native HTTPS:

* Required
  - Set `gateway_https` to `true` in the inventory.
  - Place the SSL certs and keys in either the playbook or role `files` directory.
  - Do not configure `gateway_haproxy_enabled` in the inventory so HTTPS via HAProxy does not get installed.
* Optional
  - Set SSL-related variables from `roles/gateway/defaults/main.yml` in the inventory.

## HTTPS Via HAProxy

To configure HTTPS via HAProxy:

* Required
  - Set `gateway_haproxy_enabled` to `true` in the inventory.
  - Place the SSL certificate (PEM file) in either the playbook or role `files` directory.
  - Do not configure `gateway_https` in the inventory so IAG Native HTTPS does not get configured.
* Optional
  - Set the `gateway_haproxy_ssl_cert_src` and `gateway_haproxy_ssl_cert_dest` variables in the inventory.

 Itential does not attempt to create any HTTPS certificates. These must be
 created independently. When they are included in the appropriate location
 the installer will ensure that they get uploaded to the correct location.

# Building the Inventory

To install and configure IAG, add a `gateway` group and host(s) to your inventory and configure the `gateway_release` and `gateway_whl_file`.

## Example Inventory - Single IAG Node

```
all:
    children:
        gateway:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                gateway_release: 2023.1
                gateway_whl_file: <wheel-file>
```

To configure IAG Native HTTPS, add the `gateway_https` flag to the `gateway` group and set it to `true` and configure the SSL-related variables (optional).

## Example Inventory - IAG Native SSL

```
all:
    children:
        gateway:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                gateway_release: 2023.1
                gateway_whl_file: <wheel-file>
                gateway_https: true
```

To configure HTTPS via HAProxy, add the `gateway_haproxy_enabled` flag to the `gateway` group and set it to `true`.

## Example Inventory - IAG SSL Via HAProxy

```
all:
    children:
        gateway:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                gateway_release: 2023.1
                gateway_whl_file: <wheel-file>
                gateway_haproxy_enabled: true
```

# Running the Playbook

To execute all Gateway roles, run the `gateway` playbook:

```
ansible-playbook itential.deployer.gateway -i <inventory>
```

You can also run select IAG roles by using the following tags:

* `gateway_install`
* `gateway_haproxy`

To execute only the `gateway` role, run the `itential.deployer.gateway` playbook with the `gateway_install` tag:

```
ansible-playbook itential.deployer.gateway -i <inventory> --tags gateway_install
```

To execute only the `gateway_haproxy` role, run the `itential.deployer.gateway` playbook with the `gateway_haproxy` tag:

```
ansible-playbook itential.deployer.gateway -i <inventory> --tags gateway_haproxy
```
