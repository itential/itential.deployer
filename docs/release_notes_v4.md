# Release v4 Release Notes

The following documents the new and breaking changes in the v4 release.

---

## Commits in `v4` (12)

| Hash | Description |
|------|-------------|
| a641765 | Fix ansible-lint errors in TLS changes (#310) |
| e7dd3e9 | Add TLS standardization for platform, mongo, gateway & redis roles (#300) |
| 1066487 | Add example inventories (#306) |
| 0b52955 | README updates, fail message update (#305) |
| 25c860e | Enable setting Redis replica priority (#304) |
| 5b2b9fb | Playbooks & tasks to verify environment and confirm installation (#302) |
| 8468f0f | Remove prometheus and grafana playbooks and roles (#303) |
| e84a333 | Add certify and verify playbooks (#293) |
| 5af02a6 | Remove Gateway HAProxy role (#298) |
| 3a9a13b | Remove vault playbooks and role (#296) |
| 6f57f2d | Fix issue with redis min replicas (#295) |
| 88f778e | Update redis playbook and role to support new ASA architecture (#291) |

---

## ⚠️ Breaking Changes

### 1. Five entire roles removed

| Removed Role | Impact |
|---|---|
| `roles/vault/` | All Vault-related playbooks and role tasks deleted |
| `roles/prometheus/` | All Prometheus monitoring tasks deleted |
| `roles/grafana/` | All Grafana dashboards and tasks deleted |
| `roles/gateway_haproxy/` | Gateway HAProxy role deleted |
| `roles/preflight/` | Pre-flight check role deleted |

**Action required:** Any playbooks or inventories that reference `itential.deployer.vault`, `itential.deployer.prometheus`, `itential.deployer.grafana`, or `itential.deployer.preflight` will fail. The `preflight_*.yml` playbooks are also deleted.

---

### 2. TLS default changed to ON for MongoDB and Platform

| Variable | Old default | New default |
|---|---|---|
| `mongodb_tls_enabled` | `false` | **`true`** |
| `mongodb_tls_copy_certs` | not set | **`true`** |
| `platform_mongo_tls_enabled` | `false` | **`true`** |

**Action required:** Existing inventories that do not explicitly set `mongodb_tls_enabled: false` and `platform_mongo_tls_enabled: false` will now attempt to configure TLS. If certificates are not provided, the deployment will fail or services will not start.

---

### 3. Gateway HTTPS default changed to ON and variable renamed

| Old variable | New variable | Old default | New default |
|---|---|---|---|
| `gateway_https` | `gateway_https_enabled` | `false` | **`true`** |
| `gateway_ssl_copy_certs` | `gateway_pki_copy_certs` | `true` | `true` |

**Action required:** Any inventory or task referencing `gateway_https` must be updated to `gateway_https_enabled`. Because the default flipped to `true`, inventories that relied on the `false` default will now configure HTTPS unexpectedly.

---

### 4. Gateway SSL variable set replaced by PKI variable set

The entire `gateway_ssl_*` variable set has been replaced by `gateway_pki_*` / `gateway_https_*` variables.

| Removed variable | Replacement variable |
|---|---|
| `gateway_ssl_dir` | `gateway_pki_base_dir`, `gateway_pki_https_dir` |
| `gateway_ssl_cert_src` | `gateway_https_cert_src` |
| `gateway_ssl_cert_dest` | `gateway_https_cert_dest` |
| `gateway_ssl_key_src` | `gateway_https_key_src` |
| `gateway_ssl_key_dest` | `gateway_https_key_dest` |
| `gateway_ssl_rootca_src` | `gateway_https_ca_src` |
| `gateway_ssl_rootca_dest` | `gateway_https_ca_dest` |

Certificate file modes also changed: cert `0400` → `0644`, key `0400` → `0600`.

**Action required:** Update all inventory vars that reference any `gateway_ssl_*` variable to the new `gateway_https_*` / `gateway_pki_*` equivalents.

---

### 5. MongoDB SSL variable set replaced by PKI variable set

| Removed variable | Replacement variable |
|---|---|
| `mongodb_ssl_root_dir` | `mongodb_pki_base_dir` (default: `/etc/pki/mongodb`) |
| `mongodb_auth_keyfile_destination` | `mongodb_auth_key_dest` |
| `mongodb_cert_keyfile_destination` | `mongodb_tls_cert_dest` |
| `mongodb_root_ca_file_destination` | `mongodb_tls_ca_dest` |

**Action required:** Update any inventory vars or custom tasks that reference `mongodb_ssl_root_dir`, `mongodb_auth_keyfile_destination`, `mongodb_cert_keyfile_destination`, or `mongodb_root_ca_file_destination`.

---

### 6. Platform TLS variables removed or replaced

| Removed variable | Replacement variable |
|---|---|
| `platform_tls_dir` | `platform_pki_base_dir` (new structure) |
| `platform_mongodb_root_ca_file_destination` | `platform_mongodb_ca_dest` |
| `platform_webserver_https_key` | `platform_https_key_dest` |
| `platform_webserver_https_cert` | `platform_https_cert_dest` |
| `platform_mongo_tls_ca_file` (static) | Auto-derived from `platform_pki.yml` |

**Action required:** Update any inventory vars or custom tasks that reference the removed platform TLS variables.

---

### 7. Redis variable renames and removals

| Removed variable | Replacement variable | Notes |
|---|---|---|
| `redis_master_name` | `redis_sentinel_master_name` | Renamed |
| `redis_master_host` | Auto-resolved from `groups['redis_master'][0]` | Removed from defaults |
| `redis_replication_enabled` | Removed — replication is now automatic based on group membership | Breaking if set to `false` |
| `redis_bind_ipv6` | Removed | |
| `redis_bind_addr_source` | Removed | |
| `redis_bind_addrs` | `redis_bind` | Now defaults to `127.0.0.1 {{ ansible_default_ipv4.address }}` |

**Action required:**
- Rename `redis_master_name` to `redis_sentinel_master_name` in all inventories.
- Remove `redis_replication_enabled` references — replication is now controlled solely by group membership.
- Replace `redis_bind_addrs` with `redis_bind` if overriding bind addresses.

---

### 8. Redis inventory group structure changed

The Redis installation used a flat `redis` group (and optionally `redis_secondary`). The new structure requires:

```yaml
redis_master:    # exactly one host — the initial primary
redis_replica:   # all replica hosts
redis_sentinel:  # all sentinel hosts
```

**Action required:** Existing inventories using `redis` or `redis_secondary` groups must be restructured.

---

### 9. `os_compatibility` module removed, replaced by `gather_host_information`

| Removed | Added |
|---|---|
| `plugins/modules/os_compatibility.py` | `plugins/modules/gather_host_information.py` |

**Action required:** Any custom playbooks calling `itential.deployer.os_compatibility` must be updated.

---

### 10. Vault token/role/secret defaults changed from `""` to `undefined`

| Variable | Old default | New default |
|---|---|---|
| `platform_vault_token` | `""` | _(undefined/null)_ |
| `platform_vault_role_id` | `""` | _(undefined/null)_ |
| `platform_vault_secret_id` | `""` | _(undefined/null)_ |

**Action required:** Any task logic that checked these against an empty string will now see them as undefined. Validate condition checks in custom tasks.

---

## New Features

### Verify Playbooks
New playbooks to confirm the environment is ready **before** installation:

```bash
ansible-playbook -i <inventory> itential.deployer.verify
ansible-playbook -i <inventory> itential.deployer.verify_redis
ansible-playbook -i <inventory> itential.deployer.verify_mongodb
ansible-playbook -i <inventory> itential.deployer.verify_platform
```

### Certify Playbooks
New playbooks to certify a completed installation and generate markdown reports:

```bash
ansible-playbook -i <inventory> itential.deployer.certify
ansible-playbook -i <inventory> itential.deployer.certify_redis
ansible-playbook -i <inventory> itential.deployer.certify_mongodb
ansible-playbook -i <inventory> itential.deployer.certify_platform
```

Reports are written to `/tmp/itential-reports/` on the control node by default.

### Standardized PKI Variable Structure
Each role now has a dedicated `defaults/main/pki.yml` file providing a consistent, fully customizable PKI variable hierarchy:

| Role | New PKI defaults file | Base dir default |
|---|---|---|
| Redis | `roles/redis/defaults/main/pki.yml` | `/etc/pki/redis` |
| MongoDB | `roles/mongodb/defaults/main/pki.yml` | `/etc/pki/mongodb` |
| Platform | `roles/platform/defaults/main/pki.yml` | `/etc/pki/itential-platform` |
| Gateway | `roles/gateway/defaults/main/pki.yml` | `/etc/pki/automation-gateway` |

### Redis Replica Priority
New variable `redis_replica_priority` controls Sentinel failover preference. Set to `auto` (default) to calculate automatically based on position, or an explicit integer (0–100). Setting to `0` prevents promotion.

### Redis Max Memory
New variable `redis_maxmemory_bytes` controls maximum memory for Redis. Set to `auto` (default) to calculate automatically based default ratio of 0.60 and a minimum of 512 bytes. Optionally, maximum memory can be set manually.

### Redis Prometheus User Disabled by Default
`redis_prometheus_user_enabled: false` — the Prometheus ACL user is no longer created unless explicitly enabled.

### New `env` Inventory Variable
A new top-level `env` variable is expected in inventories to declare environment type. Used by the verify stage to select resource specs.

```yaml
all:
  vars:
    env: dev   # valid values: dev, test, prod
```

### Example Inventories
Twelve example inventory files added under `example_inventories/`:

| Directory | Files |
|---|---|
| `aio/` | `aio_default_passwords.yaml`, `aio_override_default_passwords.yaml` |
| `minimal/` | `minimal_default_passwords.yaml`, `minimal_override_default_passwords.yaml` |
| `ha2/` | `ha2_default_passwords.yaml`, `ha2_override_default_passwords.yaml` |
| `asa/` | `asa_default_passwords.yaml`, `asa_override_default_passwords.yaml`, `asa_tls.yaml` |
| `platform/` | `external_urls.yaml` |
| `redis/` | `redis_from_remi_repo.yaml`, `redis_from_source.yaml`, `redis_from_system_repo.yaml` |

### Gateway Validate-Vars Task
A new `validate-vars.yml` task runs at the start of the gateway role (tagged `always`) to assert that PKI variables are properly set before any installation begins.

### TLS Documentation
New `docs/tls_guide.md` covering TLS configuration for all components.

---

## Deleted Playbooks

| Deleted playbook | Notes |
|---|---|
| `playbooks/vault.yml` | Vault role removed |
| `playbooks/grafana.yml` | Grafana role removed |
| `playbooks/prometheus.yml` | Prometheus role removed |
| `playbooks/prometheus_exporters.yml` | Prometheus role removed |
| `playbooks/prometheus_site.yml` | Prometheus role removed |
| `playbooks/download_packages_vault.yml` | Vault role removed |
| `playbooks/preflight.yml` | Preflight role removed |
| `playbooks/preflight_gateway.yml` | Preflight role removed |
| `playbooks/preflight_mongodb.yml` | Preflight role removed |
| `playbooks/preflight_platform.yml` | Preflight role removed |
| `playbooks/preflight_redis.yml` | Preflight role removed |

---

## Deleted Documentation

| Deleted file | Notes |
|---|---|
| `docs/vault_guide.md` | Vault role removed |
| `docs/prometheus_guide.md` | Prometheus/Grafana role removed |

New: `docs/tls_guide.md`

---

## Non-Breaking Changes

- **README**: Sample inventories section removed (replaced by `example_inventories/` directory).
- New verify/certify playbook documentation added. ASA architecture description updated to clarify 3-datacenter requirement.
- **`redis_prometheus_user_enabled`**: New var, defaults `false` — no change to existing behavior.
- **`redis_replica_priority`**: New var, `auto` by default — no change to existing behavior.
- **`redis_sentinel_quorum`**: New var, `auto` by default — no change to existing behavior.
- **`redis_sentinel_bind`**: New var mirroring `redis_bind` pattern — no change to existing behavior.
- **MongoDB `mongodb_certify_report_dir_*`**: New vars with defaults — no change to existing behavior.
- **Platform certify report dirs**: New vars with defaults — no change to existing behavior.
- **Gateway firewall rules**: Logic simplified — no longer depends on `gateway_haproxy_enabled` (which no longer exists). HTTP port rule applies when HTTPS is disabled; HTTPS port rule applies when HTTPS is enabled.
- **`platform_vault_token_dir`**: Changed reference from `platform_server_dir_default` to `platform_server_dir` — functionally equivalent if the role sets this variable as expected.
- **`platform_mongo_tls_allow_invalid_certificates`**: Changed from static `false` to conditional `{{ false if platform_mongo_tls_enabled | bool else '' }}` — behavior unchanged when TLS is enabled; when TLS is disabled the value becomes an empty string rather than `false`.
