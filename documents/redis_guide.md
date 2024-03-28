# Overview

The playbook and roles in this section install and configure Redis for the Itential Automation Platform.  There are currently three Redis-related roles:

* `redis` – Installs Redis and performs a base configuration.
* `redis_auth` – Configures Redis authentication.
* `redis_replication` – Configures Redis replication.

# Roles

## Redis Role

The `redis` role performs a base install of Redis including any OS packages required. It will compile and install any custom SELinux profiles. It creates the appropriate Linux users, directories, log files, and systemd services. It uses a template to generate a configuration file with some potential features available in other roles commented out. It will start the redis service when complete.

## Redis Auth Role

The `redis_auth` role performs tasks to require authentication (username and password) when communicating with the Redis server. It adjusts the Redis config file and adds each of the required users and applies appropriate ACLs (see table). The "default" Redis user is disabled. It modifies the Redis config file to use the appropriate user while doing replication. It adjusts the Sentinel config file to enable the correct Sentinel user to monitor the redis cluster, if required. It disables the default user in both Redis and Redis Sentinel. It will restart the redis service and the Sentinel service (if required) when complete.

More info on Redis authorization: https://redis.io/docs/manual/security/

| User Name | Default Password | Description
| :-------- | :--------------- | :----------
| admin | admin | Has full access to the Redis database.
| itential | itential | Has access to all keys, all channels, and all commands except: -asking -cluster -readonly -readwrite -bgrewriteaof -bgsave -failover -flushall -flushdb -psync -replconf -replicaof -save -shutdown -sync
| repluser | repluser | Has access to the minimum set of commands to perform replication.
| sentineluser | sentineluser | Has access to the minimum set of commands to perform sentinel monitoring.

:::(Warning) (⚠ Warning: ) It is assumed that these default passwords will be changed to meet more rigorous standards. These are intended to be defaults strictly used just for ease of the installation.  It is highly recommended that sensitive data be encrypted using Ansible Vault.

## Redis Replication Role

The `redis_replication` role performs the steps required to create a Redis replica set. It uses a template to generate a Redis Sentinel config file. It modifies the Redis config file to turn off protected-mode. It assumes that the first host defined in the inventory file is the initial primary. It will update the config file for the non-primary Redis servers to replicate from the primary using hostname. It will restart Redis and Redis Sentinel when complete.

For more information on Redis replication: https://redis.io/docs/manual/replication/

# Variables

## Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be overridden by the user.  Since these variable files are included at run-time based on the IAP release and OS major version, they have a higher precedence than the variables in the inventory and are not easily overridden.

## Global Variables

The variables in this section are configured in the inventory in the `all` group vars.

| Variable | Group | Type | Description | Default Value | Required?
| :------- | :---- | :--- | :---------- | :------------ | :--------
| `iap_release` | `all` | Fixed-point | Designates the IAP major version. | N/A | Yes

The `iap_release` must be defined in the inventory.  This variable, along with the OS major version, is used to determine the static variables.

## Common Variables

The variables in this section may be overridden in the inventory in the `all` group vars.

The following table lists the default variables that are shared between the Redis-related roles, located in `roles/common_vars/defaults/main/redis.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `redis_auth` | `all` | Boolean | Flag to enable Redis authentication. When set to to `true`, the `redis_auth` role will be executed. | `false`
| `redis_replication` | `all` | Boolean | Flag to enable Redis replication. When set to `true`, the `redis_replication` role will be executed. | `false`

## Redis Role Variables

The variables in this section may be overridden in the inventory in the `redis` group vars.

The following table lists the default variables located in `roles/redis/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `redis_conf_path` | `redis` | String | The path to the Redis configuration file. | `/etc/redis`
| `redis_conf_file` | `redis` | String | The location of the Redis configuration file. | `{{ redis_conf_path }}/redis.conf`
| `redis_log` | `redis` | String | The location of the Redis log file. | `/var/log/redis/redis.log`
| `redis_db_filename` | `redis` | String | The name of the Redis data file. | `dump.rdb`
| `redis_data_dir` | `redis` | String | The location of the Redis data directory. | `/var/lib/redis`
| `redis_port` | `redis` | Integer | The Redis listen port. | `6379`
| `redis_owner` | `redis` | String | The Redis Linux user. | `redis`
| `redis_group` | `redis` | String | The Redis Linux group. | `redis`
| `redis_bind_ipv6` | `redis` | Boolean | Flag to enable IPv6. | `true`
| `redis_bind_addr_source` | `redis` | String | The bind address source. Will default to the Ansible `inventory_hostname` unless explicitly set to `default_ipv4_address`. | `inventory_hostname`
| `redis_bind_addrs` | `redis` | String | A space-separated list of hostnames/IP addresses on which Redis listeners will be created.  If `redis_bind_ipv6` is set to `true`, `::1` will be added to the addresses.  The `redis_bind_addr_source` will also be added to the addresses. | `127.0.0.1`
| `iap_redis_packages` | `redis` | List of Strings | The Linux packages to install. | `redis jemalloc`

## Redis Auth Role Variables

There are no default variables for the Redis Auth role other than the Redis common default variables.

## Redis Replication Role Variables

The variables in this section may be overridden in the inventory in the `redis` group vars.

The following table lists the default variables located in `roles/redis_replication/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `redis_sentinel_conf_file` | `redis` | String | The location of the Redis Sentinel configuration file. | `"{{ redis_conf_path }}/sentinel.conf"`
| `redis_sentinel_port` | `redis` | Integer | The Redis Sentinel listen port | `26379`

# SELinux

The `redis` role contains tasks to install custom SELinux profiles (located in `roles/redis/files` and containing the `te` extension).  If your use case requires additional profiles, the files can be placed in the `files` directory and they will be automatically installed by the role.

# Building Your Inventory

To install and configure Redis, add a `redis` group and host(s) to your inventory.  The following inventory shows a basic Redis configuration with a single Redis node with no authentication.

## Example Inventory - Single Redis Node

```
all:
    vars:
        iap_release: 2023.1

    children:
        redis:
            hosts:
                <host1>:
                    ansible_host: <addr1>
```

To enable authentication, add the `redis_auth` flag to the `all` group and set it to `true`.

## Example Inventory - Configure Redis Authentication

```
all:
    vars:
        iap_release: 2023.1
        redis_auth: true

    children:
        redis:
            hosts:
                <host1>:
                    ansible_host: <addr1>
```

To configure a Redis replica set, add the `redis_replication` flag to the `all` group and set it to `true` and add the additional hosts.

## Example Inventory - Configure Redis Replication

```
all:
    vars:
        iap_release: 2023.1
        redis_auth: true
        redis_replication: true

    children:
        redis:
            hosts:
                <host1>:
                    ansible_host: <addr1>
                <host2>:
                    ansible_host: <addr2>
                <host3>:
                    ansible_host: <addr3>
```

# Running the Playbook

To execute all Redis roles, run the `redis.yml` playbook:

```
ansible-playbook redis.yml -i <inventory>
```

You can also run select Redis roles by using the following tags:

* `redis_install`
* `redis_auth`
* `redis_replication`

To execute only the `redis` role (skipping the `redis_auth` and `redis_replication` roles), run the `itential.deployer.redis` playbook with the `redis_install` tag:

```
ansible-playbook itential.deployer.redis -i <inventory> --tags redis_install
```

To execute only the Redis Auth role (skipping the Redis and Redis Replication roles), run the `itential.deployer.redis` playbook with the `redis_auth` tag:

```
ansible-playbook itential.deployer.redis -i <inventory> --tags redis_auth
```

To execute only the Redis Replication role (skipping the Redis and Redis Auth roles), run the `itential.deployer.redis` playbook with the `redis_replication` tag:

```
ansible-playbook itential.deployer.redis -i <inventory> --tags redis_replication
```
