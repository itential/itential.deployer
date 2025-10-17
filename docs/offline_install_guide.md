# Installing Itential in an Air-Gapped Environment

## Overview

It is not uncommon for customers to have environments that are air-gapped for security reasons.
The Deployer contains playbooks that will download all required packages based on the Ansible
inventory and operating system.  Those packages can then be used to install the components with
the Deployer configured in offline mode.  A single, non air-gapped server is required to download
the dependent packages.

| Definitions       | Description |
| :---------------- | :---------- |
| Control Node      | The Ansible server.  This is the server where the Deployer is installed and where the inventory files are located. |
| Target Node       | The server where the Itential components will be installed.  Sometimes also referred to as a managed node. |
| Package Type      | A generic term for the downloaded artifacts. YUM/DNF – RPMs, Python – wheels, Zip files – archives, IAG archive – pkgs, Itential Platform adapters – adapters, Ansible Collections - collections |

## Running the Download Playbooks

The download playbooks must be executed on a non air-gapped server.  It is critical to use a server
that has the same OS image as the Target Servers in the air-gapped environment.  Otherwise, the
downloaded packages will not match, and the installation will most likely fail.  It is also highly
recommended to use an image that has been updated with the latest RPMs.

When the download playbooks are executed, all relevant packages will first be downloaded to the
Target Node and then copied to the Control Node.

Like the installation playbooks, there are download playbooks for each component.  The playbooks
are named `download_packages_<component>.yml`, for example, `download_packages_gateway.yml`.

For a basic execution, use the following command:

```bash
ansible-playbook itential.deployer.download_packages_<component> -i <inventory>
```

**&#9432; Note:**
Your installation might require additional options.

The download playbooks override the `offline_install_enabled` variable to `false` since they
require YUM repos and certain packages to be installed.  This will allow users to define the
`offline_install_enabled` variable in the inventory and set it to `true` and not have to remember
to change the offline install setting between runs of the download playbooks and the installation
playbooks.

### Target Node Download Directory Structure

By default, the download playbooks will put the artifacts in `/var/tmp/itential_packages` on the
Target Node.

This is an example directory structure on a Target Node on a RedHat 9 server:

#### Example: Directory Structure on Target Node

```bash
/var/tmp/itential_packages
└── rocky_9
    ├── 2023.1
    │   └── gateway
    │       ├── collections
    │       ├── rpms
    │       └── wheels
    │           ├── app
    │           └── base
    └── 6
        ├── mongodb
        │   ├── rpms
        │   └── wheels
        │       ├── app
        │       └── base
        ├── os
        │   └── rpms
        ├── platform
        │   ├── adapters
        │   ├── rpms
        │   │   ├── dependencies
        │   │   ├── nodejs
        │   │   ├── platform
        │   │   └── python
        │   └── wheels
        │       ├── app
        │       └── base
        ├── redis
        │   ├── archives
        │   └── rpms
        │       └── build
        └── vault
            └── rpms
```

### Control Node Download Directory Structure

By default, the download playbooks will copy the artifacts to `playbooks/files/itential_packages`
on the Control Node.  This directory is relative where the Deployer is installed.

This is an example directory structure on the Control Node:

#### Example: Directory Structure on Control Node

```bash
playbooks/files/itential_packages
└── rocky_9
    ├── 2023.1
    │   └── gateway
    │       ├── collections
    │       ├── rpms
    │       └── wheels
    │           ├── app
    │           └── base
    └── 6
        ├── mongodb
        │   ├── rpms
        │   └── wheels
        │       ├── app
        │       └── base
        ├── os
        │   └── rpms
        ├── platform
        │   ├── adapters
        │   ├── rpms
        │   │   ├── dependencies
        │   │   ├── nodejs
        │   │   ├── platform
        │   │   └── python
        │   └── wheels
        │       ├── app
        │       └── base
        ├── redis
        │   ├── archives
        │   └── rpms
        │       └── build
        └── vault
            └── rpms
```

## Running the Install Playbooks in Offline Mode

### Copying Artifacts to Air-gapped Environment

After all applicable download playbooks are executed, the entire
`playbooks/files/itential_packages` directory from the non air-gapped Control Node must be
archived, copied to the Control Node in the air-gapped environment, and unarchived before running
the install playbooks.

### Defining the Inventory

The `offline_install_enabled` variable must be defined in the inventory and set to `true` to run
in offline mode, or passed on the command line using the `--extra-vars` option.

```yaml
all:
  vars:
    offline_install_enabled: true
```

### Running the Playbooks

After the artifacts are copied to the Control Node in the air-gapped environment, the install
playbooks can be executed in offline mode.

If the `offline_install_enabled` flag is set to `true` in the inventory, run the install playbooks
as you normally would.  For example:

```bash
ansible-playbook itential.deployer.<component> -i <inventory>
```

If the `offline_install_enabled` flag is not defined in the inventory, it must be passed as a
command line argument.  For example:

```bash
ansible-playbook itential.deployer.<component> -i <inventory> --extra-vars "offline_install_enabled=true"
```

In offline mode, the install playbooks will use the packages on the Control Node in the air-gapped
environment instead of installing from the YUM/DNF, Python or NodeJS repositories, from Git
(Itential Platform adapters) or from Ansible Galaxy.  The packages are copied to the Target Nodes
and placed in a temporary directory and installed locally.  The temporary directories are deleted
automatically.

## Variable Reference

All variables defined in this section work out of the box and won't need to be overridden in the
inventory in most cases.  If the user wants to use different download directories, they can be
overridden by setting the `offline_target_node_root` or `offline_control_node_root` variables in
the inventory.

### Global

The following variables are global for all roles.

| Variable | Type | Description | Default |
| :------- | :--- | :---------- | :------ |
| `offline_target_node_root` | String | Root directory on the target node where required packages are downloaded to by the download playbooks. | `/var/tmp` |
| `offline_control_node_root` | String | Root directory on the control node where required packages are downloaded to by the download playbooks and where the packages are uploaded from when installing in offline mode. | `{{ playbook_dir }}/files` |
| `offline_itential_packages_path` | String | Path appended to the root directory | `itential_packages/{{ ansible_distribution }}_{{ ansible_distribution_major_version }}` |

### Itential Platform

The following variables are defined in the `platform` role.

| Variable | Type   | Description | Default |
| :------- | :----- | :---------- | :------ |
| `platform_offline_packages_root` | String | Platform packages root directory | `{{ offline_itential_packages_path }}/{{ platform_release }}/platform` |
| `platform_offline_target_node_root` | String | Platform target node root directory | `{{ offline_target_node_root }}/{{ platform_offline_packages_root }}` |
| `platform_offline_control_node_root` | String | Platform control node root directory | `{{ offline_control_node_root }}/{{ platform_offline_packages_root }}` |
| `platform_offline_target_node_rpms_dir` | String | Platform target node RPMs directory | `{{ platform_offline_target_node_root }}/rpms` |
| `platform_offline_target_node_wheels_dir` | String | Platform target node wheels directory | `{{ platform_offline_target_node_root }}/wheels` |
| `platform_offline_target_node_adapters_dir` | String | Platform target node adapters directory | `{{ platform_offline_target_node_root }}/adapters` |
| `platform_offline_control_node_rpms_dir` | String | Platform control node RPMs directory | `{{ platform_offline_control_node_root }}/rpms` |
| `platform_offline_control_node_wheels_dir` | String | Platform control node wheels directory | `{{ platform_offline_control_node_root }}/wheels` |
| `platform_offline_control_node_adapters_dir` | String | Platform control node adapters directory | `{{ platform_offline_control_node_root }}/adapters` |

### Itential Gateway

The following variables are defined in the `gateway` role.

| Variable | Type | Description | Default |
| :------- | :--- | :---------- | :------ |
| `gateway_offline_packages_root` | String | Gateway packages root directory | `{{ offline_itential_packages_path }}/{{ iag_release }}/gateway` |
| `gateway_target_node_root` | String | Gateway target node root directory | `{{ offline_target_node_root }}/{{ gateway_offline_packages_root }}` |
| `gateway_control_node_root` | String | Gateway control node root directory | `{{ offline_control_node_root }}/{{ gateway_offline_packages_root }}` |
| `gateway_offline_target_node_rpms_dir` | String | Gateway target node RPMs directory | `{{ gateway_target_node_root }}/rpms` |
| `gateway_offline_target_node_wheels_dir` | String | Gateway target node wheels directory | `{{ gateway_target_node_root }}/wheels` |
| `gateway_offline_target_node_archives_dir` | String | Gateway target node archives directory | `{{ gateway_target_node_root }}/archives` |
| `gateway_offline_target_node_collections_dir` | String | Gateway target node collections directory | `{{ gateway_target_node_root }}/collections` |
| `gateway_offline_control_node_rpms_dir` | String | Gateway control node RPMs directory | `{{ gateway_control_node_root }}/rpms` |
| `gateway_offline_control_node_wheels_dir` | String | Gateway control node wheels directory | `{{ gateway_control_node_root }}/wheels` |
| `gateway_offline_control_node_archives_dir` | String | Gateway control node archives directory | `{{ gateway_control_node_root }}/archives` |
| `gateway_offline_control_node_collections_dir` | String | Gateway control node collections directory | `{{ gateway_control_node_root }}/collections` |

### MongoDB

The following variables are defined in the `mongodb` role.

| Variable | Type | Description | Default |
| :------- | :--- | :---------- | :------ |
| `mongodb_offline_packages_root` | String | MongoDB packages root directory | `{{ offline_itential_packages_path }}/{{ platform_release }}/mongodb` |
| `mongodb_offline_target_node_root` | String | MongoDB target node root directory | `{{ offline_target_node_root }}/{{ mongodb_offline_packages_root }}` |
| `mongodb_offline_control_node_root` | String |MongoDB control node root directory | `{{ offline_control_node_root }}/{{ mongodb_offline_packages_root }}` |
| `mongodb_offline_target_node_rpms_dir` | String | MongoDB target node RPMs directory | `{{ mongodb_offline_target_node_root }}/rpms` |
| `mongodb_offline_target_node_wheels_dir` | String | MongoDB target node wheels directory | `{{ mongodb_offline_target_node_root }}/wheels` |
| `mongodb_offline_control_node_rpms_dir` | String |MongoDB control node RPMs directory | `{{ mongodb_offline_control_node_root }}/rpms` |
| `mongodb_offline_control_node_wheels_dir` | String | MongoDB control node wheels directory | `{{ mongodb_offline_control_node_root }}/wheels` |

### OS

The following variables are defined in the `os` role.

| Variable | Type | Description | Default |
| :------- | :--- | :---------- | :------ |
| `os_offline_packages_root` | String | OS packages root directory | `{{ offline_itential_packages_path }}/{{ platform_release }}/os` |
| `os_offline_target_node_root` | String | OS target node root directory | `{{ offline_target_node_root }}/{{ os_offline_packages_root }}` |
| `os_offline_control_node_root` | String | OS control node root directory | `{{ offline_control_node_root }}/{{ os_offline_packages_root }}` |
| `os_offline_target_node_rpms_dir` | String | OS target node RPMs directory | `{{ os_offline_target_node_root }}/rpms` |
| `os_offline_control_node_rpms_dir` | String | OS control node RPMs directory | `{{ os_offline_control_node_root }}/rpms` |

### Redis

The following variables are defined in the `redis` role.

| Variable | Type | Description | Default |
| :------- | :--- | :---------- | :------ |
| `redis_offline_packages_root` | String | Redis packages root directory | `{{ offline_itential_packages_path }}/{{ platform_release }}/redis` |
| `redis_offline_target_node_root` | String | Redis target node root directory | `{{ offline_target_node_root }}/{{ redis_offline_packages_root }}` |
| `redis_offline_control_node_root` | String | Redis control node root directory | `{{ offline_control_node_root }}/{{ redis_offline_packages_root }}` |
| `redis_offline_target_node_rpms_dir` | String | Redis target node RPMs directory | `{{ redis_offline_target_node_root }}/rpms` |
| `redis_offline_target_node_archives_dir` | String | Redis target node archives directory | `{{ redis_offline_target_node_root }}/archives` |
| `redis_offline_control_node_rpms_dir` | String | Redis control node RPMs directory | `{{ redis_offline_control_node_root }}/rpms` |
| `redis_offline_control_node_archives_dir` | String | Redis control node archives directory | `{{ redis_offline_control_node_root }}/archives` |

### Vault

The following variables are defined in the `vault` role.

| Variable | Type | Description | Default |
| :------- | :--- | :---------- | :------ |
| `vault_offline_packages_root` | String | Vault packages root directory | `{{ offline_itential_packages_path }}/{{ platform_release }}/vault` |
| `vault_offline_target_node_root` | String | Vault target node root directory | `{{ offline_target_node_root }}/{{ vault_offline_packages_root }}` |
| `vault_offline_control_node_root` | String | Vault control node root directory | `{{ offline_control_node_root }}/{{ vault_offline_packages_root }}` |
| `vault_offline_target_node_rpms_dir` | String | Vault target node RPMs directory | `{{ vault_offline_target_node_root }}/rpms` |
| `vault_offline_control_node_rpms_dir` | String | Vault control node RPMs directory | `{{ vault_offline_control_node_root }}/rpms` |
