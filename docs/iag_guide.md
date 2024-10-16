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
| `iag_release` | `gateway` | Fixed-point | Designates which major release version of IAG to install. | N/A | Yes
| `iag_whl_file` | `gateway` | String | The name of the IAG wheel file to install. | N/A | Yes
| `gateway_download_url` | `platform` | String | The URL for the download of the iag whl file from a repository. | N/A | Yes*
| `repository_username` | `platform` | String | The username for authentication of the repository from gateway_download_url. | N/A | No
| `repository_password` | `platform` | String | The password for authentication of the repository from gateway_download_url. | N/A | No
| `repository_api_key` | `platform` | String | The API for authentication of the repository from gateway_download_url. Can be used instead of username/password for authentication.| N/A | No
| `repository_encrypted_file` | `platform` | String | Path to an ansible vault encrypted file containing credentials for the file downloads.| N/A | No

Both the `iag_release` and `iag_whl_file` must be configured in the inventory.

The following table lists the default variables located in `roles/gateway/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `iag_enable_ansible` | `gateway` | Boolean | Flag to enable Ansible. | `true`
| `iag_enable_nornir` | `gateway` | Boolean | Flag to enable Nornir. | `true`
| `iag_enable_netmiko` | `gateway` | Boolean | Flag to enable Netmiko. | `true`
| `iag_enable_scripts` | `gateway` | Boolean | Flag to enable scripts. | `true`
| `iag_enable_httpreq` | `gateway` | Boolean | Flag to enable HTTP requests. | `true`
| `iag_enable_netconf` | `gateway` | Boolean | Flag to enable Netconf requests. | `true`
| `iag_enable_python_venv` | `gateway` | Boolean | Flag to enable Python virtual environments. | `true`
| `iag_enable_grpc` | `gateway` | Boolean | Flag to enable GRPC requests. | `true`
| `iag_enable_git` | `gateway` | Boolean | Flag to enable Git integration. | `true`
| `iag_install_dir` | `gateway` | String |  The base directory where to install the IAG files. | `/opt/automation-gateway`
| `iag_data_dir` | `gateway` | String | The IAG data directory. | `/opt/automation-gateway`
| `iag_log_dir` | `gateway` | String | The IAG log directory. | `/var/log/automation-gateway`
| `iag_port` | `gateway` | Integer | The IAG HTTP listen port. | `8083`
| `iag_properties_location` | `gateway` | String | The location of the IAG configuration file. | `/etc/automation-gateway`
| `iag_user` | `gateway` | String | The IAG Linux user. | `itential`
| `iag_group` | `gateway` | String | The IAG Linux group. | `itential`
| `iag_https` | `gateway` | Boolean | Flag to enable HTTPS. | `false`
| `iag_https_port` | `gateway` | Integer | The IAG or HAProxy HTTPS listen port. | `8443`
| `iag_ssl_copy_certs` | `gateway` | Boolean | Flag to enable copying the IAG SSL certificate. | `true`
| `iag_ssl_dir` | `gateway` | String | The IAG SSL directory. | `{{ iag_install_dir }}/conf/certs`
| `iag_ssl_cert_src` | `gateway` | String | The SSL cert file. | `server.crt`
| `iag_ssl_cert_dest` | `gateway` | String | The SSL cert destination. | `{{ iag_ssl_dir }}/{{ iag_ssl_cert_src }}`
| `iag_ssl_key_src` | `gateway` | String | The SSL key file. | `server.key`
| `iag_ssl_key_dest` | `gateway` | String | The SSL key file destination. | `{{ iag_ssl_dir }}/{{ iag_ssl_key_src }}`
| `iag_ssl_rootca_src` | `gateway` | String | The SSL root CA file. | `rootCA.crt`
| `iag_ssl_rootca_dest` | `gateway` | String | The SSL root CA destination. | `{{ iag_ssl_dir }}/{{ iag_ssl_rootca_src }}`
| `iag_tlsv1_2` | `gateway` | Boolean | Flag to enable TLS 1.2. | `false`
| `iag_http_server_threads` | `gateway` | Integer | The number of http server threads for handling requests. | `{{ ansible_processor_cores * 4 }}`

## Gateway HAProxy Role Variables

The variables in this section may be overridden in the inventory in the `gateway` group vars.

The following table lists the default variables located in `roles/gateway_haproxy/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `iag_haproxy` | `gateway` | Boolean | Flag to enable HAProxy. | `false`
| `haproxy_conf_file` | `gateway` | String | The location of the HAProxy configuration file. | `/etc/haproxy/haproxy.cfg`
| `haproxy_ssl_cert_src` | `gateway` | String | The HAProxy SSL certificate file. | `server.pem`
| `haproxy_ssl_cert_dest` | `gateway` | String | The HAProxy SSL certificate destination. | `"/etc/ssl/certs{{ haproxy_ssl_cert_src }}"`

# Configuring HTTPS

The Gateway roles support two methods for configuring HTTPS - IAG Native HTTPS and HTTPS via HAProxy.  The Gateway roles do not generate SSL certificates.

## IAG Native HTTPS

To configure IAG Native HTTPS:

* Required
  - Set `iag_https` to `true` in the inventory.
  - Place the SSL certs and keys in either the playbook or role `files` directory.
  - Do not configure `iag_haproxy` in the inventory so HTTPS via HAProxy does not get installed.
* Optional
  - Set SSL-related variables from `roles/gateway/defaults/main.yml` in the inventory.

## HTTPS Via HAProxy

To configure HTTPS via HAProxy:

* Required
  - Set `iag_haproxy` to `true` in the inventory.
  - Place the SSL certificate (PEM file) in either the playbook or role `files` directory.
  - Do not configure `iag_https` in the inventory so IAG Native HTTPS does not get configured.
* Optional
  - Set the `haproxy_ssl_cert_src` and `haproxy_ssl_cert_dest` variables in the inventory.

 Itential does not attempt to create any HTTPS certificates. These must be
 created independently. When they are included in the appropriate location
 the installer will ensure that they get uploaded to the correct location.

# Building the Inventory

To install and configure IAG, add a `gateway` group and host(s) to your inventory and configure the `iag_release` and `iag_whl_file`.

## Example Inventory - Single IAG Node

```
all:
    children:
        gateway:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                iag_release: 2023.1
                iag_whl_file: <wheel-file>
```

To configure IAG Native HTTPS, add the `iag_https` flag to the `gateway` group and set it to `true` and configure the SSL-related variables (optional).

## Example Inventory - IAG Native SSL

```
all:
    children:
        gateway:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                iag_release: 2023.1
                iag_whl_file: <wheel-file>
                iag_https: true
```

To configure HTTPS via HAProxy, add the `iag_haproxy` flag to the `gateway` group and set it to `true`.

## Example Inventory - IAG SSL Via HAProxy

```
all:
    children:
        gateway:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                iag_release: 2023.1
                iag_whl_file: <wheel-file>
                iag_haproxy: true
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
