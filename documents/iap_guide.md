# Overview

The playbook and roles in this section install and configure IAP for the Itential Automation Platform.  There are currently three IAP-related roles:

* `platform` – Installs IAP and performs a base configuration.
* `platform_adapters` – Installs IAP adapters.
* `platform_app_artifact` – Installs IAP App Artifact.

# Roles

## Platform Role

The `platform` role performs a base install of IAP including any OS packages required. It includes the appropriate version of Python, Pip, Jinja, and TextFSM. It handles a few security vulnerabilities. It creates the appropriate Linux users, directories, log files, and systemd services. It will start the automation-platform service when complete.

## Platform Adapters Role

The `platform_adapters` role will install the source code for each adapter that is listed.  It will also install any listed custom applications assuming the Ansible controller has access to the listed Git repos.  It will restart the automation-platform service when complete.

## Platform App Artifact Role

The `platform_app_artifact` role will install app-artifacts, which is an optional Itential application that is primarily used only in development environments for packaging use cases together for deployment. It will restart the automation-platform service when complete.

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time based on the IAP release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Global Variables

The variables in this section are configured in the inventory in the `all` group vars.

| Variable | Group | Type | Description | Default Value | Required?
| :------- | :---- | :--- | :---------- | :------------ | :--------
| `iap_release` | `all` | Fixed-point | Designates the IAP major version. | N/A | Yes
| `mongo_root_ca_file_source` | `all` | String | The name of the MongoDB Root CA file.| N/A | No

The `iap_release` must be defined in the inventory.  This variable, along with the OS major version, is used to determine the static variables.

## Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables that are shared between the Platform-related roles, located in `roles/common_vars/defaults/main/iap.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `itential_root_ca_file_destination` | `all` | String | The location of the Root CA file for MongoDB. | `/opt/itential/keys/mongo-rootCA.pem`

## Platform Role Variables

The variables in this section may be overridden in the inventory in the `platform` group vars.

| Variable | Group | Type | Description | Default Value | Required?
| :------- | :---- | :--- | :---------- | :------------ | :--------
| `iap_bin_file` | `platform` | String | The name of the IAP bin file. | N/A | Yes*
| `iap_tar_file` | `platform` | String | The name of the IAP tar file. | N/A | Yes*

Either `iap_bin_file` or `iap_tar_file` must be defined in the inventory, but not both.


The following table lists the default variables located in `roles/platform/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `iap_install_dir` | `platform` | String | The IAP installation directory. | `/opt/itential`
| `iap_log_dir` | `platform` | String | The IAP log directory. | `/var/log/itential`
| `iap_https` | `platform` | Boolean | Flag to enable HTTPS. | `false`
| `iap_http_port` | `platform` | Integer | The IAP HTTP listen port. | `3000`
| `iap_https_port` | `platform` | Integer | The IAP HTTPS listen port. | `3443`
| `configure_iap` | `platform` | Boolean | Flag to enabled adding default configurations in MongoDB. | `true`
| `configure_iag_adapters` | `platform` | String | Flag to enable automatically configuring IAG adapters. | `true`
| `iap_user` | `platform` | String | The IAP Linux user. | `itential`
| `iap_group` | `platform` | String | The IAP Linux group. | `itential`
| `vault_install_dir` | `platform` | String | The location of the Vault installation directory. | `/opt/vault`
| `process_tasks_on_start` | `platform` | Boolean | Flag to enable processing tasks on startup. | `true`
| `process_jobs_on_start` | `platform` | Boolean | Flag to enable processing jobs on startup. | `true`
| `upload_using_rsync` | `platform` | Boolean | Flag to enable using rsync to upload artifacts.  <br>When set to `true`, rsync will be used.  <br>When set to `false`, secure copy will be used. | `false`
| `mongo_backup` | `platform` | Boolean | Flag to enable performing a MongoDB backup when upgrading IAP. | `true`
| `remove_iap_source_file` | `platform` | Boolean | Flag to remove the bin/tar file when finished. | `true`

## Platform Adapters Role Variables

The variables in this section may be overridden in the inventory in the `platform` group vars.

The following table lists the default variables located in `roles/platform_adapters/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `itential_adapters` | `platform` | List of Strings | The URLs of the Itental adapter Git repos. | N/A
| `delete_package_lock_file` | `platform` | Boolean | Flag to enable deletion of NPM package lock file before installing NPM module. | `false`
| `disable_git_safe_repo_check` | `platform` | Boolean | Flag to disable the Git safe repo check. | `false`
| `npm_ignore_scripts` | `platform` | Boolean | Flag to enable ignoring the scripts when installing NPM modules. | `false`

## Platform App Artifacts Role Variables

The variables in this section may be overridden in the inventory in the `platform` group vars.

The following table lists the default variables located in `roles/platform_app_artifact/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `app_artifact` | `platform` | Boolean | Flag for enabling the installation of App Artifact. | `false`
| `app_artifact_source_file` | `platform` | String | The name of the App-Artifact archive.  The archive must be placed in the `files` directory. | N/A

# Building the Inventory

To install and configure IAP, add a `platform` group and host(s) to your inventory and configure the `iap_release` and either `iap_bin_file` or `iap_tar_file`.  The following inventory shows a basic IAP configuration with a single IAP node.

## Example Inventory - Single IAP Node

```
all:
    vars:
        iap_release: 2023.1

    children:
        platform:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                iap_bin_file: <bin-file>
```

To install Itential adapters, add the `platform_adapters` flag to the `platform` group and set it to `true`, and configure the adapters in the `itential_adapters` variable.  You may also need to configure the `delete_package_lock_file`, `disable_git_safe_repo_checks` and `npm_ignore_scripts` flags and set them to `true`.

## Example Inventory - Install Itential Adapters

```
all:
    vars:
        iap_release: 2023.1

    children:
        platform:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                iap_bin_file: <bin-file>
                platform_adapters: true
                itential_adapters:
                    - <git_repo1>
                    - <git_repo2>
                    - <git_repoN>
                delete_package_lock_file: true
                disable_git_safe_repo_checks: true
                npm_ignore_scripts: true
```

To install App-Artifacts, add the `app_artifact` flag to the `platform` group and set it to `true` and configure the `app_artifact_source_file`.

## Example Inventory - Install App-Artifact

```
all:
    vars:
        iap_release: 2023.1

    children:
        platform:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                iap_bin_file: <bin-file>
                app_artifact: true
                app_artifact_source_file: <archive1>
```

# Running the Playbook

To execute all Platform roles, run the `itential.deployer.iap` playbook:

```
ansible-playbook itential.deployer.iap -i <inventory>
```

You can also run select IAP roles by using the following tags:

* `platform_install`
* `platform_adapters`
* `platform_app_artifact`

To execute only the `platform` role, run the `itential.deployer.iap` playbook with the `platform_install` tag:

```
ansible-playbook itential.deployer.iap -i <inventory> --tags platform_install
```

To execute only the `platform_adapters` role, run the `itential.deployer.iap` playbook with the `platform_adapters` tag:

```
ansible-playbook itential.deployer.iap -i <inventory> --tags platform_adapters
```

To execute only the `platform_app_artifact` role, run the `itential.deployer.iap` playbook with the `platform_app_artifact` tag:

```
ansible-playbook itential.deployer.iap -i <inventory> --tags platform_app_artifact
```
