# Overview

The Itential Deployer supports patch upgrades for IAG.  These are also referred to as monthly releases.  For example, if IAG version 3.227.0+2023.1.1 is currently installed, it could be upgraded to any 3.227.0+2023.1.X version.  The patch upgrade playbook **DOES NOT** support major upgrades.  For major upgrades, please work with your Itential Professional Services representative.

# Procedure

## Download the IAG Artifact

The IAG artifacts are hosted on the Itential Nexus repository. Please contact your Itential Professional Services representative to get the proper credentials, locations of the artifacts and instructions for downloading.  Download the new artifact and place it in the `files` directory.

## Update Inventory Variables

Next, update the inventory variables.  It is recommended that the inventory used during the original IAG install is used as the baseline.  Update the `iag_whl_file` to the new version.

_Example: Original Inventory_

```yaml
all:
    children:
        gateway:
            hosts:
                <host1:
                    ansible_host: <host1-ip>
            vars:
                iag_release: 2023.1
                iag_whl_file: automation_gateway-3.227.0+2023.1.9-py3-none-any.whl
```

_Example: Patch Upgrade Inventory_

```yaml
all:
    children:
        gateway:
            hosts:
                <host1:
                    ansible_host: <host1-ip>
            vars:
                iag_release: 2023.1
                iag_whl_file: automation_gateway-3.227.0+2023.1.52-py3-none-any.whl
```

## Run Patch IAG Playbook

Finally, run the `itential.deployer.patch_iag` playbook.

```bash
$ ansible-playbook itential.deployer.patch_iag -i <inventory>
```