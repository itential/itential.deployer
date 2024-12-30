# Overview

The playbook and roles in this section install and configure Hashicorp Vault for the Itential Automation Platform.  There are currently two Vault-related roles:

* `vault` – Installs Vault and performs a base configuration.
* `vault_unseal` – Unseals the Vault.

# Roles

## Vault Role

The `vault` role performs a base install of Hashicorp Vault including any OS packages required. It creates the appropriate Linux users, groups, configuration files, and directories for the service to run. It will start the vault service when complete.

## Vault Unseal Role

The `vault_setup` role performs the steps required to setup the Vault server. Steps include initializing the server, unsealing the server, generating the root key for the server, and enabling the KV secrets engine used to store IAP secrets. 

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time based on the IAP release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Global Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `vault_read_only` | `all` | Boolean | Flag to manage how secret data is written to Vault with IAP version 2021.2 and later. | `false`

Beginning with the 2021.2 release, a `readOnly` property was added to vaultProps in the properties.json file. This property allows developers to denote fields that contain sensitive data and manage how secret data is written to Vault. This configurable property defaults to false.

When set as readOnly: true, the following will occur:

 - Masking in the UI will be disabled (turned off).
 - Clear text will be shown.
 - All custom user decorations will be ignored.
 - IAP will not write data to Vault.

⚠ WARNING: If there are passwords stored within Vault and the readOnly property is initially set to false, and then later changed to true, all passwords will be lost and have to be set manually.

## Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables that are shared between the Vault-related roles, located in `roles/common_vars/defaults/main/vault.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `vault_group` | `all` | String | The Vault Linux group. | `vault`
| `vault_port` | `all` | Integer | The Vault listen port. | `8200`
| `vault_root_key_dir` | `all` | String | The Vault root key directory. | `/opt/vault/keys/root_key`
| `vault_name` | `all` | String | The name of the secret engine used to configure vault and IAP | `itential`

## Vault Role Variables

The variables in this section may be overridden in the inventory in the `vault` group vars.

The following table lists the default variables located in `roles/vault/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `vault_install` | `vault` | Boolean | Flag to enable Vault installation. | `false`
| `vault_dir` | `vault` | String | The Vault data directory. | `/opt/vault`
| `vault_cluster_port` | `vault` | Integer | The Vault cluster communication port. | `8201`
| `vault_user` | `all` | String |The Vault Linux user. | `vault`

## Vault Unseal Role Variables

The variables in this section may be overridden in the inventory in the `vault` group vars.

The following table lists the default variables located in `roles/vault_unseal/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `vault_setup` | `vault` | Boolean | Flag to enable Vault setup. | `false`
| `vault_unseal_keys_dir` | `vault` | String | The Vault unseal keys directory. | `/opt/vault/keys/unseal_keys`

# Building Your Inventory

To install and unseal Vault, add a `vault` group and host to your inventory and configure the `vault_install` and `vault_setup` variables.  The following inventory shows a basic Vault configuration with a single Vault node.

## Example Inventory - Single Vault Node

```
all:
    children:
        vault:
            hosts:
                <host1>:
                    ansible_host: <addr1>
            vars:
                vault_install: true
                vault_setup: true
```

**&#9432; Note:**
In order to use Vault in IAP, the `configure_vault` variable will need to be set in the `platform` group and the `itential.deployer.iap` playbook will need to be executed.  Refer to the [IAP Guide](iap_guide.md).

# Running the Playbook

To execute all Vault roles, run the `vault` playbook:

```
ansible-playbook itential.deployer.vault -i <inventory>
```

You can also run select Vault roles by using the following tags:

* `vault_install`
* `vault_setup`

To execute only the `vault` role, run the `itential.deployer.vault` playbook with the `vault_install` tag:

```
ansible-playbook itential.deployer.vault -i <inventory> --tags vault_install
```

To execute only the `vault_unseal` role, run the `itential.deployer.vault` playbook with the `vault_setup` tag:

```
ansible-playbook itential.deployer.vault -i <inventory> --tags vault_setup
```
