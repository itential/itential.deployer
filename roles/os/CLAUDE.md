# Role: os

## Purpose

Installs base OS, security, and operational packages required by all Itential components. Targets RedHat-family hosts only. Skips entirely if `/etc/itential-release` already exists (idempotency guard).

## Entry Point Tasks — main.yml

1. Stat `/etc/itential-release` (from `common_itential_release_file`)
2. Fail if `ansible_os_family` is not `redhat`
3. Include `redhat.yml` when the release file does not exist

### redhat.yml

1. Load OS-version-specific vars from `vars/release-<major>.yml` (falls through to `release-undefined.yml` which sets `invalid_os_release` to fail)
2. Fail if OS major version is unsupported
3. Include `redhat-online.yml` when `not offline_install_enabled`
4. Include `redhat-offline.yml` when `offline_install_enabled`

### redhat-online.yml

Installs `os_packages`, `security_packages`, and `operational_packages` via `dnf`.

### redhat-offline.yml

Installs the same package groups using the `offline` role's `install-rpms` task file.

### download-packages.yml (called by `download_packages_os.yml` playbook)

Downloads all OS package RPMs to the offline staging directory using the `offline` role's `download-rpms` task file.

## Key Variables

There are no `defaults/` variables in this role. Package lists come from `vars/release-<N>.yml`.

| Variable | Defined In | Purpose |
|----------|-----------|---------|
| `os_packages` | `vars/release-8.yml`, `vars/release-9.yml` | Core OS packages (e.g., `coreutils`, `openssl`) |
| `security_packages` | `vars/release-8.yml`, `vars/release-9.yml` | SELinux policy packages, `policycoreutils`, `checkpolicy` |
| `operational_packages` | `vars/release-8.yml`, `vars/release-9.yml` | Ops tooling: `git`, `curl`, `jq`, `tcpdump`, `tar`, etc. |
| `invalid_os_release` | `vars/release-undefined.yml` | Defined only when OS version is unsupported; triggers a fail |
| `offline_install_enabled` | `common/defaults/main/offline.yml` | Controls online vs offline install path |
| `offline_*_dir` | `defaults/main/offline.yml` | Offline staging directories |

### RHEL 8 Package Lists (vars/release-8.yml)

- `os_packages`: `coreutils`, `openssl`
- `security_packages`: `checkpolicy`, `libselinux`, `libselinux-utils`, `policycoreutils`, `policycoreutils-python-utils`, `selinux-policy-mls`
- `operational_packages`: `bind-utils`, `curl`, `dos2unix`, `git`, `gzip`, `jq`, `man`, `rsyslog`, `sudo`, `sysstat`, `tar`, `tcpdump`, `telnet`, `unzip`, `wget`, `which`, `zip`

RHEL 9 uses the same lists (identical `vars/release-9.yml`).

## Dependencies / Assumptions

- Requires the `common` role to have been applied first (for `common_itential_release_file` and `offline_install_enabled`).
- The `os.yml` playbook targets: `platform`, `platform_secondary`, `redis`, `redis_secondary`, `mongodb`, `mongodb_arbiter`, `gateway`.
- The `os` role is not applied automatically as part of the main component roles (it is a separate playbook step in `site.yml` predecessors). Check whether `os.yml` was run separately if packages are missing.

## Gotchas

- The role skips entirely if `/etc/itential-release` exists. This means re-runs on already-installed hosts do nothing, even if new packages were added to the vars files.
- `vars/release-undefined.yml` defines `invalid_os_release` to trigger the fail task — do not set this variable in your inventory.
- The offline path (`redhat-offline.yml`) requires offline RPMs to have been staged at the path built from `offline_control_node_root` and `offline_itential_packages_path`.
