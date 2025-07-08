# Vault Role

The playbook and role in this section install and configure Hashicorp Vault for the Itential
Platform. There is currently one Vault-related role which installs Hashicorp Vault, performs a base
configuration, and unseals the Vault.

## Vault Install

The `vault` role performs a base install of Hashicorp Vault including any OS packages required.
It creates the appropriate Linux users, groups, configuration files, and directories for the
service to run. It will start the vault service when complete.  It will then perform the steps
required to setup the Vault server. Steps include initializing the server, unsealing the server,
generating the root key for the server, and enabling the KV secrets engine used to store Itential
Platform secrets.

[!WARNING] This role should not be used on production as it does not follow robust security
practices. It is intended for development environments as an integration testing point. The
root token and the unseal keys are written to the local file system. They must be backed up and
considered carefully.

## Variables

### Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be
overridden by the user.  Since these variable files are included at run-time based on the Itential
Platform release and OS major version, they have a higher precedence than the variables in the
inventory and are not easily overridden.

### Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables that are shared between the Vault-related roles, located in `roles/common/defaults/main/vault.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `vault_dir` | String | The Vault data directory. | `/opt/vault` |
| `vault_root_key_dir` | String | The Vault root key directory. | `/opt/vault/keys/root_key` |

### Vault Role Variables

The variables in this section may be overridden in the inventory in the `vault` group vars.

The following table lists the default variables located in `roles/vault/defaults/main.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `vault_port` | Integer | The Vault listen port. | `8200` |
| `vault_cluster_port` | Integer | The Vault cluster communication port. | `8201` |
| `vault_unseal_keys_dir` | String | The Vault unseal keys directory. | `/opt/vault/keys/unseal_keys` |
| `vault_name` | String | The name of the secret engine used to configure vault and Itential Platform | `itential` |
| `vault_user` | String |The Vault Linux user. | `vault` |
| `vault_group` |  String | The Vault Linux group. | `vault` |

## Building Your Inventory

To install and unseal Vault, add a `vault` group and host to your inventory.  The following
inventory shows a basic Vault configuration with a single Vault node.

### Example Inventory - Single Vault Node

```yaml
all:
  children:
    vault:
      hosts:
        <host1>:
          ansible_host: <addr1>
```

**&#9432; Note:**
In order to use Vault in Itential Platform, the `platform_configure_vault` variable will need to be
set in the `platform` group and the `itential.deployer.platform` playbook will need to be executed.
Refer to the [Itential Platform Guide](itential_platform_guide.md).

## Running the Playbook

To execute the Vault role, run the `vault` playbook:

```bash
ansible-playbook itential.deployer.vault -i <inventory>
```

You can also run select Vault tasks by using the following tags:

* `install_vault`
* `configure_vault`
* `unseal_vault`

To execute only the installation tasks, run the `itential.deployer.vault` playbook with the `install_vault` tag:

```bash
ansible-playbook itential.deployer.vault -i <inventory> --tags install_vault
```

To execute only the configuration tasks, run the `itential.deployer.vault` playbook with the `configure_vault` tag:

```bash
ansible-playbook itential.deployer.vault -i <inventory> --tags configure_vault
```

To execute only the unseal tasks, run the `itential.deployer.vault` playbook with the `unseal_vault` tag:

```bash
ansible-playbook itential.deployer.vault -i <inventory> --tags unseal_vault
```
