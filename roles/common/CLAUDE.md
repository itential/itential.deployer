# Role: common

## Purpose

Provides shared default variables consumed by all other roles. Has no `main.yml` task entry point — it is imported by playbooks solely to inject its defaults into the variable scope. Also contains the shared `verify-host.yml` task file used by the `verify_*` playbooks.

## Entry Point Tasks

There is no `tasks/main.yml`. The only task file is:

- `tasks/verify-host.yml` — imported by `verify_redis`, `verify_mongodb`, and `verify_platform` task files via `tasks_from:`. It is not called by any role's `main.yml`.

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

## Key Variables

| Variable | Default | Source File | Purpose |
|----------|---------|-------------|---------|
| `common_itential_release_file` | `/etc/itential-release` | `defaults/main/main.yml` | Path to file tracking installed component versions. Written by each role after install. |
| `common_install_yum_repos` | `true` | `defaults/main/main.yml` | When `false`, skips YUM repo installation. Set to `false` in `all.vars` to use internal repos. |
| `offline_install_enabled` | `false` | `defaults/main/offline.yml` | Master switch for air-gapped install mode. |
| `offline_target_node_root` | `/var/tmp` | `defaults/main/offline.yml` | Root on target nodes for offline package staging. |
| `offline_control_node_root` | `{{ playbook_dir }}/files` | `defaults/main/offline.yml` | Root on control node where offline packages are staged. |
| `offline_itential_packages_path` | `itential_packages/{{ ansible_distribution \| lower }}_{{ ansible_distribution_major_version }}` | `defaults/main/offline.yml` | OS-specific subdirectory under the offline roots. |

## Dependencies / Assumptions

- The `common` role has no task dependencies.
- All other roles depend on `common` being applied first (typically via `role: itential.deployer.common` in the playbook before the component role).
- `verify-host.yml` requires `gather_facts: true` on the play (it uses `ansible_mounts`, `ansible_memtotal_mb`, `ansible_processor_vcpus`, `ansible_selinux`, etc.).

## Gotchas

- `offline_install_enabled` defaults to `false` here but the `download_packages_*` playbooks override it to `false` explicitly at the play level — the download playbooks always run online even when deploying to offline targets.
- The `common_itential_release_file` check in the `os` role skips OS package installation if the file already exists, making the `os` role effectively idempotent for re-runs.
- `verify-host.yml` uses `ignore_errors: true` on individual assertions and collects them, then does a final combined assert. This means a failing host will show all failures rather than stopping at the first.
