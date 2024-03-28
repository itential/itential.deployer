# Overview

The Itential Deployer supports patch upgrades for IAP.  These are also referred to as monthly releases.  For example, if IAP version 2023.1.1 is currently installed, it could be upgraded to any 2023.1.X version.  The patch upgrade playbook **DOES NOT** support major upgrades.  For major upgrades, please work with your Itential Professional Services representative.

# Procedure

## Download the IAP Artifact

The IAP artifacts are hosted on the Itential Nexus repository. Please contact your Itential Professional Services representative to get the proper credentials, locations of the artifacts and instructions for downloading.  Download the new artifact and place it in the `files` directory.

## Update Inventory Variables

Next, update the inventory variables.  It is recommended that the inventory used during the original IAP install is used as the baseline.  Update the `iap_bin_file` or `iap_tar_file` to the new version.  Then, determine if a MongoDB backup is required.  If it is required, then there are no additional changes required (`mongo_backup` is defaulted to `true`).  If it is not required, then add the `mongo_backup` variable to the platform group variables and set it to `false`.

_Example: Original Inventory_

```yaml
all:
    vars:
        iap_release: 2023.1

    children:
        platform:
            hosts:
                cluster6-aio01:
                    ansible_host: 172.16.37.185
            vars:
                iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin
```

_Example: Patch Upgrade Inventory_

```yaml
all:
    vars:
        iap_release: 2023.1

    children:
        platform:
            hosts:
                cluster6-aio01:
                    ansible_host: 172.16.37.185
            vars:
                iap_bin_file: itential-premium_2023.1.5.linux.x86_64.bin
                mongo_backup: false
```

## Run Patch IAP Playbook

Finally, run the `itential.deployer.patch_iap` playbook.

```bash
$ ansible-playbook itential.deployer.patch_iap -i <inventory>
```