# Role: python

## Purpose

Shared utility role for installing Python RPM packages and pip dependencies. Not called directly by playbooks — it is included by `gateway`, `mongodb`, and `platform` roles via `include_tasks` or `import_role`. Has no defaults of its own; all variables must be passed by the caller.

## Entry Point Tasks — main.yml

1. Install Python RPM packages via `dnf` using `python_packages` list (skipped when `offline_install_enabled` is true — callers handle offline Python install themselves)

### install-dependencies.yml

Called separately from `main.yml` by caller roles. Installs pip packages into either a virtualenv or via a pip executable.

1. Assert that `python_pip_executable` or `python_venv` is defined
2. If `python_venv` is defined: install `python_base_dependencies` then `python_app_dependencies` into the venv using `ansible.builtin.pip`
3. If `python_pip_executable` is defined (and no venv): install `python_base_dependencies` then `python_app_dependencies` using that pip executable with `umask 0022`. When the caller passes `python_pip_become_user`, these two tasks run as that user (`become_user`) instead of the play's default (root), with `--user` added to `extra_args` so packages land in that user's own site-packages rather than the system-wide location. Undefined by default (`default(omit)`), so callers that don't pass it keep today's root/global-install behavior unchanged — currently only `platform` passes it.

### validate-dependencies.yml

Not called automatically by `install-dependencies.yml` — callers that want post-install verification include it as a separate step. Derives an import name from each `python_app_dependencies` pip spec (strips a `==`-style version pin; does not handle pip names that differ from their import name, e.g. `PyYAML` → `yaml`) and runs `python_executable -c "import <name>"` for each, as `python_validate_become_user` if passed (same `default(omit)` pattern as `install-dependencies.yml`). Fails the play if any import fails. Currently only called by `platform`.

## Variables (all must be provided by the caller)

| Variable | Purpose |
|----------|---------|
| `python_packages` | List of RPM package names to install (e.g., `python39`, `python39-pip`) |
| `python_base_dependencies` | List of base pip packages (e.g., `pip`, `setuptools`, `wheel`) |
| `python_app_dependencies` | List of application-specific pip packages (as pip install specs, e.g. `jinja2==3.1.2`) |
| `python_pip_executable` | Absolute path to pip executable (e.g., `/usr/bin/pip3.11`) |
| `python_venv` | Absolute path to a Python virtualenv (mutually exclusive with `python_pip_executable`) |
| `python_pip_become_user` | Optional (`install-dependencies.yml`, pip-executable branch only). When set, installs as this user with `pip install --user` instead of system-wide as root. |
| `python_executable` | Absolute path to the python interpreter (`validate-dependencies.yml` only) |
| `python_validate_become_user` | Optional (`validate-dependencies.yml` only). User to run the import checks as. |
| `offline_install_enabled` | Inherited from `common` defaults; controls whether `main.yml` installs packages |

## How Callers Use This Role

Each component role maps its own vars to the generic python vars when calling:

| Caller Role | `python_packages` source | `python_pip_executable` source | venv? | `python_pip_become_user`? |
|-------------|-------------------------|-------------------------------|-------|----------------------------|
| `gateway` | `gateway_python_packages` | `gateway_pip_executable` | Yes (`gateway_python_venv`) | n/a (venv branch) |
| `mongodb` | `mongodb_python_packages` | `mongodb_pip_executable` | Yes (`mongodb_python_venv`) | n/a (venv branch) |
| `platform` | `platform_python_packages` | `platform_pip_executable` | No (system pip) | Yes — `platform_user` (`itential`) |

## Gotchas

- `main.yml` only installs RPM packages; it does not call `install-dependencies.yml`. Callers must explicitly call `install-dependencies.yml` as a separate step.
- `install-dependencies.yml` requires either `python_pip_executable` or `python_venv` — if neither is passed it fails immediately with an assert.
- The role has no `defaults/` directory. Calling it without the required variables set will produce unclear errors.
- `python_pip_become_user`/`python_validate_become_user` only affect the pip-executable branch of `install-dependencies.yml` (and `validate-dependencies.yml` respectively) — `gateway` and `mongodb` use the venv branch, which is unaffected either way.
