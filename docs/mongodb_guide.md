# Overview

The playbook and role in this section install and configure MongoDB for the Itential Automation Platform.

# Roles

There is currently only one role that can install and configure MongoDB for use with the Itential Platform.

## MongoDB Role

The `mongodb` role is basically divided into two functional segments, one for the base installation of the MongoDB software, and the other for the configuration of MongoDB. These segments can be triggered individually by using the appropriate tag. See below for details on the available tags.

The role performs a base install of MongoDB including any OS packages required. It includes a few recommended kernel settings and other optimizations recommended by MongoDB. It creates the appropriate Linux users, directories, log files, and systemd services. If the host is configured to use SELinux the role will set the appropriate labels on files and directories. It will start the mongod service when complete.

Once the base installation is complete, the role will conditionally configure a replica set. After potentially configuring a replica set, the role will then conditionally configure authorization. After this, it will conditionally configure TLS connections. Triggering these conditional configurations is based on the variables that are set in the host file. See below for examples.

### MongoDB Replication

When configured to do so, the role is responsible for configuring MongoDB as a replica set.  It uses the first host defined in the `mongodb` group in the inventory as the initial primary.  It updates the MongoDB configuration file with the replica set name and enables replication.  It initializes the replica set on the initial primary and then joins the remaining MongoDB nodes to the replica set. It will restart the mongod service when complete. The role will detect if replication has already been enabled and skip these tasks if it determines that replication is already enabled.

More info on replication: https://www.mongodb.com/docs/manual/replication/

### MongoDB Authentication

When configured to do so, the role is designed to enable authentication on the MongoDB.  It will modify the MongoDB config file to enable authentication for a single database or a replica set.  When MongoDB is configured as a replica set it requires a key for the members of the replica set to talk to one another.  This key file is created by the role and uploaded to the appropriate location.  It uses openssl and generates a random base 64 string of 756 bytes. It will restart the mongod service when complete.

More info on authentication: https://www.mongodb.com/docs/manual/core/authentication/

More info on the key file: https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-with-keyfile-access-control/

### MongoDB TLS

When configured to do so, the role is responsible for configuring MongoDB to use a TLS connection when connecting to the database.  It is NOT responsible for creating certificates.  Those must be supplied to this role.  It will copy those certificates to the correct location.  It will make all required changes to enable TLS connections in the Mongo configuration file. It will restart the mongod service when complete.

More info on TLS: https://www.mongodb.com/docs/manual/tutorial/configure-ssl/

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time based on the Itential Platform release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Global Variables

The variables in this section are configured in the inventory in the `all` group vars.

| Variable | Group | Type | Description | Default Value | Required?
| :------- | :---- | :--- | :---------- | :------------ | :---------
| `platform_release` | `all` | Fixed-point | Designates the IAP major version. If this is not included then the `mongodb` device group must specify the MongoDB packages (the precise Mongo version) to install. | N/A | No

When the `platform_release` is defined in the inventory then the playbook will use default values for the MongoDB version to install. These defaults are determined by the Itential Platform version and represent our validated design. If this is not included then the `mongodb` device group must specify the MongoDB packages (the precise Mongo version) to install.

## Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables that are shared between the MongoDB-related roles, located in `roles/common_vars/defaults/main/mongodb.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `mongodb_port` | `all` | Integer | The MongoDB listen port. | `27017`
| `mongodb_itential_db_name` | `all` | String | The name of the itential database. | `itential`
| `mongodb_localaaa_db_name` | `all` | String | The name of the local AAA database | `LocalAAA`
| `mongodb_replication_enabled` | `all` | Boolean | Flag to enable MongoDB replication | `false`
| `mongodb_auth_enabled` | `all` | Boolean | Flag to enable MongoDB authentication. | `false`
| `mongodb_tls_enabled` | `all` | Boolean | Flag to enable MongoDB TLS. | `false`
| `mongodb_itential_connection_String` | `all` | String | The default MongoDB connection String to the itential databse. | `mongodb://{{ mongodb_host }}:{{ mongodb_port }}/{{ mongo_itential_db_name }}`
| `mongodb_admin_connection_String` | `all` | String | The default MongoDB connection String to the admin database. | `mongodb://{{ mongodb_host }}:{{ mongodb_port }}/{{ mongodb_admin_db_name }}`
| `mongodb_localaaa_connection_String` | `all` | String | The default MongoDB connection String to the Local AAA databas.e | `mongodb://{{ mongodb_host }}:{{ mongodb_port }}/{{ mongodb_localaaa_db_name }}`
| `mongodb_user_admin_password` | `all` | String | The MongoDB admin user password. | `admin`
| `mongodb_user_itential_password` | `all` | String | The MongoDB itential user password. | `itential`
| `mongodb_user_localaaa_password` | `all` | String | The MongoDB Local AAA user password. | `localaaa`
| `mongodb_replset_name` | `all` | String | The MongoDB replica set name. | `rs0`

:::(Warning) (⚠ Warning: ) It is assumed that these default passwords will be changed to meet more rigorous security standards. These are intended to be defaults strictly used just for ease of the installation and should be overridden in the inventory file.  It is highly recommended that sensitive data be encrypted using Ansible Vault when they are overridden so that the passwords don't actually appear anywhere in source code.

## MongoDB Role Variables

The variables in this section may be overridden in the inventory in the `mongodb` group vars.

The following table lists the default variables located in `roles/mongodb/defaults/main/install.yml` and `roles/mongodb/defaults/main/mongodb.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `mongodb_version` | `mongodb` | Float | The MongoDB major version being installed. | Depends on `platform_release`
| `mongodb_release_url` | `mongodb` | String | The fully qualified URL to the repo where the MongoDB RPM packages exist. | Depends on `mongodb_version`
| `mongodb_gpgkey_url` | `mongodb` | String | The fully qualified URL to the GPG key for the desired RPM file. | Depends on `mongodb_version`
| `mongodb_python_executable` | `mongodb` | String | The location of the python executable used by the Community.mongodb ansible tasks. | `/usr/bin/python3`
| `mongodb_pip_executable` | `mongodb` | String | The location of the pip executable used by the Community.mongodb ansible tasks. | `/usr/bin/pip3`
| `mongodb_python_venv_root` | `mongodb` | String | The location of the virtual environment used by the Community.mongodb collection. | `/var/tmp`
| `mongodb_python_venv_name` | `mongodb` | String | The name of the Python virtual environment used by this deployer. | `mongodb_venv`
| `mongodb_conf_file` | `mongodb` | String | The location of the MongoDB configuration file. | `/etc/mongodb.conf`
| `mongodb_data_dir` | `mongodb` | String | The MongoDB data file directory. | `/var/lib/mongo`
| `mongodb_log_dir` | `mongodb` | String | The MongoDB log files directory. | `/var/log/mongodb`
| `mongodb_pid_dir` | `mongodb` | String | Directory that stores the mongodb pid file. | `/var/run/mongodb`
| `mongodb_ssl_root_dir` | `mongodb` | String | The base directory for SSL certs and key files. | `/etc/ssl/certs`
| `mongodb_auth_keyfile_destination` | `mongodb` | String | The path to the key file that is used to authenticate members of a replica set. | `/etc/ssl/certs/mongodb/mongo-replicaset-key.pem`
| `mongodb_cert_keyfile_destination` | `mongodb` | String | The path to the certificate key file used for TLS connections. | `/etc/ssl/certs/mongodb/mongo-certificate.pem`
| `mongodb_root_ca_file_destination` | `mongodb` | String | The path to the CA root file used for TLS connections | `/etc/ssl/certs/mongodb/mongo-rootCA.pem`
| `mongodb_owner` | `mongodb` | String | The MongoDB Linux user. | `mongod`
| `mongodb_group` | `mongodb` | String | The MongoDB Linux group. | `mongod`
| `mongodb_admin_db_name` | `mongodb` | String | The name of the admin database. | `admin`
| `mongodb_bind_ipv6` | `mongodb` | Boolean | Flag to enable binding to IPv6. | `true`
| `mongodb_bind_addrs` | `mongodb` | String | The hostnames and/or IP addresses and/or full Unix domain socket paths on which mongos or mongod should listen for client connections. You may attach mongos or mongod to any interface. To bind to multiple addresses, enter a list of comma-separated values.  <br>The inventory_hostname will be automatically added to `mongodb_bind_addrs`.  <br>If `mongodb_bind_ipv6` is set to true, '::1' will be added to `mongodb_bind_addrs`. | `127.0.0.1`

# Configuring TLS

The `mongodb` role does not generate SSL certificates.  They must be generated by the user and put in the top level `files` directory on the Ansible control node. These files are uploaded to the location defined in `mongodb_ssl_root_dir`.

# SELinux

The `mongodb` role contains tasks to install custom SELinux profiles (located in `roles/mongodb/files` and containing the `te` extension).  If your installation requires additional profiles, the files can be placed in the `files` directory and they will be automatically installed by the role.

# Building the Inventory

To install and configure MongoDB, add a `mongodb` group and host to your inventory.  The following inventory shows a basic MongoDB configuration with a single MongoDB node with no Authentication/TLS.

## Example Inventory - Single MongoDB Node

```
all:
  vars:
    platform_release: 6.0

  children:
    mongodb:
      hosts:
        <host1>:
          ansible_host: <addr1>
```

To add authentication, add the `mongodb_auth_enabled` variable and set it to `true`.

## Example Inventory - Configuring MongoDB Authorization

```
all:
  vars:
    platform_release: 6.0
    mongodb_auth_enabled: true

  children:
    mongodb:
      hosts:
        <host1>:
          ansible_host: <addr1>
```

To configure replication, add two additional nodes to the `mongodb` group and add the `mongodb_replication_enabled` flag to the `all` group vars and set it to `true`.

## Example Inventory - Configuring MongoDB Replica Set

```
all:
  vars:
    platform_release: 6.0
    mongodb_auth_enabled: true
    mongodb_replication_enabled: true

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
    platform_release: 6.0
    mongodb_auth_enabled: true
    mongodb_replication_enabled: true
    mongodb_tls_enabled: true

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

To execute the MongoDB role, run the `mongodb` playbook:

```
ansible-playbook itential.deployer.mongodb -i <inventory>
```

## Tags
You can also run select MongodDB segments by using the following tags:

* `install_mongodb`
* `configure_mongodb`
* `initialize_mongo_config`

The tag `install_mongodb` will run all of the installation tasks which will install MongoDB and start it up in its most basic state. This tag will execute the tasks to configure SELinux. This tag will also create the required database users even if they are not used because authorization is not enabled. Basic installation can be achieved with this command:

```
ansible-playbook itential.deployer.mongodb -i <inventory> --tags install_mongodb
```
The tag `configure_mongodb` will run all of the configuration tasks. These tasks are conditional depending on the features that are enabled in the global vars of the inventory file. Configuration can be achieved with this command:

```
ansible-playbook itential.deployer.mongodb -i <inventory> --tags configure_mongodb
```

This tag can be run repeatedly if there is a need to enable these features in a consecutive manner or to troubleshoot. However, each feature does alter the state of MongoDB and its possible that repeated executions can put the configuration in a bad state. To "reset" the configuration to the state that the installation tag produced you can run this command:

```
ansible-playbook itential.deployer.mongodb -i <inventory> --tags initialize_mongo_config
```
