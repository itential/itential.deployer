# Role: python

## Purpose

Shared utility role for installing Python RPM packages and pip dependencies. Not called directly by playbooks — it is included by `gateway`, `mongodb`, and `platform` roles via `include_tasks` or `import_role`. Has no defaults of its own; all variables must be passed by the caller.

## Entry Point Tasks — main.yml

1. Install Python RPM packages via `dnf` using `python_packages` list (skipped when `offline_install_enabled` is true — callers handle offline Python install themselves)

### install-dependencies.yml

Called separately from `main.yml` by caller roles. Installs pip packages into either a virtualenv or via a pip executable.

1. Assert that `python_pip_executable` or `python_venv` is defined
2. If `python_venv` is defined: install `python_base_dependencies` then `python_app_dependencies` into the venv using `ansible.builtin.pip`
3. If `python_pip_executable` is defined (and no venv): install `python_base_dependencies` then `python_app_dependencies` using that pip executable with `umask 0022`

### create-symlinks.yml

Creates symlinks for python and pip executables. Called by callers that need to set up `/usr/bin/python<N>` symlinks.

## Variables (all must be provided by the caller)

| Variable | Purpose |
|----------|---------|
| `python_packages` | List of RPM package names to install (e.g., `python39`, `python39-pip`) |
| `python_base_dependencies` | List of base pip packages (e.g., `pip`, `setuptools`, `wheel`) |
| `python_app_dependencies` | List of application-specific pip packages |
| `python_pip_executable` | Absolute path to pip executable (e.g., `/usr/bin/pip3.11`) |
| `python_venv` | Absolute path to a Python virtualenv (mutually exclusive with `python_pip_executable`) |
| `offline_install_enabled` | Inherited from `common` defaults; controls whether `main.yml` installs packages |

## How Callers Use This Role

Each component role maps its own vars to the generic python vars when calling:

| Caller Role | `python_packages` source | `python_pip_executable` source | venv? |
|-------------|-------------------------|-------------------------------|-------|
| `gateway` | `gateway_python_packages` | `gateway_pip_executable` | Yes (`gateway_python_venv`) |
| `mongodb` | `mongodb_python_packages` | `mongodb_pip_executable` | Yes (`mongodb_python_venv`) |
| `platform` | `platform_python_packages` | `platform_pip_executable` | No (system pip) |

## Gotchas

- `main.yml` only installs RPM packages; it does not call `install-dependencies.yml`. Callers must explicitly call `install-dependencies.yml` as a separate step.
- `install-dependencies.yml` requires either `python_pip_executable` or `python_venv` — if neither is passed it fails immediately with an assert.
- The role has no `defaults/` directory. Calling it without the required variables set will produce unclear errors.
