# Nginx Role
The Ansible playbooks and roles discussed in this section installs and configures Nginx as a load balancer using the `nginxinc.nginx_core` collection.

**&#9432; Note:**
These are optional playbooks and roles and are not required for operation of the Itential platform.

## Setup

In order to run the Nginx playbooks and roles, the `nginxinc.nginx_core` [collection](https://galaxy.ansible.com/ui/repo/published/nginxinc/nginx_core) must be
installed manually. It does not get installed automatically when the `itential.deployer` collection
is installed.

```bash
ansible-galaxy collection install nginxinc.nginx_core
```

## Roles

There are two `nginxinc.nginx_core` roles responsible for installing and configuring all of the necessary components.

[nginxinc.nginx](https://github.com/nginxinc/ansible-role-nginx) will install Nginx.

[nginxinc.nginx_config](https://github.com/nginxinc/ansible-role-nginx-config) will configure Nginx.


## Variables

### Global Variables

There are no global variables.

### Nginx Role Variables
There are many variable that can be used to install and configure Nginx that are documented in [nginxinc.nginx](https://github.com/nginxinc/ansible-role-nginx) and 
[nginxinc.nginx_config](https://github.com/nginxinc/ansible-role-nginx-config) codebase

### Install Role Variables

| Variable | Variable Type | Description | Default Value |
|----------------------------------|----------------|----------------------------------------------------------------------------------------------------------------|----------------|
| `nginx_enable` | Boolean | Enable NGINX and NGINX modules. | `true` |
| `nginx_debug_output` | Boolean | Print NGINX configuration file to terminal after executing playbook. | `false` |
| `nginx_type` | String | Specify which type of NGINX you want to install. Options are 'opensource' or 'plus'. | `opensource` |
| `nginx_version` | String | (Optional) Specify which version of NGINX you want to install. Default is to install the latest release. | Not set |
| `nginx_start` | Boolean | Start NGINX service. | `true` |
| `nginx_setup` | String | Specify whether you want to install NGINX, upgrade to the latest version, or remove NGINX. Options are 'install', 'upgrade', or 'uninstall'. | `install` |
| `nginx_manage_repo` | Boolean | Specify whether or not you want to manage the NGINX repositories. | `true` |
| `nginx_install_from` | String | Specify repository origin for NGINX Open Source. Options are 'nginx_repository', 'source' or 'os_repository'. Only works if 'nginx_type' is set to 'opensource'. | `nginx_repository` |
| `nginx_repository` | String | (Optional) Specify repository for NGINX Open Source or NGINX Plus. Only works if 'install_from' is set to 'nginx_repository' when installing NGINX Open Source. | Not set |
| `nginx_install_source_build_tools` | Boolean | Install compiler and build tools from packages when installing from source. Only applies if 'nginx_install_from' is set to 'source'. | `true` |
| `nginx_install_source_pcre` | Boolean | Install PCRE library from source (true) or package manager (false) when installing NGINX from source. | `false` |
| `nginx_install_source_openssl` | Boolean | Install OpenSSL library from source (true) or package manager (false) when installing NGINX from source. | `true` |
| `nginx_install_source_zlib` | Boolean | Install zlib library from source (true) or package manager (false) when installing NGINX from source. | `false` |
| `nginx_static_modules` | List | Static modules to compile with NGINX when installing from source. You can select any of the static modules listed on http://nginx.org/en/docs/configure.html. Default includes SSL module (DO NOT remove if you need SSL support). | `[http_ssl_module]` |
| `nginx_distribution_package` | String | (Optional) Specify NGINX package name when installing nginx from an 'os_repository'. | Not set |
| `nginx_skip_os_install_config_check` | Boolean | (Optional) Skip checking the NGINX configuration file after installation when installing NGINX from your OS repository. Not recommended unless you know what you're doing. | `false` |
| `nginx_signing_key` | String | (Optional) Choose where to fetch the NGINX signing key from. | `http://nginx.org/keys/nginx_signing.key` |
| `nginx_branch` | String | Specify which branch of NGINX Open Source you want to install. Options are 'mainline' or 'stable'. Only works if 'install_from' is set to 'nginx_repository' or 'source'. | `mainline` |
| `nginx_license.certificate` | String | Location of your NGINX Plus license certificate in your local machine. | `license/nginx-repo.crt` |
| `nginx_license.key` | String | Location of your NGINX Plus license key in your local machine. | `license/nginx-repo.key` |
| `nginx_license.jwt` | String | Location of your NGINX Plus license JWT in your local machine. Only required starting with NGINX Plus R33 and later. | `license/license.jwt` |
| `nginx_setup_license` | Boolean | Set up NGINX Plus license before installation. | `true` |
| `nginx_remove_license` | Boolean | Remove NGINX Plus license and repository after installation for security purposes. | `true` |
| `nginx_install_epel_release` | Boolean | Specify whether or not you want this role to install the EPEL package when installing NGINX OSS in some distributions and some NGINX OSS/Plus modules. | `true` |
| `nginx_modules` | List | Install NGINX Dynamic Modules. You can select any of the dynamic modules. Format is list with either the dynamic module name or a dictionary. When using a dictionary, the default value for state is present, and for version it's nginx_version if specified. | `[]` (empty list) |

### Configure Role Variables

#### Main Variables
| Variable                    | Type           | Description                                                                                       | Default Value |
|-----------------------------|----------------|---------------------------------------------------------------------------------------------------|----------------|
| nginx_config_start          | Boolean        | Start NGINX service.                                                                              | `true`         |
| nginx_config_debug_output   | Boolean        | Print NGINX configuration file to terminal after executing playbook.                              | `false`        |
| nginx_config_cleanup        | Boolean        | Remove existing NGINX configuration files (e.g., `*.conf`). Supports specifying paths or files.   | `false`        |
| nginx_config_cleanup_paths  | List (dicts)   | List of directories and recurse options to clean up old configs. *(commented out in file)*        | *None*         |
| nginx_config_cleanup_files  | List           | List of specific config files to remove. *(commented out in file)*                                | *None*         |
| nginx_config_modules        | List           | Add modules at the top of `nginx.conf`. Not needed if `nginx_config_main_template` is used.       | *None*         |


#### SE Linux Variables
| Variable                         | Variable Type | Description                                                                                                    | Default Value |
|----------------------------------|----------------|----------------------------------------------------------------------------------------------------------------|----------------|
| nginx_config_selinux             | Boolean        | Enable SELinux enforcing for NGINX (CentOS/RHEL only). You may need to open ports manually.                   | `false`        |
| nginx_config_selinux_enforcing  | Boolean        | Enforce mode if true, permissive if false (only works when `nginx_config_selinux` is true).                  | `true`         |
| nginx_config_selinux_tcp_ports  | List (Integers)| List of TCP ports to add to `http_port_t` SELinux type. (80 and 443 are included by default). *(commented)*  | *None*         |
| nginx_config_selinux_udp_ports  | List (Integers)| List of UDP ports to add to `http_port_t` SELinux type. *(commented out in file)*                            | *None*         |

#### Upload variables
| Variable | Variable Type | Description | Default Value |
|----------------------------------|----------------|----------------------------------------------------------------------------------------------------------------|----------------|
| `nginx_config_upload_enable` | Boolean | Enable uploading NGINX related files to your system. Default location of files is the files folder within the NGINX Config Ansible role. | `false` |
| `nginx_config_upload` | List | Upload NGINX config files/snippets. Each item contains src (source path, can optionally include specific file name), dest (destination path, can optionally include specific desired file name), and backup (boolean). | See example below |
| `nginx_config_upload_html_enable` | Boolean | Enable uploading HTML files to your system. | `false` |
| `nginx_config_upload_html` | List | Upload HTML files. Each item contains src (source file path), dest (destination path), and backup (boolean). | See example below |
| `nginx_config_upload_ssl_enable` | Boolean | Enable uploading SSL certificates and keys to your system. | `false` |
| `nginx_config_upload_ssl_crt` | List | Upload SSL certificates. Each item contains src (source certificate path), dest (destination path), and backup (boolean). | See example below |
| `nginx_config_upload_ssl_key` | List | Upload SSL private keys. Each item contains src (source key path), dest (destination path), and backup (boolean). | See example below |
##### Example upload list 
```yaml
nginx_config_upload:
  - src: config/snippets/
    dest: /etc/nginx/snippets
    backup: true
```
#### Template variables
There are many template variables associated with the configuration role. To view the entire list, please visit [Nginx github template file](https://github.com/nginx/ansible-role-nginx-config/blob/main/defaults/main/template.yml)

## Building Your Inventory

To install and configure Nginx, add `nginx` groups and hosts to
your inventory (in addition to the other Itential-related groups and hosts).

### Example Inventory - Generic Nginx load balancer 

####  This load balancer listens on port 3443 and forwards requests to port 3000 on the servers defined in backend_servers_main using sticky sessions.

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    nginx:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        nginx_ssl_certificate_file: <path>
        nginx_ssl_key_file: <path>
        nginx_user: <user>
        nginx_group: <group>

        # Variables for nginx installation
        nginx_setup: install
        nginx_type: opensource
        nginx_branch: stable
        nginx_service_modify: true
        nginx_service_timeout: 95
        nginx_enable: true
        nginx_start: true

        # Variables for nginx configuration 
        nginx_config_start: true
        nginx_config_debug_output: false
        nginx_config_cleanup: false
        nginx_config_selinux: true
        nginx_config_selinux_enforcing: false
        nginx_config_html_demo_template_enable: false
        nginx_config_selinux_tcp_ports:
          - 3443
        
        nginx_config_main_template_enable: true
        nginx_config_main_template:
          template_file: nginx.conf.j2
          deployment_location: /etc/nginx/nginx.conf
          backup: false
          config:
            main:
              user:
                username: nginx
                group: nginx
              worker_processes: auto
              error_log:
                file: /var/log/nginx/error.log
              pid: /run/nginx.pid
            core:
              tcp_nopush: true
              tcp_nodelay: true
              types_hash_max_size: 4096
              default_type: application/octet-stream
            events:
              worker_connections: 1024

              access: 
                - path: /var/log/nginx/access.log
            http:
              include:
                - /etc/nginx/mime.types
                - /etc/nginx/conf.d/*.conf

        nginx_config_http_template_enable: true
        nginx_config_http_template:
        - template_file: http/default.conf.j2
          deployment_location: /etc/nginx/conf.d/default.conf
          backup: false
          config:
            core:
              sendfile: true
              tcp_nopush: true
              tcp_nodelay: true
              keepalive_timeout:
                timeout: 75s
              types_hash_max_size: 1024
              default_type: application/octet-stream
              include: /etc/nginx/dynamic/upstream_main.conf
            servers:
              - core:
                  listen:
                    - port: 3443
                      ssl: true
                  access_log:
                    - path: /var/log/nginx/upstream_main.log
                      format: upstreamlog
                      buffer: 32k
                      flush: 5s
                  client_max_body_size: 50M
                ssl:
                  certificate: <path>
                  certificate_key: <path>
                locations:
                  - location: /
                    proxy:
                      pass: http://backend_servers_main
                      ssl_verify: false
                      set_header:
                        - field: Host
                          value: $host
                        - field: X-Real-IP
                          value: $remote_addr
                        - field: X-Forwarded-For
                          value: $proxy_add_x_forwarded_for
                        - field: X-Upstream-Server
                          value: $upstream_addr
            log:
              format:
                - name: main
                  escape: default
                  format: |
                    '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"'
                - name: upstreamlog
                  escape: default
                  format: |
                    '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"'

        # Upstream configuration (separate file) - contains only upstream block
        - template_file: http/default.conf.j2
          deployment_location: /etc/nginx/dynamic/upstream_main.conf
          backup: true
          config:
            upstreams:
              - name: backend_servers_main
                servers:
                  - address: <addr1>:3000
                    max_fails: 3
                    fail_timeout: 30s
                  - address: <addr2>:3000
                    max_fails: 3
                    fail_timeout: 30s
                ip_hash: true
```

## Running the Playbooks

To execute the installation and configuration of Nginx, run the `nginx` playbook:

```bash
ansible-playbook itential.deployer.nginx -i <inventory>
```

To execute the installation of Nginx, run the `nginx_install` playbook:

```bash
ansible-playbook itential.deployer.nginx_install -i <inventory>
```

To execute the configuration of nginx_configure, run the `nginx` playbook:

```bash
ansible-playbook itential.deployer.nginx_configure -i <inventory>
```
