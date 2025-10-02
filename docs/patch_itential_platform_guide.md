# Patch IAP

Itential uses semantic versioning to articulate changes made to the core products. The Itential
Deployer supports patch and minor upgrades for Itential Platform.  The patch upgrade playbook
**DOES NOT** support major upgrades, for example going from 6.X.X to 7.X.X.  For major upgrades,
there are typically other components that might need to be upgraded such as the dependencies.
Please work with your Itential Professional Services representative before doing an upgrade to a
new major version.

## Requirements

In order to run the Patch Itential Platform playbook, the `jmespath` Python module must be
installed on the **Ansible Control Node**.

## Procedure

### Download the Itential Platform Packages

The Itential Platform packages are hosted on the Itential Nexus repository. Please contact your
Itential Professional Services representative to get the proper credentials, locations of the
packages and instructions for downloading.  Download the new packages and place them in the
`playbooks/files` directory.

**&#9432; Note:**
Nexus URLs are also supported in `platform_packages`.

### Update Inventory Variables

Next, update the inventory variables.  It is recommended that the inventory used during the original
Itential Platform install is used as the baseline.  Update the `platform_release` to the desired
version and update the `platform_packages` appropriately. It is highly recommended to take a backup
of MongoDB before patching. For more information:

<https://www.mongodb.com/docs/database-tools/mongodump/>

#### Example: Original Inventory

```yaml
all:
  children:
    platform:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_encryption_key: <openssl rand -hex 32> # 64-length hex string, representing a 256-bit AES  encryption key.
        platform_release: 6.0
        platform_redis_host: redis1.example.com
        platform_mongo_url: mongodb://itential:password@mongo1.example.com:27017/itential
        platform_packages:
          - itential-platform-6.0.0-rc.noarch.rpm
          - itential-lifecycle_manager-6.0.0-rc.noarch.rpm
          - itential-configuration_manager-6.0.0-rc.noarch.rpm
          - itential-service_management-6.0.0-rc1.x86_64.rpm
```

#### Example: Patch Upgrade Inventory

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
        platform_encryption_key: <openssl rand -hex 32> # 64-length hex string, representing a 256-bit AES  encryption key.
        platform_release: 6.0
        platform_redis_host: redis1.example.com
        platform_mongo_url: mongodb://itential:password@mongo1.example.com:27017/itential
        platform_packages:
          - itential-platform-6.0.1-rc.noarch.rpm
          - itential-configuration_manager-6.0.1-rc.noarch.rpm
```

### Run Patch Itential Platform Playbook

Finally, run the `patch_platform` playbook.

```bash
ansible-playbook itential.deployer.patch_platform -i <inventory>
```
