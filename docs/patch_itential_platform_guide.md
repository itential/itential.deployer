# Overview

The Itential Deployer supports patch upgrades for Itential Platform.  These are also referred to as
monthly releases.  For example, if Itential Platform version 2023.1.1 is currently installed, it
could be upgraded to any 2023.1.X version.  The patch upgrade playbook **DOES NOT** support major
upgrades.  For major upgrades, please work with your Itential Professional Services representative.

# Requirements

In order to run the Patch Itential Platform playbook, the `jmespath` Python module must be
installed on the **Ansible Control Node**.

# Procedure

## Download the Itential Platform Artifact

The Itential Platform artifacts are hosted on the Itential Nexus repository. Please contact your
Itential Professional Services representative to get the proper credentials, locations of the
artifacts and instructions for downloading.  Download the new artifact and place it in the `files`
directory.

## Update Inventory Variables

Next, update the inventory variables.  It is recommended that the inventory used during the original
 Itential Platform install is used as the baseline.  Update the `platform_bin_file` or
 `platform_tar_file` to the new version.  It is highly recommended to take a backup of MongoDB
 before patching. For more information: https://www.mongodb.com/docs/database-tools/mongodump/

_Example: Original Inventory_

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    platform:
      hosts:
        cluster6-aio01:
          ansible_host: 172.16.37.185
      vars:
        platform_bin_file: itential-premium_2023.1.1.linux.x86_64.bin
```

_Example: Patch Upgrade Inventory_

```yaml
all:
  vars:
    platform_release: 2023.1

  children:
    platform:
      hosts:
        cluster6-aio01:
          ansible_host: 172.16.37.185
      vars:
        platform_bin_file: itential-premium_2023.1.5.linux.x86_64.bin
```

## Run Patch Itential Platform Playbook

Finally, run the `patch_platform` playbook.

```bash
$ ansible-playbook itential.deployer.patch_platform -i <inventory>
```