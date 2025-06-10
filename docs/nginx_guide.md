# Nginx Role

This Ansible role configures Nginx as a load balancer using the `nginxinc.nginx_core` collection.

**&#9432; Note:**
These are optional playbooks and roles and are not required for operation of the Itential platform.

## Setup

In order to run the Nginx playbooks and roles, the `nginxinc.nginx` collection must be
installed manually. It does not get installed automatically when the `itential.deployer` collection
is installed.

```bash
ansible-galaxy role install nginxinc.nginx
```

## Variables

### Global Variables

There are no global variables.

### Nginx Role Variables


| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `nginx_type` | String |Type of Nginx installation | `opensource` |
| `nginx_branch` | String | Nginx branch to install | `mainline` |
| `nginx_lb_method` | String | Load balancing method | `least_conn` |
| `nginx_lb_keepalive` | Integer | Number of idle keepalive connections to upstream servers | `65` |
| `nginx_vhost_domain` | String | Domain or subdomain configured for the virtual host | `itential` |
| `nginx_vhost_port` | Integer | Port number on which the virtual host listens for HTTP traffic | `3000` |
| `nginx_vhost_ssl_port` | Integer | Port number used for HTTPS traffic (SSL/TLS) | `3443` |
| `nginx_enable_ssl` | Boolean | enables/disables SSL support | `false` |
| `nginx_ssl_certificate` | String | Path to the SSL certificate file (when nginx_enable_ssl is true) | `/etc/ssl/certs/nginx.crt` |
| `nginx_ssl_certificate_key` | String | Path to the SSL certificate’s private key (when nginx_enable_ssl is true) | `/etc/ssl/private/nginx.key` |
| `nginx_ssl_protocols` | String | Allowed SSL/TLS versions | `TLSv1.2 TLSv1.3` |
| `nginx_ssl_ciphers` | String | List of acceptable SSL ciphers | `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384` |
| `nginx_health_check_enabled` | Boolean | Enables health checks for backend services | `false` |
| `nginx_health_check_path` | String |URI path used to perform the health check | `/health` |
| `nginx_access_log` | String | File path where HTTP access logs are writte | `/var/log/nginx/access.log` |
| `nginx_error_log` | String |File path where Nginx error logs are written | `/var/log/nginx/error.log` |
| `nginx_log_level` | String |Verbosity of error logging (debug, info, notice, warn, error, crit, alert, emerg) | `warn` |




## Building Your Inventory

To install and configure Nginx, add `nginx` groups and hosts to
your inventory (in addition to the other Itential-related groups and hosts).

### Example Inventory - Generic load balancer

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    nginx:
      hosts:
        <host1>:
          ansible_host: <nginx_ip_addr>
      vars:
        nginx_backend_servers:
          - name: <backend_host_addr1>
            address: <backend_ip_addr1>
            port: <backend_port1>
          - name: <backend_host_addr2>
            address: <backend_ip_addr2>
            port: <backend_port2>
        nginx_vhost_port: <nginx_listening port>
```

### Example Inventory - SSL load balancer
```yaml
all:
  vars:
    platform_release: 6.0

  children:
    nginx:
      hosts:
        <host1>:
          ansible_host: <nginx_ip_addr>
      vars:
        nginx_backend_servers:
          - name: <backend_host_addr1>
            address: <backend_ip_addr1>
            port: <backend_port1>
          - name: <backend_host_addr2>
            address: <backend_ip_addr2>
            port: <backend_port2>
        nginx_vhost_ssl_port: <nginx_listening port>
```

## Running the Playbooks

To execute the installation of Prometheus, Grafana and all the exporters, run the `prometheus_site` playbook:

```bash
ansible-playbook itential.deployer.nginx -i <inventory>
```
