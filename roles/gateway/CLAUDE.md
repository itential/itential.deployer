# Role: gateway

## Purpose

Installs and configures Itential Automation Gateway (IAG). Handles Python virtualenv creation, pip dependency installation, Ansible collection installation, Nornir configuration, HTTPS TLS certificate deployment, systemd service setup, firewalld, and SELinux.

## Entry Point Tasks — main.yml

1. `validate-vars.yml` (always tagged) — validate PKI variables
2. Load release vars from `vars/gateway-release-{{ gateway_release }}.yml` (fail if release unsupported)
3. Create temp working directory
4. Install dependency packages (`gateway_packages`) — online or offline
5. Create `itential` group and user (with SSH key generation)
6. Create working directories under `gateway_install_dir` and `gateway_data_dir`
7. Create `python-venvs` directory (when `gateway_enable_python_venv: true`)
8. `configure-gateway-https.yml` — PKI setup and cert copy (when `gateway_pki_copy_certs: true`)
9. Install Python (include `install-python.yml`)
10. Install build packages (`gateway_build_packages`) — online only (removed in `always` block)
11. Install Python dependencies (`install-python-dependencies.yml`)
12. Configure Ansible (when `gateway_enable_ansible: true`): install collections → create `ansible.cfg` → create empty inventory/vault files
13. Check if IAG is already installed (`stat` on `venv/bin/automation-gateway`)
14. Copy or download IAG wheel file when not already installed
15. `pip install` IAG wheel into `gateway_install_dir/venv`
16. Set ownership (`chown -R`) and permissions (`chmod -R 775`) on venv (tagged `configure_gateway`)
17. Create `properties.yml` from versioned template (tagged `configure_gateway`)
18. Create Nornir inventory/config files (when `gateway_enable_nornir: true`)
19. Write `automation-gateway.service` systemd unit (tagged `configure_gateway`)
20. Open firewalld port (HTTP or HTTPS depending on `gateway_https_enabled`)
21. `configure-selinux.yml`
22. Copy test scripts to `gateway_install_dir/scripts/`
23. Start and enable `automation-gateway` service (tagged `always` — runs even when other tags are selected via `--tags`)
24. `update-release-file.yml`
25. Remove temp working directory
26. `always` block: remove build packages that were installed; assert service is active

## Other Entry Points

- `tasks/verify-gateway.yml` (invoked by `playbooks/verify_gateway.yml`, tags_from `verify-gateway`) — checks connectivity to Gateway's required public repositories (`gateway_required_repositories`, passed to `common:verify-connectivity` as `required_repositories`) via `common:verify-connectivity`. Unlike the other components' verify flows, it does not call `common:verify-host` (no `gateway_hw_specs` exists yet), so it skips OS/CPU/RAM/disk/proxy validation entirely. Its final assert uses `ignore_errors: true` and sets a per-host `verification_passed` fact instead of failing hard, for the same reason described in `roles/common/CLAUDE.md`'s "Non-Fatal Verify Design" section — so that a Gateway failure doesn't abort `playbooks/verify.yml` before the other imported verify playbooks run.

## Key Variables

### gateway.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `gateway_install_dir` | `/opt/automation-gateway` | IAG installation root |
| `gateway_data_dir` | `/var/lib/automation-gateway` | IAG data directory |
| `gateway_log_dir` | `/var/log/automation-gateway` | IAG log directory |
| `gateway_properties_location` | `/etc/automation-gateway` | Properties file directory |
| `gateway_ansible_collections_path` | `{{ gateway_install_dir }}/ansible/collections` | Ansible collections path |
| `gateway_port` | `8083` | HTTP listen port |
| `gateway_https_enabled` | `true` | Enable HTTPS (default on) |
| `gateway_https_port` | `8443` | HTTPS listen port |
| `gateway_pki_copy_certs` | `true` | Copy TLS certs from control node |
| `gateway_tlsv1_2` | `false` | Allow TLSv1.2 (in addition to 1.3) |
| `gateway_user` | `itential` | OS user for IAG process |
| `gateway_group` | `itential` | OS group |
| `gateway_venv_name` | `venv_gateway_{{ gateway_release }}` | Name of the Python virtualenv directory |
| `gateway_python_venv` | `{{ gateway_install_dir }}/{{ gateway_venv_name }}` | Path to the Python virtualenv |
| `gateway_http_server_threads` | `{{ ansible_processor_cores * 4 }}` | IAG HTTP thread count |
| `gateway_enable_ansible` | `true` | Install Ansible and configure collections |
| `gateway_enable_nornir` | `true` | Create Nornir config/inventory files |
| `gateway_enable_netmiko` | `true` | Enable netmiko support |
| `gateway_enable_scripts` | `true` | Enable script execution |
| `gateway_enable_netconf` | `true` | Enable NETCONF support |
| `gateway_enable_httpreq` | `true` | Enable HTTP request feature |
| `gateway_enable_python_venv` | `true` | Create Python venv directories |
| `gateway_enable_grpc` | `true` | Enable gRPC support |
| `gateway_enable_git` | `true` | Enable Git support |

### pki.yml defaults (TLS paths)

| Variable | Default | Purpose |
|----------|---------|---------|
| `gateway_pki_base_dir` | `/etc/pki/automation-gateway` | Base PKI directory |
| `gateway_pki_private_dir` | `{{ gateway_pki_base_dir }}/private` | Private key subdirectory |
| `gateway_pki_https_dir` | `{{ gateway_pki_base_dir }}/https` | HTTPS cert subdirectory |
| `gateway_https_cert_file` | `{{ inventory_hostname }}.crt` | HTTPS cert filename |
| `gateway_https_key_file` | `{{ inventory_hostname }}.key` | HTTPS key filename |
| `gateway_https_ca_file` | `ca-bundle.crt` | HTTPS CA bundle filename |
| `gateway_https_cert_dest` | `{{ gateway_pki_https_dir }}/{{ gateway_https_cert_file }}` | Cert destination |
| `gateway_https_key_dest` | `{{ gateway_pki_private_dir }}/{{ gateway_https_key_file }}` | Key destination |
| `gateway_https_ca_dest` | `{{ gateway_pki_https_dir }}/{{ gateway_https_ca_file }}` | CA destination |
| `gateway_pki_src_dir` | `""` | Source dir on control node (required when `gateway_pki_copy_certs: true`) |
| `gateway_https_cert_src` | `{{ gateway_pki_src_dir }}/{{ gateway_https_cert_file }}` | Cert source |
| `gateway_https_key_src` | `{{ gateway_pki_src_dir }}/{{ gateway_https_key_file }}` | Key source |
| `gateway_https_ca_src` | `{{ gateway_pki_src_dir }}/{{ gateway_https_ca_file }}` | CA source |

### offline.yml defaults

| Variable | Default | Purpose |
|----------|---------|---------|
| `gateway_target_node_root` | Under `offline_target_node_root` | Target node offline package dir |
| `gateway_control_node_root` | Under `offline_control_node_root` | Control node offline package dir |
| `gateway_offline_target_node_rpms_dir` | `{{ gateway_target_node_root }}/rpms` | RPM target dir |
| `gateway_offline_target_node_wheels_dir` | `{{ gateway_target_node_root }}/wheels` | Wheels target dir |
| `gateway_offline_control_node_rpms_dir` | `{{ gateway_control_node_root }}/rpms` | RPM source dir (control) |
| `gateway_offline_control_node_wheels_dir` | `{{ gateway_control_node_root }}/wheels` | Wheels source dir (control) |
| `gateway_offline_control_node_collections_dir` | `{{ gateway_control_node_root }}/collections` | Collections source dir (control) |

### vars/main.yml

| Variable | Purpose |
|----------|---------|
| `gateway_required_repositories` | List of repository dicts (`url`, `type`, optional `check_target`, `notes`) checked by `verify-gateway.yml` via `common:verify-connectivity`. Mirrors the Gateway rows of the README "Required Public Repositories" table. Previously this list lived in `roles/common/vars/main.yml`; `common` no longer has a `vars/` directory. |

## TLS Configuration

HTTPS is **enabled by default** (`gateway_https_enabled: true`, `gateway_pki_copy_certs: true`).

Flow (`configure-gateway-https.yml`):
1. Create `gateway_pki_base_dir` (mode `0750`, owned by `itential:itential`)
2. Create `gateway_pki_https_dir` (mode `0750`)
3. Create `gateway_pki_private_dir` (mode `0700`)
4. Call `copy-certs.yml` to copy `{{ inventory_hostname }}.crt`, `{{ inventory_hostname }}.key`, and `ca-bundle.crt` from `gateway_pki_src_dir` on the control node

The PKI infrastructure is created unconditionally when `gateway_pki_copy_certs: true`, regardless of `gateway_https_enabled`. This allows certs to be in place even if HTTPS is enabled later. The `properties.yml` template references the cert/key paths when `gateway_https_enabled: true`.

**`gateway_pki_src_dir` must be set in inventory** when `gateway_pki_copy_certs: true`. The `validate-vars.yml` task will fail if it is empty.

To disable HTTPS entirely:
```yaml
gateway_https_enabled: false
gateway_pki_copy_certs: false
```

## Templates

| Template | Rendered To | Purpose |
|----------|-------------|---------|
| `properties.4.4.yml.j2` | `/etc/automation-gateway/properties.yml` | IAG properties for release 4.4 (port, TLS, Ansible paths, feature flags) |
| `properties.4.3.yml.j2` | `/etc/automation-gateway/properties.yml` | IAG properties for release 4.3 (port, TLS, Ansible paths, feature flags) |
| `properties.4.2.yml.j2` | `/etc/automation-gateway/properties.yml` | IAG properties for release 4.2 |
| `properties.2023.3.yml.j2` | (legacy) | Legacy release templates |
| `properties.2023.2.yml.j2` | (legacy) | Legacy release templates |
| `properties.2023.1.yml.j2` | (legacy) | Legacy release templates |
| `properties.2022.1.yml.j2` | (legacy) | Legacy release templates |
| `properties.2021.2.yml.j2` | (legacy) | Legacy release templates |
| `properties.2021.1.yml.j2` | (legacy) | Legacy release templates |
| `automation-gateway.service.j2` | `/etc/systemd/system/automation-gateway.service` | Systemd unit |
| `ansible.cfg.j2` | `/etc/ansible/ansible.cfg` | Ansible configuration for IAG's internal Ansible |
| `nornir.config.yml.j2` | `{{ gateway_install_dir }}/nornir/config.yml` | Nornir configuration |
| `gateway.preflight.j2` | Used by `preflight.yml` | Pre-install checklist output |

## Handlers

| Handler | Listen String | Action |
|---------|--------------|--------|
| Restart automation-gateway | `restart automation-gateway` | `systemctl restart automation-gateway` |

## Release-Specific Vars (vars/gateway-release-4.4.yml)

| Variable | Value |
|----------|-------|
| `gateway_python_version` | `3.12` |
| `gateway_python_packages` | `python3.12`+`python3.12-pip` (RHEL 8, RHEL 9, AL2023) |
| `gateway_python_base_dependencies` | `pip==24.0`, `setuptools==78.1.1`, `wheel==0.43.0` |
| `gateway_build_packages` | `gcc-c++`, `libssh-devel`, `make`, `pkgconf-pkg-config`, `python3.12-devel` |
| `gateway_python_app_dependencies` | `importlib-metadata==4.12.0`, `grpcio-tools==1.63.2` |

Release 4.3 (`vars/gateway-release-4.3.yml`) uses Python `3.9` (`python39` on RHEL 8, `python3` on RHEL 9/AL2023) and different pinned versions (e.g., `importlib-metadata==4.13.0`, `grpcio-tools==1.53.0`). Release 4.2 uses the same package sets as 4.3 but different pinned versions (e.g., `setuptools==69.0.3`, `ncclient==0.6.10`).

Supported `gateway_release` values: `4.2`, `4.3`, `4.4`. Legacy date-format releases (`2021.1` through `2023.3`) have property templates but no dedicated vars files.

## IAG Installation Methods

The role supports two ways to provide the IAG wheel:

1. **Local file**: Set `gateway_whl_file` to the filename relative to `playbook_dir/files/`. The role copies it to the target's temp dir.
2. **Repository download**: Set `gateway_archive_download_url` to the full URL. The role downloads it on the target node using `get_url` with JFrog or Nexus credentials. Sets `gateway_whl_file` from the download result.

Only one of `gateway_whl_file` or `gateway_archive_download_url` should be set.

## Files

| File | Purpose |
|------|---------|
| `files/scripts/verify-iag-environment.py` | Python script copied to `gateway_install_dir/scripts/` for post-install environment verification |

## Dependencies / Assumptions

- The `common` role must be applied first (for `offline_install_enabled`, `common_install_yum_repos`).
- `gateway_release` must be defined in the inventory under the `gateway` group vars.
- `gateway_whl_file` or `gateway_archive_download_url` must be defined (the role does not fail fast on this — it will fail at the pip install step if neither is set and IAG is not already installed).

## Gotchas

- Build packages (`gcc`, `libssh-devel`, `make`, etc.) are installed to compile Python wheel dependencies, then removed in the `always` block — even if the play fails. This cleanup runs unconditionally.
- The IAG install is skipped if `{{ gateway_python_venv }}/bin/automation-gateway` already exists (`stat` check). To force reinstall, remove this file/symlink first.
- The "Set ownership/permissions and create properties.yml" block and the "Write automation-gateway.service to host" task are no longer gated by `not gateway_installed.stat.exists` — they now run on every playbook execution (tagged `configure_gateway`), so `properties.yml` and the systemd unit are regenerated and ownership/permissions are reapplied on re-runs, not just on first install.
- `gateway_http_server_threads` defaults to `ansible_processor_cores * 4`. On systems where `ansible_processor_cores` is unavailable or 0, this will produce 0 threads. Verify the value is sensible on target hardware.
- `gateway_pki_copy_certs: true` runs unconditionally when set, regardless of `gateway_https_enabled`. This means if you disable HTTPS but leave `gateway_pki_copy_certs: true`, the role will still try to copy certs (and fail if `gateway_pki_src_dir` is empty).
- The Ansible `ansible.cfg` written to `/etc/ansible/ansible.cfg` sets the collections path to `gateway_ansible_collections_path`. If `/etc/ansible/ansible.cfg` already exists, it is backed up but replaced.
- The `gateway_release` variable maps to both a vars file (`vars/gateway-release-<N>.yml`) and a properties template (`templates/properties.<N>.yml.j2`). Adding a new release requires both files.
- `gateway_venv_name` is a fixed name (`venv`) shared across all releases — it is not suffixed with `gateway_release`. Because different releases pin different `gateway_python_version` values (e.g. `3.9` for 4.3, `3.12` for 4.4), `install-python.yml` checks the existing venv's Python version on every run. If it doesn't match the release's `gateway_python_version`, the existing venv is moved to a `.bak.py<old_version>.<timestamp>` sibling path and a fresh venv is created, which also causes the IAG install/properties steps in `main.yml` to re-run (since the `{{ gateway_python_venv }}/bin/automation-gateway` stat check will report not-installed). This logic only runs via the main install flow (`main.yml` → `install-python.yml`) — `upgrade-gateway.yml` (used by `patch_gateway.yml`) does not check or rebuild the venv, consistent with patch upgrades not supporting major version changes.
