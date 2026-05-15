# Role: mongodb

## Purpose

Installs and configures MongoDB for use with Itential Platform. Handles single-node and replica set deployments, user creation, authentication, TLS, kernel tuning, SELinux policy modules, NUMA configuration, logrotate, and firewalld port opening.

## Entry Point Tasks — main.yml

1. `validate-vars.yml` (always tagged) — validates required variables
2. Set node type facts: `mongodb_is_primary_node`, `mongodb_is_replica_node`, `mongodb_data_nodes`
3. `install-mongodb.yml` — full install sequence (notifies `Update Itential release file` handler)
4. `configure-mongodb.yml` — conditional configuration (skipped if auth, TLS, and replication are all disabled)
5. Assert `mongod` service is `active`

## install-mongodb.yml Sequence

1. Install MongoDB packages (online: adds MongoDB YUM repo then `dnf install`; offline: `offline/install-rpms`)
2. Pin MongoDB in `/etc/dnf/dnf.conf` with `exclude=mongodb-org*`
3. Create `mongodb_data_dir`, `mongodb_log_dir`, `mongodb_pid_dir`
4. Install Python (for `community.mongodb` collection)
5. Configure Transparent Huge Pages (THP): disable for MongoDB < 8.0; enable + tune for >= 8.0
6. Adjust kernel parameters (`sysctl`)
7. Configure SELinux (when enforcing) via the `selinux` role
8. Configure logrotate
9. Configure NUMA
10. Open firewalld port `mongodb_port/tcp`
11. Write initial `mongod.conf` with `stage: initialize` (auth/TLS/replication forced off)
12. Start `mongod`
13. Use `itential.deployer.mongodb_config_state` module to discover current auth/replication state
14. Create `admin`, `itential`, and optionally `monitor` database users (runs only on `mongodb_primary[0]`)

## configure-mongodb.yml Sequence

Conditionally includes (in order):

1. `configure-mongodb-replicaset.yml` — when `mongodb_replica` group has members
2. `configure-mongodb-auth.yml` — when `mongodb_auth_enabled`
3. `configure-mongodb-tls.yml` — when `mongodb_tls_enabled`

## Key Variables

### mongodb.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `mongodb_conf_file` | `/etc/mongod.conf` | Path to mongod config |
| `mongodb_data_dir` | `/var/lib/mongo` | Data directory |
| `mongodb_log_dir` | `/var/log/mongodb` | Log directory |
| `mongodb_pid_dir` | `/var/run/mongodb` | PID directory |
| `mongodb_owner` | `mongod` | OS user/group for MongoDB files |
| `mongodb_group` | `mongod` | OS group |
| `mongodb_port` | `27017` | Listen port |
| `mongodb_bind_addrs` | `127.0.0.1` | Bind addresses (inventory_hostname and optionally `::1` added automatically) |
| `mongodb_bind_ipv6` | `true` | Add `::1` to bind addresses |
| `mongodb_auth_enabled` | `true` | Enable MongoDB authentication |
| `mongodb_tls_enabled` | `true` | Enable TLS |
| `mongodb_tls_copy_certs` | `true` | Copy certs from control node to target |
| `mongodb_replication_enabled` | `false` | Enable replica set configuration |
| `mongodb_replset_name` | `rs0` | Replica set name |
| `mongodb_user_admin` | `admin` | Admin user name |
| `mongodb_user_itential` | `itential` | App user name |
| `mongodb_user_admin_password` | `admin` | Admin password (change in production) |
| `mongodb_user_itential_password` | `itential` | App password (change in production) |
| `mongodb_user_monitor_password` | `monitor` | Monitor user password |
| `mongodb_monitor_user_enabled` | `false` | Create the monitor user |
| `mongodb_primary_priority` | `10` | Replica priority for `mongodb_primary` group hosts |
| `mongodb_replica_priority` | `5` | Default replica priority for `mongodb_replica` group hosts |
| `mongodb_certify_report_dir_remote` | `/var/tmp/itential-reports/mongodb` | Report dir on target |
| `mongodb_certify_report_dir_local` | `/tmp/itential-reports/mongodb` | Report dir on control node |

### kernel_params.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `mongodb_sysctl_file` | `/etc/sysctl.d/98-mongodb.conf` | Sysctl config file path |
| `mongodb_net_ipv4_tcp_keepalive_time` | `300` | TCP keepalive |
| `mongodb_net_core_somaxconn` | `65535` | Max socket connections |
| `mongodb_vm_zone_reclaim_mode` | `0` | NUMA zone reclaim mode |
| `mongodb_vm_swappiness` | `1` | VM swappiness |
| `mongodb_vm_max_map_count` | `262144` | Max memory map areas |

### install.yml defaults (runtime-computed)

| Variable | Default | Purpose |
|----------|---------|---------|
| `mongodb_python_executable` | `/usr/bin/python3` | System Python |
| `mongodb_pip_executable` | `/usr/bin/pip3` | System pip |
| `mongodb_python_venv` | `/usr/local/lib/mongodb_venv` | Python venv for `community.mongodb` |
| `mongodb_mongod_service_retries` | `5` | Retries when starting mongod |
| `mongodb_mongod_service_delay` | `10` | Seconds between retries |

### pki.yml defaults (TLS paths)

| Variable | Default | Purpose |
|----------|---------|---------|
| `mongodb_pki_base_dir` | `/etc/pki/mongodb` | Base PKI directory |
| `mongodb_pki_private_dir` | `{{ mongodb_pki_base_dir }}/private` | Private key subdirectory |
| `mongodb_tls_server_cert_file` | `{{ inventory_hostname }}.pem` | Combined cert+key PEM filename |
| `mongodb_tls_ca_file` | `ca-bundle.crt` | CA bundle filename |
| `mongodb_auth_key_file` | `replica.key` | Replica set keyfile filename |
| `mongodb_tls_cert_dest` | `{{ mongodb_pki_base_dir }}/{{ mongodb_tls_server_cert_file }}` | Cert destination on target |
| `mongodb_tls_ca_dest` | `{{ mongodb_pki_base_dir }}/{{ mongodb_tls_ca_file }}` | CA destination on target |
| `mongodb_auth_key_dest` | `{{ mongodb_pki_private_dir }}/{{ mongodb_auth_key_file }}` | Keyfile destination on target |
| `mongodb_pki_src_dir` | `""` | Source directory on control node (must be set in inventory when TLS enabled) |
| `mongodb_tls_cert_src` | `{{ mongodb_pki_src_dir }}/{{ mongodb_tls_server_cert_file }}` | Cert source |
| `mongodb_tls_ca_src` | `{{ mongodb_pki_src_dir }}/{{ mongodb_tls_ca_file }}` | CA source |

## TLS Configuration

TLS is **enabled by default** (`mongodb_tls_enabled: true`, `mongodb_tls_copy_certs: true`).

Flow (`configure-mongodb-tls.yml`):
1. When `mongodb_tls_copy_certs: true`: create PKI directories, then call `copy-certs.yml` to copy cert files from `mongodb_pki_src_dir` on the control node
2. Write `mongod.conf` with `stage: tls` (enables TLS settings in the template)
3. Flush handlers (restarts mongod immediately with TLS config)

**`mongodb_pki_src_dir` must be set in inventory** when `mongodb_tls_copy_certs: true`. The cert file is `<inventory_hostname>.pem` (combined cert + key in PEM format) — MongoDB requires a single PEM with both. The replica keyfile (`replica.key`) is only needed when `mongodb_replication_enabled: true`.

To disable TLS (e.g., AIO dev environments):
```yaml
mongodb_tls_enabled: false
mongodb_tls_copy_certs: false
```

## Templates

| Template | Rendered To | Purpose |
|----------|-------------|---------|
| `mongod.conf.j2` | `/etc/mongod.conf` | Main mongod configuration; rendered multiple times with different `stage` values (`initialize`, `auth`, `tls`) |
| `mongod.logrotate.j2` | `/etc/logrotate.d/mongod` | Logrotate configuration |
| `thp.service.j2` | `/etc/systemd/system/thp.service` | Systemd service to set THP state on boot (only for MongoDB < 8.0) |
| `tuned.conf.j2` | `/etc/tuned/mongodb/tuned.conf` | Tuned profile for MongoDB |
| `mongodb.preflight.j2` | Used by `preflight.yml` | Pre-install checklist output |
| `mongodb-validation-report.md.j2` | `mongodb_certify_report_dir_remote/<host>.md` | Certification report |

## Handlers

| Handler | Trigger | Action |
|---------|---------|--------|
| `restart mongod` | `notify: restart mongod` | `systemctl restart mongod` |
| `Update Itential release file` | `notify: Update Itential release file` | Includes `update-release-file.yml` to write component version to `/etc/itential-release` |

## Inventory Groups

| Group | Nodes |
|-------|-------|
| `mongodb_primary` | Primary data node (required) |
| `mongodb_replica` | Secondary data nodes (optional) |
| `mongodb_arbiter` | Arbiter nodes (optional) |
| `mongodb` | All of the above (used in the `mongodb.yml` playbook host target) |

The `mongodb_primary[0]` host runs user creation tasks. All hosts in `mongodb_primary` get `mongodb_is_primary_node: true` and priority `mongodb_primary_priority`.

## Release-Specific Vars (vars/platform-release-6.yml)

| Variable | RHEL 8/9/2023 default |
|----------|----------------------|
| `mongodb_version` | `8.0` |
| `mongodb_packages` | `mongodb-org` (+ `mongodb-mongosh-shared-openssl3` on Amazon 2023) |
| `mongodb_package_dependencies` | `selinux-policy`, `selinux-policy-targeted`, `audit`, `tuned` (tuned excluded on Amazon 2023) |
| `mongodb_python_packages` | `python39`+`python39-pip` (RHEL 8); `python3`+`python3-pip` (RHEL 9, AL2023) |

Hardware specs for `verify` playbook (`mongodb_hw_specs`):
- dev: 8 CPU, 64 GB RAM, 1000 GB disk
- test/prod: 16 CPU, 128 GB RAM, 1000 GB disk

## Dependencies / Assumptions

- The `common` role must be applied first.
- The `community.mongodb` collection must be installed on the control node.
- Python 3 must be available on the target node for `community.mongodb` tasks (the role installs it).
- When `mongodb_tls_enabled: true` and `mongodb_tls_copy_certs: true`, the certificate file at `{{ mongodb_pki_src_dir }}/{{ inventory_hostname }}.pem` must contain both the certificate and private key concatenated.

## Gotchas

- The mongod config is written three times during install: `initialize` (no auth/TLS), after auth setup, and after TLS setup. Each write triggers a mongod restart via the handler.
- The `mongodb_config_state` custom module determines whether to create users idempotently — it queries MongoDB directly and checks for existing auth/replication config. This module uses the `mongodb_python_venv` interpreter.
- User creation runs only on `mongodb_primary[0]` even in replica set mode, which is correct because MongoDB replicates users across the set.
- When `replication_enabled: true`, replica set initiation must happen before auth is enabled. The `configure-mongodb-replicaset.yml` task runs first for this reason.
- THP behavior changed at MongoDB 8.0: older versions require THP disabled; 8.0+ requires THP enabled. The role checks `mongodb_version | float` to decide which task file to run.
