# Overview

The playbook and role in this section are designed to run preflight checks on the hosts for Redis, Mongodb, Platform, and Gateway. These checks will determine if the host meets the minimum recommended system specifications for the given application.

# Preflight Role

## General information

The preflight role can be run separately to check the inventory host as well as when running the installation role for the other applications. By default, when installing an application using the deployer, the preflight role will not run. This behavior is controlled with the variables `preflight_run_checks` and `preflight_enforce_checks`. When `preflight_enforce_checks` is set to true, and any of the preflight checks fail, installation on the application will not proceed.

The following checks will be made against the host. 

| Check | Description | Cause Failure
| :---- | :---------- | :---------- 
| `OS`  | What version of Redhat/Rocky is installed on the host | Yes
| `CPU` | How many CPU cores the host has | Yes
| `RAM` | How many RAM the host has | Yes
| `Disk Space` | How much free disk space the host has | Yes
| `SELinux` | Is SELinxus being enforced | No
| `IPv6` | Is IPv6 configured | No
| `HTTP Proxy` | Is there an HTTP proxy | No
| `HTTPS Proxy` | Is there an HTTPS proxy | No
| `URLs` | Does the host have access to required URLs | No
| `AVX` | Is AVX supported (MongoDB only) | No

The preflight role will run checks against the hosts and then transfer the results into a local directory defined by the `preflight_directory` for review. 

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables, located in `roles/common_vars/defaults/main/preflight.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `preflight_directory` | `all` | String | Directory containing the results of the preflight checks  |`/tmp/preflight`
| `preflight_mounts` | `all` | String | Which mount to check for the storage requirment | `/`
| `env` | `all` | String | Which environment specs to check the host against `dev`/`staging`/`prod`   | `dev`
| `preflight_run_checks` | `all` | Boolean | Flag to run the preflight checks | `true`
| `preflight_enforce_checks` | `all` | Boolean | When true, a failed result of preflight checks will stop installation. When false, the installation will proceed  | `false`


# Building Your Inventory

The preflight checks will not run by default when installing the redis, mongodb, platform, and gateway applications. If a host fails, by default, the deployer will continue to install the application. This behavior can be controlled by setting variables in the inventory as shown below.

## Example Inventory

```
all:
    vars:
        iap_release: 2023.1
        preflight_directory: "/tmp/preflight"
        preflight_mounts: "/"
        preflight_env: dev
        preflight_run_checks: true
        preflight_enforce_checks: false

```

# Running the Playbook

To execute the preflight role, run the `preflight` playbook:

```
ansible-playbook itential.deployer.preflight -i <inventory>
```

To execute the preflight role on a specific host, run the `preflight_[[application]]` playbook:

```
ansible-playbook itential.deployer.preflight_redis -i <inventory>

ansible-playbook itential.deployer.preflight_mongodb -i <inventory>

ansible-playbook itential.deployer.preflight_platform -i <inventory>

ansible-playbook itential.deployer.preflight_gateway -i <inventory>
```
