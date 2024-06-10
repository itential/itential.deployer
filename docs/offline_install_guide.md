# Installing Itential in an Air-Gapped Environment

## Overview

It is not uncommon for customers to have production environments that are air-gapped for security reasons.  The Deployer contains playbooks that will download all required packages based on the Ansible inventory and operating system.  Those packages can then be used to install the components with the Deployer configured in offline mode.  Non air-gapped servers are required to download the dependent packages.

| Definitions       | Description |
| :---------------- | :---------- |
| Control Node      | The Ansible server.  This is the server where the Deployer is installed and where the inventory files are located. |
| Target Node       | The servers where the Itential components will be installed.  Sometimes also referred to as managed nodes. |
| Package Type      | A generic term for the downloaded artifacts.<br>YUM/DNF – rpms<br>Python – wheels<br> Zip files – archives<br>IAG archive – pkgs<br>IAP adapters – adapters |

## Offline Variables

The Deployer has various offline-related default variables (that can be overridden) and one variable that must be configured in the inventory.

### Default Variables

For each component, role variables are defined to specify where the packages are download on the control node and the target nodes.  These variables will work as-is and will not have to be specified in the inventory.  However, if the user would like to specify custom download directories, they may be overridden in the inventory.

### Root Variables

The root download directory on the control node and target nodes are defined in role variables.  The default control node download root directory is `files/itential_packages` in the Deployer playbooks directory.  The default root directory on the target nodes is `/var/tmp/itential_packages`.  The OS distribution (e.g. redhat) and the OS major version (e.g. 9) will be appended to the root directory.

For example, for a Redhat 9 installation, the control node root download directory will be `files/itential_packages/redhat_9`.  The root download directory on target nodes will be `/var/tmp/itential_packages/redhat_9`.

### Component Variables

Under the root download directory, there will be subdirectories for each component and package type on both the control node and target nodes.  Not all components have every package type.

For example, here is the directory structure on a target node for an All-in-one deployment (Redis, RabbitMQ, MongoDB, Vault and IAP) on a RedHat 9 server:

_Example: Directory Structure on Target Node - AIO_

```bash
itential_packages/
└── redhat_9
    └── 2023.1
        ├── iap
        │   ├── adapters
        │   │   ├── custom
        │   │   └── opensource
        │   ├── rpms
        │   └── wheels
        ├── mongodb
        │   ├── rpms
        │   └── wheels
        ├── os
        │   └── rpms
        ├── rabbitmq
        │   └── rpms
        ├── redis
        │   └── rpms
        └── vault
            └── rpms
```

Here is the directory structure on target node for a Gateway deployment on a Redhat 9 server:

_Example: Directory Structure on Target Node - Gateway_

```bash
itential_packages/
└── redhat_9
    └── 2023.1
        ├── iag
        │   ├── archives
        │   ├── pkgs
        │   ├── rpms
        │   └── wheels
        └── os
            └── rpms
```

And here is the directory structure on the control node:

_Example: Directory Structure on Control Node_

```bash
files/itential_packages
└── redhat_9
    └── 2023.1
        ├── iag
        │   ├── archives
        │   ├── pkgs
        │   ├── rpms
        │   └── wheels
        ├── iap
        │   ├── adapters
        │   │   ├── custom
        │   │   └── opensource
        │   ├── rpms
        │   └── wheels
        ├── mongodb
        │   ├── rpms
        │   └── wheels
        ├── os
        │   └── rpms
        ├── rabbitmq
        │   └── rpms
        ├── redis
        │   └── rpms
        └── vault
            └── rpms
```

### Offline Mode Variable

The `offline_install` variable must be defined in the inventory and set to true to run in offline mode, or passed on the command line using the `--extra-vars` option.

```yaml
all:
    vars:
        offline_install: true
```

## Running the Download Playbooks

The download playbooks must be executed on non air-gapped servers.  It is critical to use servers that have the same OS image as the target servers in the air-gapped environment.  Otherwise, the downloaded packages will not match, and the installation will most likely fail.  It is also highly recommended to use an image that has been updated with the latest RPMs.

When the download playbooks are executed, the relevant packages will first be downloaded to the target node and then copied to the control node.

Like the installation playbooks, there are download playbooks for each component.  The playbook are named `download-packages-<component>.yml`, for example, `download-packages-gateway.yml`.

For a basic execution, use the following command:

```bash
ansible-playbook itential.deployer.download_packages_<component> -i <inventory>
```

Note - Your installation might require additional options.

The download playbooks override the offline_install variable to false since they require YUM repos and certain packages to be installed.  This will allow users to define the offline_install variable in the inventory and set it to true and not have to remember to change the offline install setting between runs of the download playbooks and the installation playbooks.

## Running the Install Playbooks in Offline Mode

After all applicable download playbooks are executed, the normal install playbooks can be executed in offline mode.  

Once the offline_install variable is set to true, run the install playbooks as you normally would.  For example:

If `offline_install: true` is defined in the inventory.

```bash
ansible-playbook itential.deployer.<component> -i <inventory>
```
OR
```bash
ansible-playbook itential.deployer.<component> -i <inventory> --extra-vars "offline_install=true"
```

In offline mode, the install playbooks will use the packages downloaded to the control node instead of installing from the YUM/DNF, Python or NodeJS repositories, or from Git in the case of IAP adapters.  The packages are copied to the target nodes and placed in an Ansible temporary directory and installed locally.  The temporary directories are deleted automatically.

## Variable Reference

### Global

| Variable                              | Group | Type    | Description                                      | Default |
| :------------------------------------ | :---- | :------ | :----------------------------------------------- | :------ |
| `offline_install`                     | `all` | Boolean | Flag to enable offline install mode.             | N/A |
| `itential_packages_path`              | `all` | String  | Path appended to the root directory.             | `itential_packages/{{ ansible_distribution }}_{{ ansible_distribution_major_version }}` |
| `rpms_path`                           | `all` | String  | RPMs path.                                       | `{{ packages_path }}/rpms` |
| `wheels_path`                         | `all` | String  | Wheels path.                                     | `{{ packages_path }}/wheels` |
| `archives_path`                       | `all` | String  | Archives path.                                   | `{{ packages_path }}/archives` |
| `adapters_path`                       | `all` | String  | Adapters path.                                   | `{{ packages_path }}/adapters` |
| `packages_download_root_control_node` | `all` | String  | Root download directory on the control node.     | `{{ playbook_dir }}/files` |
| `packages_download_dir_control_node`  | `all` | String  | Download directory on the control node.          | `{{ packages_download_root_control_node }}/{{ packages_path }}` |
| `rpms_download_dir_control_node`      | `all` | String  | RPMs download directory on the control node.     | `{{ packages_download_dir_control_node }}/rpms` |
| `wheels_download_dir_control_node`    | `all` | String  | Wheels download directory on the control node.   | `{{ packages_download_dir_control_node }}/wheels`  |
| `archives_download_dir_control_node`  | `all` | String  | Archives download directory on the control node. | `{{ packages_download_dir_control_node }}/archives` |
| `adapters_download_dir_control_node`  | `all` | String  | Adapters download directory on the control node. | `{{ packages_download_dir_control_node }}/adapters` |
| `packages_download_root_target_node`  | `all` | String  | Download directory on the target node.           | `/var/tmp` |
| `packages_download_dir_target_node`   | `all` | String  | Root download directory on the target nodes.     | `{{ packages_download_root_target_node }}/{{ packages_path }}` |
| `rpms_download_dir_target_node`       | `all` | String  | RPMs download directory on the target nodes.     | `{{ packages_download_dir_target_node }}/rpms` |
| `wheels_download_dir_target_node`     | `all` | String  | Wheels download directory on the target nodes.   | `{{ packages_download_dir_target_node }}/wheels` |
| `archives_download_dir_target_node`   | `all` | String  | Archives download directory on the target node.  | `{{ packages_download_dir_target_node }}/archives` |
| `adapters_download_dir_target_node`   | `all` | String  | Adapters download directory on the target nodes. | `{{ packages_download_dir_target_node }}/adapters` |

### IAP

| Variable            | Group      | Type   | Description        | Default |
| :------------------ | :--------- | :----- | :----------------- | :------ |
| `iap_packages_path` | `platform` | String | IAP packages path. | `{{ itential_packages_path }}/{{ iap_release }}/iap` |

### IAG

| Variable            | Group     | Type   | Description        | Default |
| :------------------ | :-------- | :------| :----------------- | :------ |
| `iag_packages_path` | `gateway` | String | IAG packages path. | `{{ itential_packages_path }}/{{ iag_release }}/iag` |

### MongoDB

| Variable                | Group     | Type   | Description            | Default |
| :---------------------- | :-------- | :----- | :--------------------- | :------ |
| `mongodb_packages_path` | `mongodb` | String | MongoDB packages path. | `{{ itential_packages_path }}/{{ iap_release }}/mongodb` |

### OS

| Variable           | Group | Type   | Description       | Default |
| :----------------- | :---- | :----- | :---------------- | :------ |
| `os_packages_path` | `all` | String | OS packages path. | `{{ itential_packages_path }}/{{ iap_release }}/os` |

### RabbitMQ

| Variable                 | Group | Type   | Description             | Default |
| :----------------------- | :---- | :----- | :---------------------- | :------ |
| `rabbitmq_packages_path` | `all` | String | RabbitMQ packages path. | `{{ itential_packages_path }}/{{ iap_release }}/rabbitmq` |

### Redis

| Variable              | Group | Type   | Description          | Default |
| :-------------------- | :---- | :----- | :------------------- | :------ |
| `redis_packages_path` | `all` | String | Redis packages path. | `{{ itential_packages_path }}/{{ iap_release }}/redis` |

### Vault

| Variable              | Group | Type   | Description          | Default |
| :-------------------- | :---- | :----- | :------------------- | :------ |
| `vault_packages_path` | `all` | String | Vault packages path. | `{{ itential_packages_path }}/{{ iap_release }}/vault` |
