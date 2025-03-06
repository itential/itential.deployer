# Overview

The Itential Deployer supports patch upgrades for Itential Platform.  These are also referred to as
monthly releases.  For example, if Itential Platform version 6.0.0 is currently installed, it
could be upgraded to any 6.0.X version.  The patch upgrade playbook **DOES NOT** support major
upgrades.  For major upgrades, please work with your Itential Professional Services representative.

# Requirements

In order to run the Patch Itential Platform playbook, the `jmespath` Python module must be
installed on the **Ansible Control Node**.

# Procedure

## Download the Itential Platform Packages

The Itential Platform packages are hosted on the Itential Nexus repository. Please contact your
Itential Professional Services representative to get the proper credentials, locations of the
packages and instructions for downloading.  Download the new packages and place them in the 
`playbooks/files` directory.

**&#9432; Note:**
Nexus URLs are also supported in `platform_packages`.

## Update Inventory Variables

Next, update the inventory variables.  It is recommended that the inventory used during the original
Itential Platform install is used as the baseline.  Update the `platform_release` to the desired
version and update the `platform_packages` appropriately. It is highly recommended to take a backup
of MongoDB before patching. For more information:

https://www.mongodb.com/docs/database-tools/mongodump/

_Example: Original Inventory_

```yaml
all:
  children:
    platform:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_release: 6.0
        platform_redis_host: redis1.example.com
        platform_mongo_url: mongodb://itential:password@mongo1.example.com:27017/itential
        platform_packages:
          - itential-platform-6.0.0-rc.noarch.rpm
          - itential-lifecycle_manager-6.0.0-rc.noarch.rpm
          - itential-configuration_manager-6.0.0-rc.noarch.rpm
          - itential-service_management-6.0.0-rc1.x86_64.rpm
```

_Example: Patch Upgrade Inventory_

In this example the `itential-platform` and `itential-configuration_manager` packages are being 
upgraded to 6.0.1.  The `itential-lifecycle_manager` and `itential-service_management`
packages are not being upgraded.

```yaml
all:
  children:
    platform:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_release: 6.0
        platform_redis_host: redis1.example.com
        platform_mongo_url: mongodb://itential:password@mongo1.example.com:27017/itential
        platform_packages:
          - itential-platform-6.0.1-rc.noarch.rpm
          - itential-configuration_manager-6.0.1-rc.noarch.rpm
```

## Run Patch Itential Platform Playbook

Finally, run the `patch_platform` playbook.

```bash
$ ansible-playbook itential.deployer.patch_platform -i <inventory>
```