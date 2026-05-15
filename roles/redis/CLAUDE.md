# Role: redis

## Purpose

Installs and configures Redis and Redis Sentinel for use with Itential Platform. Supports installation from source (default) or from a YUM repository (Remi or system). Handles authentication (ACL users), TLS, replication, Sentinel setup, SELinux, logrotate, and firewalld.

## Entry Point Tasks — main.yml

1. Validate variables (`validate-vars.yml`) and set node type facts:
   - `redis_is_master_node`, `redis_is_replica_node`, `redis_is_sentinel_node`, `redis_is_data_node`
   - `redis_has_replicas`, `redis_has_sentinels`
2. Install Redis (triggers `Enable and Start Redis` and `Enable and Start Redis Sentinel` handlers):
   a. `install-common.yml` — create OS user/group, directories, security packages
   b. `install-from-source.yml` — when `redis_install_from_source: true`
   c. `install-from-repo.yml` — when `redis_install_from_source: false`
3. Configure SELinux (when enforcing and install-from-source; loads `itential_redis_sentinel.te`)
4. Configure TLS (`configure-redis-tls.yml`) — when `redis_tls_enabled: true`
5. Configure Redis (`configure-redis.yml`) — when `redis_is_data_node`
6. Configure Sentinel (`configure-sentinel.yml`) — when `redis_is_sentinel_node`
7. Flush handlers, start and assert Redis is active (data nodes)
8. Flush handlers, start and assert Redis Sentinel is active (sentinel nodes)

## install-from-source.yml

1. Check if `redis-server` binary exists and get its version
2. If already installed and version matches `redis_source_url` archive name: skip
3. Otherwise: create temp dir → install build packages (`tar`, `gcc`, `make`, etc.) → download source archive → unarchive → `make install USE_SYSTEMD=true PREFIX=/usr/local` → clean up → remove build packages

## Key Variables

### redis.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `redis_bin_dir` | `/usr/local/bin` (source) or `/usr/bin` (repo) | Binary location |
| `redis_conf_dir` | `/etc/redis` | Config directory |
| `redis_conf_file` | `/etc/redis/redis.conf` | Redis config file |
| `redis_log_dir` | `/var/log/redis` | Log directory |
| `redis_data_dir` | `/var/lib/redis` | Data directory |
| `redis_db_filename` | `dump.rdb` | RDB filename |
| `redis_owner` | `redis` | OS user |
| `redis_group` | `redis` | OS group |
| `redis_port` | `6379` | Listen port |
| `redis_bind` | `127.0.0.1 {{ ansible_default_ipv4.address }}` | Bind addresses |
| `redis_auth_enabled` | `true` | Enable ACL user authentication |
| `redis_tls_enabled` | `false` | Enable TLS (disabled by default) |
| `redis_replicaof` | `{{ groups['redis_master'][0] }} {{ redis_port }}` | Replication target (used on replica nodes) |
| `redis_replica_priority` | `auto` | Sentinel failover priority; `auto` calculates from position |
| `redis_user_admin_password` | `admin` | Admin user password |
| `redis_user_itential_password` | `itential` | App user password |
| `redis_user_repluser_password` | `repluser` | Replication user password |
| `redis_user_sentineladmin_password` | `admin` | Sentinel admin password |
| `redis_user_sentineluser_password` | `sentineluser` | Sentinel monitor user password |
| `redis_user_monitor_password` | `monitor` | Monitor user password |
| `redis_monitor_user_enabled` | `false` | Create the monitor user |
| `redis_maxmemory_bytes` | `auto` | `auto` = 80% of RAM; or explicit bytes |
| `redis_maxmemory_ratio` | `0.80` | Fraction of RAM to use when `redis_maxmemory_bytes: auto` |
| `redis_maxmemory_min_mb` | `512` | Minimum maxmemory floor (MB) |
| `redis_tls_port` | `6379` (default; see pki.yml for TLS port) | TLS port |
| `redis_tls_auth_clients` | `no` | Whether to require client certificates |
| `redis_tls_protocols` | `TLSv1.2 TLSv1.3` | Allowed TLS protocol versions |
| `redis_certify_report_dir_remote` | `/var/tmp/itential-reports/redis` | Cert report dir on target |
| `redis_certify_report_dir_local` | `/tmp/itential-reports/redis` | Cert report dir on control node |

### sentinel.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `redis_sentinel_conf_file` | `/etc/redis/sentinel.conf` | Sentinel config file |
| `redis_sentinel_log` | `/var/log/redis/sentinel.log` | Sentinel log path |
| `redis_sentinel_master_name` | `itentialmaster` | Sentinel master set name |
| `redis_sentinel_port` | `26379` | Sentinel listen port |
| `redis_sentinel_bind` | `127.0.0.1 {{ ansible_default_ipv4.address }}` | Sentinel bind addresses |
| `redis_sentinel_quorum` | `auto` | Auto-calculates as `(sentinel_count // 2) + 1`; or explicit integer |
| `redis_sentinel_certify_report_dir_remote` | `/var/tmp/itential-reports/sentinel` | Sentinel cert report dir on target |
| `redis_sentinel_certify_report_dir_local` | `/tmp/itential-reports/sentinel` | Sentinel cert report dir on control node |

### install.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `redis_install_from_source` | `true` | Install from source (compiled); `false` = install from YUM |
| `redis_build_packages` | `tar`, `unzip`, `gcc`, `gcc-c++`, `make`, `systemd-devel` | Packages needed to compile Redis |
| `redis_security_packages` | `policycoreutils-python-utils` | SELinux management package |
| `redis_remi_repo_url` | Remi enterprise URL | Used when installing from Remi repo |
| `redis_epel_repo_url` | Fedora EPEL URL | Used when installing EPEL for Remi |

### pki.yml defaults (TLS paths)

| Variable | Default | Purpose |
|----------|---------|---------|
| `redis_pki_base_dir` | `/etc/pki/redis` | Base PKI directory |
| `redis_pki_private_dir` | `{{ redis_pki_base_dir }}/private` | Private key subdirectory |
| `redis_tls_cert_file` | `{{ inventory_hostname }}.crt` | Server cert filename |
| `redis_tls_key_file` | `{{ inventory_hostname }}.key` | Server key filename |
| `redis_tls_ca_file` | `ca-bundle.crt` | CA bundle filename |
| `redis_tls_dh_params_file` | `dhparams.pem` | DH params filename |
| `redis_sentinel_tls_cert_file` | `sentinel.crt` | Sentinel cert filename |
| `redis_sentinel_tls_key_file` | `sentinel.key` | Sentinel key filename |
| `redis_pki_src_dir` | `""` | Source directory on control node (required when TLS enabled) |
| `redis_pki_owner` | `redis` | File/dir owner |
| `redis_pki_group` | `redis` | File/dir group |
| All `_dest` vars | Built from base dir + filename | Destination paths on target |
| All `_src` vars | Built from `redis_pki_src_dir` + filename | Source paths on control node |

## TLS Configuration

TLS is **disabled by default** (`redis_tls_enabled: false`).

Flow (`configure-redis-tls.yml`, runs when `redis_tls_enabled: true`):
1. Create `redis_pki_base_dir` (mode `0750`)
2. Create `redis_pki_private_dir` (mode `0700`)
3. Copy server cert, server key, CA bundle, DH params from control node (each conditional on source path being non-empty)
4. Each copy notifies `restart redis`

The `redis.conf.j2` template includes TLS configuration blocks when `redis_tls_enabled: true`. Sentinel TLS certs (`sentinel.crt`, `sentinel.key`) are expected in `redis_pki_src_dir` when using TLS with Sentinel.

To enable TLS, set in inventory:
```yaml
redis_tls_enabled: true
redis_pki_src_dir: /path/to/certs/on/control/node
```

## Templates

| Template | Rendered To | Purpose |
|----------|-------------|---------|
| `redis.conf.j2` | `/etc/redis/redis.conf` | Redis server configuration (auth, TLS, replication, ports, memory) |
| `sentinel.conf.j2` | `/etc/redis/sentinel.conf` | Sentinel configuration (master monitoring, quorum, TLS) |
| `redis.service.j2` | `/etc/systemd/system/redis.service` | Redis systemd unit |
| `redis-sentinel.service.j2` | `/etc/systemd/system/redis-sentinel.service` | Redis Sentinel systemd unit |
| `redis.logrotate.j2` | `/etc/logrotate.d/redis` | Redis log rotation |
| `redis-sentinel.logrotate.j2` | `/etc/logrotate.d/redis-sentinel` | Sentinel log rotation |
| `redis.preflight.j2` | Used by `preflight.yml` | Pre-install output |
| `redis-validation-report.md.j2` | `redis_certify_report_dir_remote/<host>.md` | Certification report |

## Handlers

| Handler | Listen String | Action |
|---------|--------------|--------|
| Enable and Start Redis | `restart redis` | `systemctl restart redis` (throttle: 1; data nodes only) |
| Enable and Start Redis Sentinel | (no listen string) | `systemctl restart redis-sentinel` (throttle: 1; sentinel nodes only) |
| Update Itential release file | (separate notify) | Includes `update-release-file.yml` |

Handler throttle (`throttle: 1`) ensures rolling restart of replicas — only one Redis node restarts at a time.

## Inventory Groups

| Group | Role |
|-------|------|
| `redis_master` | Primary data node |
| `redis_replica` | Secondary data nodes |
| `redis_sentinel` | Sentinel nodes (typically colocated with data nodes) |

The same host can be in both `redis_master` and `redis_sentinel`. The role detects which groups a host belongs to and runs the appropriate configuration tasks.

## Release-Specific Vars (vars/platform-release-6.yml)

| Variable | Value |
|----------|-------|
| `redis_source_url` | `https://github.com/redis/redis/archive/7.4.6.tar.gz` (all OS versions) |
| `redis_packages` (from repo) | `@redis:remi-7.2` (all OS versions) |

Hardware specs for `verify` playbook (`redis_hw_specs`):
- dev: 8 CPU, 16 GB RAM, 100 GB disk
- test/prod: 8 CPU, 32 GB RAM, 100 GB disk

## Dependencies / Assumptions

- The `common` role must be applied first.
- The `os` role should be applied before `redis` to ensure SELinux tools and build tools are available.
- `redis_master` group must always have at least one member — `redis_replicaof` and sentinel config reference `groups['redis_master'][0]`.
- When `redis_install_from_source: true`, build packages (`gcc`, `make`, `systemd-devel`, etc.) are installed, used for compilation, then removed. Offline mode requires these pre-staged in `redis_offline_control_node_rpms_dir/build/`.

## Gotchas

- `redis_install_from_source: true` is the default. The Remi repo install (`redis_install_from_source: false`) requires `common_install_yum_repos: true` and the string `remi` in `redis_packages`.
- The source install checks the installed Redis version against the archive filename. Version mismatch triggers a full recompile. The comparison uses the tarball name (e.g., `redis-7.4.6`) not semantic version parsing.
- `redis_sentinel_quorum: auto` computes quorum at template render time based on `groups['redis_sentinel'] | length`. For a 3-sentinel cluster this is 2 (majority). If you set an explicit value, ensure it is `<= number of sentinels`.
- `redis_replica_priority: auto` calculates priority based on the host's index in the replica group. Explicit values `0-100` work; `0` means never promote.
- The `throttle: 1` on the restart handler means in a 3-node cluster, each restart is serialized. This is intentional to prevent split-brain during rolling restarts.
