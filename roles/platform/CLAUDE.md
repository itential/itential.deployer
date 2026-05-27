# Role: platform

## Purpose

Installs and configures Itential Platform (IAP). Handles OS user/directory setup, NodeJS installation, Python installation, RPM package installation, adapter installation, optional app artifacts, HTTPS and MongoDB client TLS certificate deployment, Vault integration, SELinux, firewalld, and service startup.

## Entry Point Tasks — main.yml

1. `validate-vars.yml` (always tagged) — validates required variables and loads release-specific vars
2. Configure OS:
   a. `create-itential-user.yml` — create `itential` user and group
   b. Create directories: `platform_server_dir`, `platform_config_dir`, `platform_log_dir`
   c. Add sudoers entry for `chroot` (required by TemplateBuilder)
   d. `configure-firewalld.yml` — open HTTP and HTTPS ports
3. Install Dependencies, Platform, Adapters, App Artifacts (notifies `Update Itential release file`):
   a. `install-platform-dependency-packages.yml` — install OS packages
   b. `install-nodejs.yml` — install NodeJS
   c. `install-python.yml` — install Python
   d. `install-platform.yml` — install IAP RPM packages
   e. `install-adapters.yml` — install configured adapters
   f. `install-app-artifacts.yml` — when `platform_app_artifacts_enabled: true`
4. `configure-selinux.yml` — apply SELinux configuration
5. `configure-vault.yml` — when `platform_configure_vault: true`
6. `copy-certs.yml` — when `platform_webserver_https_copy_certs` or `platform_mongodb_copy_certs` is true
7. `configure-platform.yml` — write `properties.json` and other config
8. `start-service.yml` — start `itential-platform` systemd service

## validate-vars.yml

- Asserts `platform_packages` is defined and contains only `.rpm` files (online installs)
- Asserts repo credentials when packages are downloaded from HTTP URLs
- Asserts `platform_release` is defined OR all individual vars (`platform_nodejs_package`, `platform_python_version`, `platform_python_packages`, `platform_python_app_dependencies`) are defined
- Asserts `platform_encryption_key` is a 64-character hex string
- Validates Vault variables when `platform_configure_vault: true`
- Validates PKI source directories when copy-certs flags are enabled
- Loads `vars/platform-release-<N>.yml` and sets release-specific defaults for NodeJS/Python when not overridden in inventory

## Key Variables

### platform.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_root_dir` | `/opt/itential/platform` | Platform install root |
| `platform_config_dir` | `/etc/itential` | Config directory |
| `platform_log_dir` | `/var/log/itential/platform` | Log directory |
| `platform_user` | `itential` | OS user running the service |
| `platform_group` | `itential` | OS group |
| `platform_package_dependencies` | `glibc-common`, `openldap`, `openldap-clients`, `openssl`, `git` | OS packages required before Platform RPM |
| `platform_encryption_key` | (required) | 64-char hex string (256-bit AES key); generate with `openssl rand -hex 32` |
| `platform_packages` | (required) | List of RPM package names or download URLs |
| `platform_app_artifacts_enabled` | `false` | Install app artifacts |
| `platform_start_service` | `true` | Start the service after install |
| `platform_upload_using_rsync` | `false` | Use rsync for artifact upload |
| `platform_delete_package_lock_file` | `true` | Delete package-lock.json before npm install |
| `platform_npm_ignore_scripts` | `true` | Skip npm scripts during install |
| `platform_certify_report_dir_remote` | `/var/tmp/itential-reports/platform` | Report dir on target |
| `platform_certify_report_dir_local` | `/tmp/itential-reports/platform` | Report dir on control node |

### server.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_server_id` | `{{ inventory_hostname }}` | Unique server identifier in multi-node deployments |
| `platform_encrypted` | `true` | Platform uses encrypted code files |
| `platform_task_worker_enabled` | `true` | Start task worker on boot |
| `platform_job_worker_enabled` | `true` | Allow jobs to start on boot |
| `platform_service_launch_timeout` | `600` | Seconds before adapter launch is considered failed |
| `platform_shutdown_timeout` | `3` | Seconds to wait before forcing shutdown |
| `platform_audit_enabled` | `false` | Enable detailed audit events |

### webserver.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_webserver_http_enabled` | `true` | Enable HTTP listener |
| `platform_webserver_http_port` | `3000` | HTTP port |
| `platform_webserver_https_enabled` | `true` | Enable HTTPS listener |
| `platform_webserver_https_port` | `3443` | HTTPS port |
| `platform_webserver_https_ciphers` | Long cipher list | Allowed TLS ciphers |
| `platform_webserver_https_secure_protocol` | `TLS_method` | OpenSSL method |
| `platform_webserver_cache_control_enabled` | `false` | HTTP cache control headers |
| `platform_webserver_timeout` | `300000` | Request timeout (ms) |

### mongodb.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_mongo_auth_enabled` | `true` | Use MongoDB auth |
| `platform_mongo_user` | `itential` | MongoDB username |
| `platform_mongo_password` | `itential` | MongoDB password (change in production) |
| `platform_mongo_db_name` | `itential` | MongoDB database name |
| `platform_mongo_url` | `mongodb://localhost:27017` | MongoDB connection string |
| `platform_mongo_tls_enabled` | `true` | Use TLS for MongoDB connection |
| `platform_mongo_tls_allow_invalid_certificates` | `false` (when TLS enabled) | Accept invalid/self-signed certs |
| `platform_mongo_bypass_version_check` | `false` | Skip MongoDB version compatibility check |

### redis.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_redis_auth_enabled` | `true` | Use Redis auth |
| `platform_redis_username` | `itential` | Redis username |
| `platform_redis_password` | `itential` | Redis password (change in production) |
| `platform_redis_host` | `localhost` | Redis host (not used when sentinels are configured) |
| `platform_redis_port` | `6379` | Redis port |
| `platform_redis_sentinels` | (empty) | List of `{host, port}` dicts for Sentinel-based HA |
| `platform_redis_sentinel_username` | `sentineluser` | Sentinel username |
| `platform_redis_sentinel_password` | `sentineluser` | Sentinel password |
| `platform_redis_name` | `itentialmaster` | Redis primary name (must match `redis_sentinel_master_name`) |
| `platform_redis_tls_enabled` | `true` | Enable TLS for both the Redis data connection and the Sentinel connection |
| `platform_redis_tls` | (empty) | TLS options dict for NodeJS Redis client |
| `platform_redis_sentinel_tls` | (empty) | TLS options dict for Sentinel connection; used when `platform_redis_tls_enabled: true` |

### pki.yml defaults (TLS paths)

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_pki_base_dir` | `/etc/pki/itential-platform` | Base PKI directory |
| `platform_pki_https_dir` | `{{ platform_pki_base_dir }}/https` | HTTPS cert subdirectory |
| `platform_pki_private_dir` | `{{ platform_pki_base_dir }}/private` | Private key subdirectory |
| `platform_mongodb_pki_dir` | `{{ platform_pki_base_dir }}/mongodb` | MongoDB client cert subdirectory |
| `platform_redis_pki_dir` | `{{ platform_pki_base_dir }}/redis` | Redis client cert subdirectory |
| `platform_webserver_https_copy_certs` | `true` | Copy HTTPS certs from control node |
| `platform_mongodb_copy_certs` | `true` | Copy MongoDB CA from control node |
| `platform_redis_copy_certs` | `true` | Copy Redis CA from control node |
| `platform_https_cert_file` | `{{ inventory_hostname }}.crt` | HTTPS cert filename |
| `platform_https_key_file` | `{{ inventory_hostname }}.key` | HTTPS key filename |
| `platform_https_ca_file` | `ca-bundle.crt` | HTTPS CA bundle filename |
| `platform_mongodb_ca_file` | `ca-bundle.crt` | MongoDB CA bundle filename |
| `platform_redis_ca_file` | `ca-bundle.crt` | Redis CA bundle filename |
| `platform_https_pki_src_dir` | `""` | HTTPS cert source dir on control node |
| `platform_mongodb_pki_src_dir` | `""` | MongoDB cert source dir on control node |
| `platform_redis_pki_src_dir` | `""` | Redis cert source dir on control node |
| `platform_redis_ca_src` | `{{ platform_redis_pki_src_dir }}/{{ platform_redis_ca_file }}` | Redis CA source path on control node |
| `platform_redis_ca_dest` | `{{ platform_redis_pki_dir }}/{{ platform_redis_ca_file }}` | Redis CA destination path on target |
| `platform_mongo_tls_ca_file` | `{{ platform_mongodb_ca_dest }}` or `""` | CA file path in properties (empty when TLS disabled) |

### authentication.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_default_user_enabled` | `true` | Enable built-in admin user |
| `platform_default_user_username` | `admin` | Default admin username |
| `platform_default_user_password` | `admin` | Default admin password (change in production) |
| `platform_auth_session_ttl` | `60` | Session timeout (minutes) |
| `platform_auth_unique_sessions_enabled` | `false` | Log out existing sessions on new login |

### vault.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_configure_vault` | `false` | Enable Vault integration |
| `platform_vault_url` | `http://localhost:8200` | Vault server URL |
| `platform_vault_auth_method` | `token` | `token` or `approle` |
| `platform_vault_token` | (required if token auth) | Vault token |
| `platform_vault_role_id` | (required if approle) | AppRole role ID |
| `platform_vault_secret_id` | (required if approle) | AppRole secret ID |
| `platform_vault_read_only` | `true` | Read-only Vault access |

### logging.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `platform_log_level` | `info` | File log level |
| `platform_log_level_console` | `warn` | Console log level |
| `platform_log_max_files` | `100` | Max rotated log files |
| `platform_log_max_file_size` | `1048576` | Max log file size (bytes; ~1 MB) |
| `platform_log_filename` | `platform.log` | Primary log filename |

## TLS Configuration

HTTPS and MongoDB client TLS are both **enabled by default** (copy-certs flags default to `true`).

**HTTPS certs** (`platform_webserver_https_copy_certs: true`):
- Source: `{{ platform_https_pki_src_dir }}/{{ inventory_hostname }}.crt` and `.key` and `ca-bundle.crt`
- Destination: `/etc/pki/itential-platform/https/` (cert, CA) and `private/` (key)
- Ownership: root:itential; private key mode 0640

**MongoDB client CA** (`platform_mongodb_copy_certs: true`):
- Source: `{{ platform_mongodb_pki_src_dir }}/ca-bundle.crt`
- Destination: `/etc/pki/itential-platform/mongodb/ca-bundle.crt`
- Used by Platform's MongoDB driver to validate the server certificate

To disable all TLS cert management:
```yaml
platform_webserver_https_copy_certs: false
platform_mongodb_copy_certs: false
platform_webserver_https_enabled: false
platform_mongo_tls_enabled: false
```

## Templates

| Template | Rendered To | Purpose |
|----------|-------------|---------|
| `6-properties.j2` | `/etc/itential/properties.json` | Main Platform properties file (MongoDB, Redis, webserver, auth, Vault, logging, etc.) |
| `itential-platform.service.j2` | `/etc/systemd/system/itential-platform.service` | Systemd unit for Platform |
| `iag_adapter_service_config.j2` | IAG adapter config path | IAG adapter service configuration |
| `platform.preflight.j2` | Used by `preflight.yml` | Pre-install checklist output |
| `platform-validation-report.md.j2` | `platform_certify_report_dir_remote/<host>.md` | Certification report |

## Handlers

| Handler | Listen String | Action |
|---------|--------------|--------|
| Enable and Start Platform | `restart itential-platform` | `systemctl restart itential-platform` (only when `platform_start_service: true`) |
| Update Itential release file | (separate notify) | Includes `update-release-file.yml` |

## Inventory Groups

| Group | Description |
|-------|-------------|
| `platform` | Primary Platform nodes |
| `platform_secondary` | Secondary Platform nodes (same role applied) |

Both groups receive the same role. The `platform_server_id` defaults to `inventory_hostname` to uniquely identify each node in a multi-node deployment.

## Release-Specific Vars (vars/platform-release-6.yml)

| Variable | RHEL 8 | RHEL 9 / AL2023 |
|----------|--------|-----------------|
| `platform_nodejs_package` | `@nodejs:20/common` | `@nodejs:20` / `nodejs20` |
| `platform_python_version` | `3.11` | `3.11` |
| `platform_python_packages` | `python3.11`, `python3.11-pip` | same |
| `platform_python_app_dependencies` | `jinja2==3.1.2`, `markupsafe==2.1.4`, `textfsm==1.1.3` | same |

Hardware specs for `verify` playbook (`platform_hw_specs`):
- dev: 8 CPU, 32 GB RAM, 250 GB disk
- test/prod: 16 CPU, 64 GB RAM, 250 GB disk

## Dependencies / Assumptions

- MongoDB and Redis must be running and accessible before Platform starts.
- `platform_encryption_key` is a mandatory 64-char hex string. The validate-vars task fails fast if missing or malformed.
- `platform_packages` must be either local RPM filenames (relative to `playbook_dir/files/`) or full HTTP/HTTPS URLs. Mixed lists are not supported.
- When using repository download (`gateway_archive_download_url`-style for Platform), set `repository_username`/`repository_password` or `repository_api_key`.

## Certify Behavior (certify-platform.yml)

`certify-platform.yml` runs on all hosts in `platform*` (both `platform` and `platform_secondary`). Each host produces its own report.

**Connectivity checks:** The HTTP and HTTPS health endpoint tasks use `failed_when: false` and return without a `.json` attribute when Platform is down or not yet listening. The downstream MongoDB and Redis connectivity `set_fact` tasks are guarded by `platform_http_health_check.json is defined` and `platform_https_health_check.json is defined`. When Platform is unreachable, connectivity flags remain `false` (initialized earlier) rather than crashing the play.

**Redis TLS for Platform:** Platform requires its own Redis CA cert at `platform_redis_ca_dest` when `platform_redis_tls_enabled: true`. Set `platform_redis_pki_src_dir` in the inventory to enable cert copy. Without it, `platform.properties` will have `redis_tls` commented out and Platform will fail to connect to a TLS-only Redis.

**Multi-host:** The play runs on `hosts: platform*`, so all Platform nodes are certified in parallel. Each host is checked independently using its own `inventory_hostname` and `ansible_host`.

## Gotchas

- The `platform_server_dir` and `platform_services_dir` are derived from `platform_root_dir` and cannot be independently overridden via inventory — only `platform_root_dir` can be changed.
- `platform_start_service: false` prevents service startup but the handler still fires if notified — the `when: platform_start_service | bool` condition is on the handler itself.
- The sudoers entry for `chroot` is appended to `/etc/sudoers` with `lineinfile`. If the file has a `Defaults requiretty` directive, the entry will still be added but may not work correctly.
- `platform_mongo_tls_ca_file` resolves to `platform_mongodb_ca_dest` when `platform_mongo_tls_enabled: true` and to `""` when disabled. The template uses this variable directly, so changing `platform_mongo_tls_enabled` without setting this var correctly will cause a broken properties file.
- When `platform_redis_sentinels` is set, `platform_redis_host` is ignored by the Platform Redis client. Set `platform_redis_name` to match the sentinel master name used in the Redis role (`redis_sentinel_master_name`, default: `itentialmaster`).
