# Role: offline

## Purpose

Shared utility role providing reusable tasks for downloading packages (RPMs, Python wheels, adapters, Ansible collections) to the control node and installing them from the control node onto target nodes in air-gapped deployments. Has no `main.yml` — all task files are called via `tasks_from:` by other roles.

## Task Files

| File | Called By | Purpose |
|------|-----------|---------|
| `download-rpms.yml` | Component roles' `download-packages.yml` | Downloads RPM packages to a specified directory using one of several methods |
| `download-wheels.yml` | Component roles' `download-packages.yml` | Downloads Python wheel packages using `pip download` |
| `download-adapters.yml` | `platform/download-packages.yml` | Downloads multiple platform adapters |
| `download-adapter.yml` | `download-adapters.yml` | Downloads a single adapter (looped) |
| `install-rpms.yml` | Component role task files | Copies RPMs from control node to target and installs via dnf or rpm |
| `install-wheels.yml` | Component role task files | Installs Python wheels from control node into a venv or via pip |
| `install-wheels-archives.yml` | Component role task files | Installs multiple wheel archives |
| `install-wheels-archive.yml` | `install-wheels-archives.yml` | Installs a single wheel archive (looped) |
| `install-adapter.yml` | `platform/install-adapters.yml` | Installs a single adapter archive |
| `fetch-packages.yml` | Component roles' `download-packages.yml` | Copies downloaded packages from target node back to control node (fetch) |

## download-rpms.yml

Requires the caller to set:

| Variable | Values | Purpose |
|----------|--------|---------|
| `offline_download_dir` | path | Directory on target to download RPMs into |
| `offline_download_method` | `yum_module`, `yum_install`, `yum_reinstall`, `repotrack`, `yumdownloader`, `get_url` | Which download mechanism to use |
| `offline_download_packages` | list | Package names or URLs to download |

Supports `repository_api_key` (JFrog/GitLab) and `repository_username`/`repository_password` (Nexus) for `get_url` method.

## install-rpms.yml

Requires the caller to set:

| Variable | Purpose |
|----------|---------|
| `offline_rpms_path` | Path on the control node glob-matched for `*.rpm` files to copy and install |

Process: creates temp dir → copies RPMs → rebuilds RPM DB → disables all repos → installs via dnf with `cacheonly: true` and `disable_gpg_check: true`. Optionally uses `rpm -i` directly if `offline_use_rpm_cmd: true`.

## fetch-packages.yml

Requires:

| Variable | Purpose |
|----------|---------|
| `offline_src_dir` | Directory on target node containing downloaded packages |
| `offline_dest_dir` | Directory on control node to fetch packages into |

Uses `ansible.builtin.fetch` with `flat: true`.

## Offline Directory Structure

The offline directory paths are built by each component role using variables from `common/defaults/main/offline.yml`:

```
{{ offline_control_node_root }}/
  {{ offline_itential_packages_path }}/
    {{ platform_release }}/platform/
      rpms/dependencies/
      rpms/nodejs/
      rpms/os/
      wheels/
      adapters/
    {{ gateway_release }}/gateway/
      rpms/dependencies/
      rpms/python/
      rpms/build/
      wheels/
      collections/
    mongodb/
      rpms/
      wheels/
    redis/
      rpms/build/
      rpms/security/
      archives/
```

## Dependencies / Assumptions

- This role has no defaults. All variables are passed by the calling role's task files.
- The role is always included (not applied independently) — it appears in `roles:` only in `download_packages_*` playbooks where `offline_install_enabled` is forced to `false`.
- `install-rpms.yml` uses `dnf` with all repos disabled, relying on the packages being fully self-contained (with all dependencies pre-downloaded).

## Gotchas

- `offline_use_rpm_cmd` is an escape hatch for environments where `dnf` with `cacheonly` fails. It uses `rpm -i` with options from `offline_rpm_cmd_opts` (caller must set this).
- `download-rpms.yml` with `repotrack` runs `repotrack` from the download directory (`chdir`), not with `--download-path`. Verify `repotrack` behavior on the target OS version.
- The `get_url` method in `download-rpms.yml` only processes packages where `'http' in package` and `package.endswith('.rpm')` — non-URL entries are silently skipped.
