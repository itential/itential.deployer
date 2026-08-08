# Role: common

## Purpose

Provides shared default variables consumed by all other roles. Has no `main.yml` task entry point — it is imported by playbooks solely to inject its defaults into the variable scope. Also contains the shared `verify-host.yml`, `verify-connectivity.yml`, and `verify-results.yml` task files used by the `verify_*` playbooks.

## Entry Point Tasks

There is no `tasks/main.yml`. The task files are:

- `tasks/verify-host.yml` — imported by `verify-mongodb`, `verify-redis`, and `verify-platform` task files via `tasks_from:`. Checks OS/arch/HW specs/proxy and initializes `validation_errors`. Not called by Gateway's `verify-gateway.yml` (Gateway has no `gateway_hw_specs`/HW requirements defined yet).
- `tasks/verify-connectivity.yml` — imported by `verify-mongodb`, `verify-redis`, `verify-platform`, and `verify-gateway` (all four components) via `tasks_from:`. Checks outbound connectivity to the URLs in `common_required_repositories` (`vars/main.yml`) that match the caller's `component_name`. See "verify-connectivity.yml Logic" below.
- `tasks/verify-results.yml` — imported by `verify-mongodb`, `verify-redis`, and `verify-platform` (not Gateway, which does its own minimal assert) to print `validation_errors` and assert `cpu_validation`/`memory_validation`/`disk_validation`/`proxy_validation`/`connectivity_validation` all passed.

None of these task files are called by any role's `main.yml`.

## verify-host.yml Logic

Expects two variables from the caller:

| Variable | Example | Purpose |
|----------|---------|---------|
| `component_name` | `"Redis"` | Used in debug messages |
| `hw_specs_var_name` | `"redis_hw_specs"` | Name of the hardware specs dict variable to validate against |

Execution order:
1. Assert `platform_release` and `env` are defined, `env` in `['dev','test','prod']`
2. Call `itential.deployer.gather_host_information` module to collect OS/arch/hardware facts
3. Validate OS: RedHat/Rocky/OracleLinux 8 or 9, or Amazon Linux 2023
4. Validate architecture: `x86_64` or `aarch64`
5. Validate CPU, RAM, and disk against the `hw_specs_var_name[env]` dict (uses `ignore_errors: true` and collects failures into `validation_errors`)
6. Check for proxy settings in env vars, `/etc/environment`, `/etc/profile.d/`
7. Assert all validations passed

The hardware specs dicts (e.g., `redis_hw_specs`, `platform_hw_specs`, `mongodb_hw_specs`) are defined in `roles/<component>/vars/platform-release-<N>.yml` and keyed by `env` value.

## verify-connectivity.yml Logic

Expects one variable from the caller:

| Variable | Example | Purpose |
|----------|---------|---------|
| `component_name` | `"MongoDB"` | Selects the matching rows from `common_required_repositories` |

`common_required_repositories` (`vars/main.yml`, auto-loaded whenever the `common` role is used) mirrors the "Required Public Repositories" table in `README.md`, excluding the Ansible Control Node rows. Each entry has a `component`, `url`, `type` (`bare` or `path`), optional `check_target`, and `notes`.

Execution order:
1. Filter `common_required_repositories` down to entries matching `component_name`
2. Check baseline reachability of every entry's bare `url` via `ansible.builtin.uri` — any real HTTP status (100-599) counts as reachable; only a connection-level failure (DNS/TCP/TLS/timeout, which `fetch_url` reports as `status: -1`) counts as unreachable. Append failures to `validation_errors`.
3. For entries with `type: path` that passed step 2, request the specific `check_target` resource and expect an actual `[200, 301, 302]` response. Append failures to `validation_errors`.
4. Assert both checks passed (`ignore_errors: true`, registers `connectivity_validation`), following the same pattern as `cpu_validation`/`memory_validation`/etc. in `verify-host.yml`.

Called from `verify-mongodb.yml`, `verify-redis.yml`, and `verify-platform.yml` (which also calls it a second time with `component_name: "Vault"`, gated on `platform_configure_vault | bool`, since this collection doesn't have its own Vault role/host group but Platform is what integrates with it) and `verify-gateway.yml`.

## Key Variables

| Variable | Default | Source File | Purpose |
|----------|---------|-------------|---------|
| `common_itential_release_file` | `/etc/itential-release` | `defaults/main/main.yml` | Path to file tracking installed component versions. Written by each role after install. |
| `common_install_yum_repos` | `true` | `defaults/main/main.yml` | When `false`, skips YUM repo installation. Set to `false` in `all.vars` to use internal repos. |
| `offline_install_enabled` | `false` | `defaults/main/offline.yml` | Master switch for air-gapped install mode. |
| `offline_target_node_root` | `/var/tmp` | `defaults/main/offline.yml` | Root on target nodes for offline package staging. |
| `offline_control_node_root` | `{{ playbook_dir }}/files` | `defaults/main/offline.yml` | Root on control node where offline packages are staged. |
| `offline_itential_packages_path` | `itential_packages/{{ ansible_distribution \| lower }}_{{ ansible_distribution_major_version }}` | `defaults/main/offline.yml` | OS-specific subdirectory under the offline roots. |
| `common_required_repositories` | See `vars/main.yml` | `vars/main.yml` | List of required public repositories per component, consumed by `verify-connectivity.yml`. Keep in sync with the README table. |

## Dependencies / Assumptions

- The `common` role has no task dependencies.
- All other roles depend on `common` being applied first (typically via `role: itential.deployer.common` in the playbook before the component role).
- `verify-host.yml` requires `gather_facts: true` on the play (it uses `ansible_mounts`, `ansible_memtotal_mb`, `ansible_processor_vcpus`, `ansible_selinux`, etc.).

## Gotchas

- `offline_install_enabled` defaults to `false` here but the `download_packages_*` playbooks override it to `false` explicitly at the play level — the download playbooks always run online even when deploying to offline targets.
- The `common_itential_release_file` check in the `os` role skips OS package installation if the file already exists, making the `os` role effectively idempotent for re-runs.
- `verify-host.yml` uses `ignore_errors: true` on individual assertions and collects them, then does a final combined assert. This means a failing host will show all failures rather than stopping at the first.
- `verify-connectivity.yml`'s baseline check deliberately does NOT use `ansible.builtin.uri`'s `status_code: -1` — that is not a wildcard; `status_code` is a literal list of acceptable HTTP codes (default `[200]`). Instead it passes `status_code: "{{ range(100, 600) | list }}"` so any real HTTP response passes, and relies on `fetch_url` setting `status: -1` (which is never in that range) to detect genuine connection failures.
- `verify-connectivity.yml` deliberately avoids requiring the `git` binary (e.g. via `git ls-remote`) for the `gitlab.com`/`github.com` rows, since verification runs pre-install and `git` may not be installed on the target yet. It uses plain HTTPS `check_target` requests instead (a real gitlab.com group page, and a `codeload.github.com` tarball URL that also exercises the `github.com` → `codeload.github.com` redirect).
- `verify-results.yml` previously asserted on `platform_validation is not failed`, but nothing ever registered a variable by that name (Platform's own TLS checks register `platform_tls_dir_validation`/`platform_tls_contents_validation` instead) — this made `verify_redis`/`verify_mongodb`/`verify_platform` fail with "the 'failed' test expects a dictionary" on an undefined variable. It was replaced with `connectivity_validation is not failed`.
