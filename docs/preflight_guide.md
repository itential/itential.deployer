# Overview

The playbook and role in this section are designed to run preflight checks on the hosts for Redis, Mongodb, Platform, and Gateway. These checks will determine if the host meets the minimum recomended system specifications for the given application.

# Preflight Role

## General information

This role can be run seperatly to check the inventory host as well as when running the installtion role for the other applications. By default, when installing an application using the deployer, the preflight role will run however, it will ignore the results so the application will still be installed. This behaviour is controlled with the variables `run_preflight` and `ignore_preflight_checks`. When `ignore_preflight_checks` is set to false, and any of the preflight checks fail, installition on the application will not preceed.

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
| `Ports` | Are ports needed for the application blocked by firewalls | No
| `URLs` | Does the host have access to required URLs | No
| `AVX` | Is AVX supported (MongoDB only) | No

The preflight role will run checks against the hosts and then trasfer the results into a local directory defined by the `preflight_directory` for review. 

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables that are shared between the Redis-related roles, located in `roles/common_vars/defaults/main/preflight.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `preflight_directory` | `all` | String | Directory containing the results of the preflight checks  |`/tmp/preflight`
| `mount` | `all` | String | Which mount to check for the storage requirment | `/`
| `env` | `all` | String | Which environment specs to check the host against `dev`/`staging`/`prod`   | `dev`
| `run_preflight` | `all` | Boolean | Flag to run the preflight checks | `true`
| `ignore_preflight_checks` | `all` | Boolean | Ignore a failed result of preflight checks and proceed with installation  | `true`


# Building Your Inventory

To install and configure Redis, add a `redis` group and host(s) to your inventory.  The following inventory shows a basic Redis configuration with a single Redis node with no authentication.

## Example Inventory - Single Redis Node

```
all:
    vars:
        iap_release: 2023.1
        preflight_directory: "/tmp/preflight"
        mount: "/"
        env: dev
        run_preflight: true
        ignore_preflight_checks: true

```

# Running the Playbook

To execute the preflight role, run the `preflight` playbook:

```
ansible-playbook itential.deployer.preflight -i <inventory>
```
