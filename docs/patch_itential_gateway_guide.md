# Patch IAG

The Itential Deployer supports patch upgrades for IAG.  These are also referred to as monthly
releases.  For example, if IAG version 3.227.0+2023.1.1 is currently installed, it could be
upgraded to any 3.227.0+2023.1.X version.  The patch upgrade playbook **DOES NOT** support major
upgrades.  For major upgrades, please work with your Itential Professional Services representative.

## Requirements

In order to run the Patch IAG playbook, the `jmespath` Python module must be installed on the
**Ansible Control Node**.

## Procedure

### Download the IAG Artifact

The IAG artifacts are hosted on the Itential Nexus repository. Please contact your Itential
Professional Services representative to get the proper credentials, locations of the artifacts and
instructions for downloading.  Download the new artifact and place it in the `files` directory.

### Update Inventory Variables

Next, update the inventory variables.  It is recommended that the inventory used during the
original IAG install is used as the baseline.  Update the `gateway_whl_file` to the new version.

#### Example: Original Inventory

```yaml
all:
  children:
    gateway:
      hosts:
        <host1:
          ansible_host: <host1-ip>
      vars:
        gateway_release: 4.3
        gateway_whl_file: <wheel-file>
```

#### Example: Patch Upgrade Inventory

```yaml
all:
  children:
    gateway:
      hosts:
        <host1:
          ansible_host: <host1-ip>
      vars:
        gateway_release: 4.3
        gateway_whl_file: <wheel-file>
```

### Run Patch IAG Playbook

Finally, run the `patch_iag` playbook.

```bash
ansible-playbook itential.deployer.patch_iag -i <inventory>
```
