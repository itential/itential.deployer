# Overview

The playbook and roles in this section install and configure MongoDB for the Itential Automation Platform.  There are currently four MongoDB-related roles:

* `mongodb` – Installs MongoDB and performs a base configuration.
* `mongodb_auth` – Configures MongoDB authentication.
* `mongodb_replication` – Configures MongoDB as replica set.
* `mongodb_tls` - Configures MongoDB SSL.

# Roles

## MongoDB Role

The `mongodb` role performs a base install of MongoDB including any OS packages required. It includes a few recommended kernel settings and other optimizations recommended by MongoDB. It creates the appropriate Linux users, directories, log files, and systemd services. It will start the mongod service when complete.

## MongoDB Authentication

The `mongodb_auth` role is designed to enable authorization on the MongoDB.  It will modify the MongoDB config file to enable authentication for a single database or a replica set.  When MongoDB is configured as a replica set it requires a key for the members of the replica set to talk to one another.  This key file is uploaded to the appropriate location.  It will restart the mongod service when complete.

More info on the key file: https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-with-keyfile-access-control/

## MongoDB Replication

The `mongodb_replication` role is responsible for configuring MongoDB as a replica set.  It uses the first host defined in the `mongodb` group in the inventory as the initial primary.  It updates the MongoDB configuration file with the replica set name and enables replication.  It initializes the replica set on the initial primary and then joins the remaining MongoDB nodes to the replica set. It will restart the mongod service when complete.

More info on replication: https://www.mongodb.com/docs/manual/replication/

## MongoDB TLS

The `mongodb_tls` role is responsible for configuring MongoDB to use a TLS connection when connecting to the database.  It is NOT responsible for creating certificates.  Those must be supplied to this role.  It will copy those certificates to the correct location.  It will make all required changes to enable TLS connections in the Mongo configuration file. It will restart the mongod service when complete.

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time based on the Itential Platform release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Global Variables

The variables in this section are configured in the inventory in the `all` group vars.

| Variable | Group | Type | Description | Default Value | Required?
| :------- | :---- | :--- | :---------- | :------------ | :---------
| `platform_release` | `all` | Fixed-point | Designates the Itential Platform major version. | N/A | Yes
| `mongo_root_ca_file_source` | `all` | String | The name of the MongoDB Root CA file.| N/A | No

The `platform_release` must be defined in the inventory.  This variable, along with the OS major version, is used to determine the static variables.

## Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables that are shared between the MongoDB-related roles, located in `roles/common_vars/defaults/main/mongodb.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `mongo_port` | `all` | Integer | The MongoDB listen port. | `27017`
| `mongo_itential_db_name` | `all` | String | The name of the itential database. | `itential`
| `mongo_localaaa_db_name` | `all` | String | The name of the local AAA database | `LocalAAA`
| `mongodb_replication` | `all` | Boolean | Flag to enable MongoDB replication | `false`
| `mongodb_auth` | `all` | Boolean | Flag to enable MongoDB authentication. | `false`
| `mongodb_tls` | `all` | Boolean | Flag to enable MongoDB TLS. | `false`
| `mongo_itential_connection_string` | `all` | String | The default MongoDB connection string to the itential databse. | `mongodb://{{ mongo_host }}:{{ mongo_port }}/{{ mongo_itential_db_name }}`
| `mongo_admin_connection_string` | `all` | String | The default MongoDB connection string to the admin database. | `mongodb://{{ mongo_host }}:{{ mongo_port }}/{{ mongo_admin_db_name }}`
| `mongo_localaaa_connection_string` | `all` | String | The default MongoDB connection string to the Local AAA databas.e | `mongodb://{{ mongo_host }}:{{ mongo_port }}/{{ mongo_localaaa_db_name }}`
| `mongo_user_admin_password` | `all` | String | The MongoDB admin user password. | `admin`
| `mongo_user_itential_password` | `all` | String | The MongoDB itential user password. | `itential`
| `mongo_user_localaaa_password` | `all` | String | The MongoDB Local AAA user password. | `localaaa`
| `mongo_replset_name` | `all` | String | The MongoDB replica set name. | `rs0`

:::(Warning) (⚠ Warning: ) It is assumed that these default passwords will be changed to meet more rigorous standards. These are intended to be defaults strictly used just for ease of the installation.  It is highly recommended that sensitive data be encrypted using Ansible Vault.

## MongoDB Role Variables

The variables in this section may be overridden in the inventory in the `mongodb` group vars.

The following table lists the default variables located in `roles/mongodb/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `mongo_conf_file` | `mongodb` | String | The location of the MongoDB configuration file. | `/etc/mongodb.conf`
| `mongo_data_dir` | `mongodb` | String | The MongoDB data file directory. | `/var/lib/mongo`
| `mongo_log_dir` | `mongodb` | String | The MongoDB log files directory. | `/var/log/mongodb`
| `mongo_owner` | `mongodb` | String | The MongoDB Linux user. | `mongod`
| `mongo_group` | `mongodb` | String | The MongoDB Linux group. | `mongod`
| `mongo_admin_db_name` | `mongodb` | String | The name of the admin database. | `admin`
| `mongodb_bind_ipv6` | `mongodb` | Boolean | Flag to enable binding to IPv6. | `true`
| `mongodb_bind_addrs` | `mongodb` | String | The hostnames and/or IP addresses and/or full Unix domain socket paths on which mongos or mongod should listen for client connections. You may attach mongos or mongod to any interface. To bind to multiple addresses, enter a list of comma-separated values.  <br>The inventory_hostname will be automatically added to `mongodb_bind_addrs`.  <br>If `mongodb_bind_ipv6` is set to true, '::1' will be added to `mongodb_bind_addrs`. | `127.0.0.1`

## MongoDB Auth Role Variables

The variables in this section may be overridden in the inventory in the `mongodb` group vars.

The following table lists the default variables located in `roles/mongodb_auth/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `mongo_auth_keyfile_source` | `mongodb` | String | The name of the key file. | `mongo-replicaset-key.pem`
| `mongo_auth_keyfile_destination` | `mongodb` | String | The key file used to authenticate members of a replica set. | `/etc/ssl/{{ mongo_auth_keyfile_source }}`

## MongoDB Replication Role Variables

There are no default variables for the MongoDB Replication role.

## MongoDB TLS Role Variables

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `mongo_cert_keyfile_source` | `mongodb` | String | The MongoDB SSL cert key file source. | N/A
| `mongo_cert_keyfile_destination` | `mongodb` | String | The MongoDB SSL cert key file destination. | `/etc/ssl/mongo-certificate.pem`
| `mongo_root_ca_file_source` | `mongodb` | String | The MongoDB SSL root CA source. | N/A
| `mongo_root_ca_file_destination` | `mongodb` | String | The MongoDB SSL root CA file destination. | `/etc/ssl/mongo-rootCA.pem`

# Configuring TLS

The `mongodb_tls` roles does not generate SSL certificates.  They must be generated by the user and put in the top level `files` directory on the Ansible control node.  The following variables must be defined in the `all` group vars.

| File | Variable | Group | Default
| :--- | :------- | :---- | :------
| Key File | `{{ mongo_cert_keyfile_source }}` | `mongodb` | N/A
| Root CA File | `{{ mongo_root_ca_file_source }}` | `mongodb` | N/A

The following table shows the source and destination locations for the files.

| File | Source Location | Destination Location
| :--- | :-------------- | :-------------------
| Server Cert | `{{ mongo_cert_keyfile_sourcele_path }}` | `{{ mongo_cert_keyfile_destination }}`
| Server Key | `{{ mongo_root_ca_file_source }}` | `{{ mongo_root_ca_file_destination }}`

# SELinux

The `mongodb` role contains tasks to install custom SELinux profiles (located in `roles/mongodb/files` and containing the `te` extension).  If your use case requires additional profiles, the files can be placed in the `files` directory and they will be automatically installed by the role.

# Building the Inventory

To install and configure MongoDB, add a `mongodb` group and host to your inventory.  The following inventory shows a basic MongoDB configuration with a single MongoDB node with no Authentication/TLS.

## Example Inventory - Single MongoDB Node

```
all:
    vars:
        platform_release: 2023.1

    children:
        mongodb:
            hosts:
                <host1>:
                    ansible_host: <addr1>
```

To add authentication, add the `mongodb_auth` variable and set it to `true`.

## Example Inventory - Configuring MongoDB Authorization

```
all:
    vars:
        platform_release: 2023.1
        mongodb_auth: true

    children:
        mongodb:
            hosts:
                <host1>:
                    ansible_host: <addr1>
```

To configure replication, add two additional nodes to the `mongodb` group and add the `mongodb_replication` flag to the `all` group vars and set it to `true`.

## Example Inventory - Configuring MongoDB Replica Set

```
all:
    vars:
        platform_release: 2023.1
        mongodb_auth: true
        mongodb_replication: true

    children:
        mongodb:
            hosts:
                <host1>:
                    ansible_host: <addr1>
                <host2>:
                    ansible_host: <addr2>
                <host3>:
                    ansible_host: <addr3>
```

To configure a MongoDB TLS, add the `mongodb_tls` flag to the `all` group vars and set it to `true` and configure the `mongo_cert_keyfile_source` and `mongo_root_ca_file_source`.

## Example Inventory - Configuring MongoDB TLS

```
all:
    vars:
        platform_release: 2023.1
        mongodb_auth: true
        mongodb_cluster: true
        mongodb_tls: true

    children:
        mongodb:
            hosts:
                <host1>:
                    ansible_host: <addr1>
                <host2>:
                    ansible_host: <addr2>
                <host3>:
                    ansible_host: <addr3>
            vars:
                mongo_cert_keyfile_source: mongodb.pem
                mongo_root_ca_file_source: rootCA.pem
```

# Running the Playbook

To execute all MongoDB roles, run the `mongodb` playbook:

```
ansible-playbook itential.deployer.mongodb -i <inventory>
```

You can also run select MongodDB roles by using the following tags:

* `mongodb_install`
* `mongodb_replication`
* `mongodb_auth`
* `mongodb_tls`

To execute only the `mongodb` role, run the `itential.deployer.mongodb` playbook with the `mongodb_install` tag:

```
ansible-playbook itential.deployer.mongodb -i <inventory> --tags mongodb_install
```

To execute only the MongoDB Replication role, run the `itential.deployer.mongodb` playbook with the `mongodb_replication` tag:

```
ansible-playbook itential.deployer.mongodb -i <inventory> --tags mongodb_replication
```

To execute only the MongoDB Authentication role, run the `itential.deployer.mongodb` playbook with the `mongodb_auth` tag:

```
ansible-playbook itential.deployer.mongodb -i <inventory> --tags mongodb_auth
```

To execute only the MongoDB TLS role, run the `itential.deployer.mongodb` playbook with the `mongodb_tls` tag:

```
ansible-playbook itential.deployer.mongodb -i <inventory> --tags mongodb_tls
```
