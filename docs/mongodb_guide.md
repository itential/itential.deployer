# MongoDB Role

The playbook and role in this section install and configure MongoDB for the Itential Automation
Platform. There is currently only one role that can install and configure MongoDB for use with the Itential
Platform.

## MongoDB Installation

The `mongodb` role is basically divided into two functional segments, one for the base installation
of the MongoDB software, and the other for the configuration of MongoDB. These segments can be
triggered individually by using the appropriate tag. See below for details on the available tags.

The role performs a base install of MongoDB including any OS packages required. It includes a few
recommended kernel settings and other optimizations recommended by MongoDB. It creates the
appropriate Linux users, directories, log files, and systemd services. If the host is configured to
use SELinux the role will set the appropriate labels on files and directories. It will start the
mongod service when complete.

Once the base installation is complete, the role will conditionally configure a replica set. After
potentially configuring a replica set, the role will then conditionally configure authorization.
After this, it will conditionally configure TLS connections. Triggering these conditional
configurations is based on the variables that are set in the host file. See below for examples.

## MongoDB Replication

When configured to do so, the role is responsible for configuring MongoDB as a replica set.  It uses
the first host defined in the `mongodb` group in the inventory as the initial primary.  It updates
the MongoDB configuration file with the replica set name and enables replication.  It initializes
the replica set on the initial primary and then joins the remaining MongoDB nodes to the replica
set. It will restart the mongod service when complete. The role will detect if replication has
already been enabled and skip these tasks if it determines that replication is already enabled.

More info on replication: <https://www.mongodb.com/docs/manual/replication/>

## MongoDB Authentication

When configured to do so, the role is designed to enable authentication on the MongoDB.  It will
modify the MongoDB config file to enable authentication for a single database or a replica set.
When MongoDB is configured as a replica set it requires a key for the members of the replica set to
talk to one another.  This key file is created by the role and uploaded to the appropriate location.
It uses openssl and generates a random base 64 string of 756 bytes. It will restart the mongod
service when complete.

More info on authentication: <https://www.mongodb.com/docs/manual/core/authentication/>

More info on the key file: <https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-with-keyfile-access-control/>

## MongoDB TLS

When configured to do so, the role is responsible for configuring MongoDB to use a TLS connection
when connecting to the database.  It is NOT responsible for creating certificates.  Those must be
supplied to this role.  It will copy those certificates to the correct location.  It will make all
required changes to enable TLS connections in the Mongo configuration file. It will restart the
mongod service when complete.

More info on TLS: <https://www.mongodb.com/docs/manual/tutorial/configure-ssl/>

## Variables

### Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be
overridden by the user.  Since these variable files are included at run-time based on the Itential
Platform release and OS major version, they have a higher precedence than the variables in the
inventory and are not easily overridden.

### Global Variables

The variables in this section are configured in the inventory in the `all` group vars.

| Variable | Group | Type | Description | Default Value |
| :------- | :---- | :--- | :---------- | :------------ |
| `platform_release` | `all` | Fixed-point | Designates the IAP major version. If this is not included then the `mongodb` device group must specify the MongoDB packages (the precise Mongo version) to install. | N/A |

When the `platform_release` is defined in the inventory then the playbook will use default values
for the MongoDB version to install. These defaults are determined by the Itential Platform version
and represent our validated design. If this is not included then the `mongodb` device group must
specify the MongoDB packages (the precise Mongo version) to install. See below an example of how to
override the default MongoDB version.

### MongoDB Role Variables

The variables in this section may be overridden in the inventory in the `mongodb` group vars.

The following table contains the most commonly overridden variables.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `mongodb_admin_db_name` | String | The name of the admin database. | `admin` |
| `mongodb_auth_enabled` | Boolean | Flag to enable MongoDB authentication. | `true` |
| `mongodb_itential_db_name` | String | The name of the itential database. | `itential` |
| `mongodb_replication_enabled` | Boolean | Flag to enable MongoDB replication | `false` |
| `mongodb_replset_name` | String | The MongoDB replica set name. | `rs0` |
| `mongodb_ssl_root_dir` | String | The base directory for SSL certs and key files. | `/etc/ssl/certs` |
| `mongodb_tls_enabled` | Boolean | Flag to enable MongoDB TLS. | `false` |
| `mongodb_user_admin_password` | String | The MongoDB admin user password. | `admin` |
| `mongodb_user_itential_password` | String | The MongoDB itential user password. | `itential` |

> :warning: It is assumed that these default passwords will be changed to meet more rigorous
security standards. These are intended to be defaults strictly used just for ease of the
installation and should be overridden in the inventory file. It is highly recommended that sensitive
data be encrypted using Ansible Vault when they are overridden so that the passwords don't actually
appear anywhere in source code.

These variables can be used to override the default version of MongoDB that is installed.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `mongodb_packages` | List(String) | The list of MongoDB yum package names to install. | |
| `mongodb_version` | Float | The MongoDB major version being installed. | Depends on `platform_release` |

These variables effect how and where MongoDB is installed. In most cases, these should not be
modified.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `mongodb_conf_file` | String | The location of the MongoDB configuration file. | `/etc/mongodb.conf` |
| `mongodb_data_dir` | String | The MongoDB data file directory. | `/var/lib/mongo` |
| `mongodb_gpgkey_url` | String | The fully qualified URL to the GPG key for the desired RPM file. | Depends on `mongodb_version` |
| `mongodb_group` | String | The MongoDB Linux group. | `mongod` |
| `mongodb_log_dir` | String | The MongoDB log files directory. | `/var/log/mongodb` |
| `mongodb_owner` | String | The MongoDB Linux user. | `mongod` |
| `mongodb_pid_dir` | String | Directory that stores the mongodb pid file. | `/var/run/mongodb` |
| `mongodb_port` | Integer | The MongoDB listen port. | `27017` |
| `mongodb_release_url` | String | The fully qualified URL to the repo where the MongoDB RPM packages exist. | Depends on `mongodb_version` |

These variables apply to advanced situations.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `mongodb_python_executable` | String | The location of the python executable used by the Community.mongodb ansible tasks. | `/usr/bin/python3` |
| `mongodb_pip_executable` | String | The location of the pip executable used by the Community.mongodb ansible tasks. | `/usr/bin/pip3` |
| `mongodb_python_venv_root` | String | The location of the virtual environment used by the Community.mongodb collection. | `/var/tmp` |
| `mongodb_python_venv_name` | String | The name of the Python virtual environment used by this deployer. | `mongodb_venv` |
| `mongodb_bind_ipv6` | Boolean | Flag to enable binding to IPv6. | `true` |
| `mongodb_bind_addrs` | String | The hostnames and/or IP addresses and/or full Unix domain socket paths on which mongos or mongod should listen for client connections. You may attach mongos or mongod to any interface. To bind to multiple addresses, enter a list of comma-separated values. The inventory_hostname will be automatically added to `mongodb_bind_addrs`.  If `mongodb_bind_ipv6` is set to true, '::1' will be added to `mongodb_bind_addrs`. | `127.0.0.1` |
| `mongodb_mongod_service_retries` | Integer | The number of retries when starting the mongod service. | 5 |
| `mongodb_mongod_service_delay` | Integer | The time in seconds between retries when starting the mongod service. | 10 |
| `mongodb_status_poll` | Integer | The maximum number of times to query for the replicaset status before the set converges or we fail. | 3 |
| `mongodb_status_interval` | Integer | The number of seconds to wait between polling executions. | 10 |

## Configuring TLS

The `mongodb` role does not generate SSL certificates.  They must be generated by the user and put
in the top level `files` directory on the Ansible control node. These files are uploaded to the
location defined in `mongodb_ssl_root_dir`.

## SELinux

The `mongodb` role contains tasks to install custom SELinux profiles (located in
`roles/mongodb/files` and containing the `te` extension).  If your installation requires additional
profiles, the files can be placed in the `files` directory and they will be automatically installed
by the role.

## Building the Inventory

To install and configure MongoDB, add a `mongodb` group and host(s) to your inventory file.  The
following inventory examples demonstrate some common installation patterns.

## Example Inventory - Single MongoDB Node accepting all defaults for Platform 6

This example shows a basic MongoDB configuration with a single MongoDB node accepting all default
values defined with Platform 6.

```yaml
all:
  vars:
    repository_api_key: #key
    platform_release: 6

  children:
    mongodb:
      hosts:
        <host1>:
          ansible_host: <addr1>
```

## Example Inventory - Single MongoDB Node overriding the default MongoDB version

This example shows how to override the default version of MongoDB that is installed. Note that the
`platform_release` variable is NOT specified and the packages are explicitly defined in the
mongodb group vars.

```yaml
all:
  vars:
    repository_api_key: #key

  children:
    mongodb:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        mongodb_version: 7.0
        mongodb_packages:
          - mongodb-org
        mongodb_python_packages:
          - python3
          - python3-pip
```

## Example Inventory - Configuring MongoDB Replica Set accepting all other defaults

To configure replication, add two additional nodes (at least) to the `mongodb` group, add the
`mongodb_replication_enabled` flag to the `mongodb` group vars, and set it to `true`. Optionally,
override the replica set name.

```yaml
all:
  vars:
    repository_api_key: #key
    platform_release: 6

  children:
    mongodb:
      hosts:
        <host1>: # This host will be chosen as the primary initially
          ansible_host: <addr1>
        <host2>:
          ansible_host: <addr2>
        <host3>:
          ansible_host: <addr3>
      vars:
        mongodb_replication_enabled: true
        # Optionally override the replica set name
        # mongodb_replset_name: <a-meaningful-replica-set-name>
```

## Example Inventory - Configuring MongoDB TLS accepting all other defaults

To configure a MongoDB TLS, add the `mongodb_tls` flag to the `all` group vars and set it to `true`
and configure the `mongo_cert_keyfile_source` and `mongo_root_ca_file_source`.

```yaml
all:
  vars:
    repository_api_key: #key
    platform_release: 6

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
      mongodb_replication_enabled: true
      mongodb_tls_enabled: true
      mongo_cert_keyfile_source: mongodb.pem
      mongo_root_ca_file_source: rootCA.pem
```

## Running the Playbook

To execute the MongoDB role, run the `mongodb` playbook:

```bash
ansible-playbook itential.deployer.mongodb -i <inventory>
```

## Tags

You can also run select MongodDB segments by using the following tags:

* `install_mongodb`
* `configure_mongodb`
* `initialize_mongo_config`

The tag `install_mongodb` will run all of the installation tasks which will install MongoDB and
start it up in its most basic state. This tag will execute the tasks to configure SELinux. This tag
will also create the required database users even if they are not used because authorization is not
enabled. Basic installation can be achieved with this command:

```bash
ansible-playbook itential.deployer.mongodb -i <inventory> --tags install_mongodb
```

The tag `configure_mongodb` will run all of the configuration tasks. These tasks are conditional
depending on the features that are enabled in the global vars of the inventory file. Configuration
can be achieved with this command:

```bash
ansible-playbook itential.deployer.mongodb -i <inventory> --tags configure_mongodb
```

This tag can be run repeatedly if there is a need to enable these features in a consecutive manner
or to troubleshoot. However, each feature does alter the state of MongoDB and its possible that
repeated executions can put the configuration in a bad state. To "reset" the configuration to the
state that the installation tag produced you can run this command:

```bash
ansible-playbook itential.deployer.mongodb -i <inventory> --tags initialize_mongo_config
```
