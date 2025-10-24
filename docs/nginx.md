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
There are many variables that can be used to install and configure Nginx that are documented in [nginxinc.nginx](https://github.com/nginxinc/ansible-role-nginx) and 
[nginxinc.nginx_config](https://github.com/nginxinc/ansible-role-nginx-config) codebase


## Building Your Inventory

To install and configure Nginx, add `nginx` groups and hosts to
your inventory (in addition to the other Itential-related groups and hosts).

### Example Inventory - Generic Nginx load balancer 

####  This load balancer listens on port 3443 and forwards requests to port 3000 on the servers defined in backend_servers_main using sticky sessions.

```yaml
all:
  vars:
    platform_release: 6

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
        
        nginx_config_upload_ssl_enable: true
        nginx_config_upload_ssl_crt:
          - src: <path>/cert.crt
            dest: /etc/nginx/ssl/
            backup: true
        nginx_config_upload_ssl_key:
          - src: <path>/key.key
            dest: /etc/nginx/ssl/
            backup: true

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
