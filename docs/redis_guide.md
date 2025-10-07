# Redis Role

The playbook and role in this section install and configure Redis for the Itential Automation
Platform.  There is one Redis-related role which installs Redis and performs a base configuration.
Optionally configures authentication and replication.

## Redis Install

The `redis` role performs a base install of Redis including any OS packages required.  It will
compile and install any custom SELinux profiles.  It creates the appropriate Linux users,
directories, log files, and systemd services.  It uses a template to generate a configuration file
based on the variables defined in the redis group vars.  It will start the Redis service when
complete.

## Authentication

Optionally, the `redis` role performs tasks to require authentication (username and password) when
communicating with the Redis server.  It adjusts the Redis config file and adds each of the
required users and applies appropriate ACLs (see table).  The "default" Redis user is disabled.
It modifies the Redis config file to use the appropriate user while doing replication.  It adjusts
the Sentinel config file to enable the correct Sentinel user to monitor the redis cluster, if
required.  It disables the default user in both Redis and Redis Sentinel.

More info on Redis authorization: <https://redis.io/docs/manual/security/>

| User Name | Default Password | Description |
| :-------- | :--------------- | :---------- |
| admin | admin | Has full access to the Redis database. |
| itential | itential | Has access to all keys, all channels, and all commands except: -asking -cluster -readonly -readwrite -bgrewriteaof -bgsave -failover -flushall -flushdb -psync -replconf -replicaof -save -shutdown -sync |
| repluser | repluser | Has access to the minimum set of commands to perform replication. |
| sentineluser | sentineluser | Has access to the minimum set of commands to perform sentinel monitoring. |
| prometheus | prometheus | Has access to the minimum set of commands to perform Redis and Sentinel monitoring with Prometheus. Required by the optional redis_exporter service. |

:::(Warning) (⚠ Warning: ) It is assumed that these default passwords will be changed to meet more
rigorous standards.  These are intended to be defaults strictly used just for ease of the
installation.  It is highly recommended that sensitive data be encrypted using Ansible Vault.

## Replication

Optionally, the `redis` role performs the steps required to create a Redis replica set.  It uses a
template to generate a Redis Sentinel config file.  It modifies the Redis config file to turn off
protected-mode.  It assumes that the first host defined in the inventory file is the initial
primary.  It will update the config file for the non-primary Redis servers to replicate from the
primary using hostname.  It will start the Redis Sentinel service when complete.

For more information on Redis replication: <https://redis.io/docs/manual/replication/>

## Variables

### Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be
overridden by the user.  Since these variable files are included at run-time based on the Itential
Platform release and OS major version, they have a higher precedence than the variables in the
inventory and are not easily overridden.

### Global Variables

The variables in this section can be configured in the inventory in the `all` group or the `redis`
group.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `platform_release` | Fixed-point | Designates the Itential Platform major version. | N/A |

Defining `platform_release` in the inventory is optional.  However, this variable, along with the
OS and major version, is used to determine the default installation variables.  If
`platform_release` is not defined, then either `redis_packages` or `redis_source_url` must be
defined.  Refer to the [Overriding Installation Variables](#overriding-installation-variables)
section for details.

### Redis Role Variables

The variables in this section may be overridden in the inventory in the `redis` group.

### Install Variables

The following tables lists the default variables located in `roles/redis/defaults/main/install.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `redis_install_from_source` | String | The method used to install Redis. Set to `true` to install from source (default). Set to `false` to install using DNF packages. | `true` |
| `redis_build_packages` | List | The packages required to build Redis from source | See role. |
| `redis_security_packages` | List | The packages required to configure SELinux | See role. |
| `redis_packages` | List | The Redis packages to install | Varies depending on OS and Platform release |
| `redis_source_url` | String | The Redis source URL | Varies depending on OS and Platform release |
| `redis_remi_repo_url` | String | The URL of the Remi repo RPM. Note: this is only used when the `redis_install_from_source` is set to `false` and the Remi packages are being installed. | `http://rpms.remirepo.net/enterprise/remi-release-{{ ansible_distribution_major_version }}.rpm` |
| `redis_epel_repo_url` | String | The URL of the EPEL repo RPM. Note: this is only used when the `redis_install_from_source` is set to `false` and the Remi packages are being installed. | `https://dl.fedoraproject.org/pub/epel/epel-release-latest-{{ ansible_distribution_major_version }}.noarch.rpm` |

### Redis Variables

The following tables lists the default variables located in `roles/redis/defaults/main/redis.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `redis_bin_dir` | String | The Redis binary directory. | `/usr/local/bin` (installing from source) `/usr/bin` (installing from package) |
| `redis_conf_dir` | String | The Redis configuration directory. | `/etc/redis` |
| `redis_conf_file` | String | The location of the Redis configuration file. | `/etc/redis/redis.conf` |
| `redis_log_dir` | String | The Redis log directory. | `/var/log/redis` |
| `redis_log` | String | The location of the Redis log file. | `/var/log/redis/redis.log` |
| `redis_db_filename` | String | The name of the Redis data file. | `dump.rdb` |
| `redis_data_dir` | String | The location of the Redis data directory. | `/var/lib/redis` |
| `redis_port` | Integer | The Redis listen port. | `6379` |
| `redis_owner` | String | The Redis Linux user. | `redis` |
| `redis_group` | String | The Redis Linux group. | `redis` |
| `redis_bind_ipv6` | Boolean | Flag to enable IPv6. | `true` |
| `redis_bind_addr_source` | String | The bind address source. Will default to the Ansible `inventory_hostname` unless explicitly set to `default_ipv4_address`. | `inventory_hostname` |
| `redis_bind_addrs` | String | A space-separated list of hostnames/IP addresses on which Redis listeners will be created. If `redis_bind_ipv6` is set to `true`, `::1` will be added to the addresses. The `redis_bind_addr_source` will also be added to the addresses. | `127.0.0.1` |
| `redis_tls_enabled` | Boolean | Flag to enable TLS connections. | `false` |

### Auth Variables

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `redis_auth_enabled` | Boolean | Flag to enable Redis authentication. When set to to `true`, Redis authentication will be configured. | `true` |
| `redis_user_admin_password` | String | The Redis admin user's default password | `admin` |
| `redis_user_itential_password` | String | The Redis itential user's default password | `itential` |
| `redis_user_repluser_password` | String | The Redis repluser user's default password | `repluser` |
| `redis_user_sentineladmin_password` | String | The Redis Sentinel admin user's default password | `admin` |
| `redis_user_sentineluser_password` | String | The Redis Sentinel default user's default password | `sentinel` |
| `redis_user_prometheus_password` | String | The Redis prometheus user's default password | `prometheus` |

### Replication Variables

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `redis_replication_enabled` | Boolean | Flag to enable Redis replication. When set to `true`, Redis replication will be configured and the Redis Sentinel service started. | `false` |
| `redis_sentinel_port` | Integer | The Redis Sentinel listen port | `26379` |
| `redis_sentinel_conf_file` | String | The location of the Redis Sentinel configuration file. | `/etc/redis/sentinel.conf` |
| `redis_sentinel_log` | String | The location of the Redis Sentinel log file. | `/var/log/redis/sentinel.log` |
| `redis_master_name` | String | The Redis master name | `itentialmaster` |

### Offline Variables

There are several variables used when download and installing Redis in offline mode.  These
variables will not be documented here since they will rarely need to be overridden in the inventory.

## SELinux

The `redis` role contains tasks to install custom SELinux profiles (located in `roles/redis/files`
and containing the `te` extension).  If your use case requires additional profiles, the files can
be placed in the `files` directory and they will be automatically installed by the role.

## Overriding Installation Variables

This role supports installing Redis from source (default) or from packages using RPMs.  The
`redis_install_from_source` flag is used to determine which method will be used.  If
`redis_install_from_source` is set to `true` , the Redis source code defined by the
`redis_source_url` variable will downloaded and installed.  Alternatively, if
`redis_install_from_source` is set to `false`, the Redis packages defined by the `redis_packages`
variable will be installed using DNF.  When the `platform_release` is defined in the inventory,
the `redis_source_url` or `redis_packages` variable will automatically be defaulted to a supported
value for the Platform and OS.  However, users can override the installation variables by defining
either the `redis_source_url` or `redis_packages` in the inventory.

| `platform_release` defined in inventory? | `redis_install_from_source` | `redis_source_url` | `redis_packages` |
| :--------------------------------------- | :-------------------------- | :----------------- | :--------------- |
| Yes | `true` | defaulted to supported value may be overridden | N/A |
| Yes | `false` | N/A | defaulted to supported value may be overridden |
| No | `true` | must be defined in inventory | N/A |
| No | `false` | N/A | must be defined in inventory |

When installing from packages, if the package contains `remi`, the EPEL and Remi repos will be
installed.

The default values are not documented in this guide since they may change.  The current values can
be found in `roles/redis/vars/platform-release-<platform_release>.yml`.

## Building Your Inventory

To install and configure Redis, add a `redis` group and host(s) to your inventory.  The following
inventory shows a basic Redis configuration with a single Redis node with no authentication.

### Example Inventory - Single Redis Node

```yaml
all:
  children:
    redis:
      hosts:
        <host1>:
          ansible_host: <addr1>
    vars:
        platform_release: 6.0
```

### Example Inventory - Single Redis Node, Override Source URL

```yaml
all:
  children:
    redis:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        redis_source_url: https://github.com/redis/redis/archive/7.2.7.tar.gz
```

### Example Inventory - Single Redis Node, Install Using Packages

```yaml
all:
  children:
    redis:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_release: 6.0
        redis_install_from_source: false
```

To enable authentication, add the `redis_auth_enabled` flag to the `redis` group and set it to `true`.

### Example Inventory - Configure Redis Authentication

```yaml
all:
  children:
    redis:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_release: 6.0
        redis_auth_enabled: true
```

To configure a Redis replica set, add the `redis_replication_enabled` flag to the `redis` group and set it to `true` and add the additional hosts.

### Example Inventory - Configure Redis Replication

```yaml
all:
  children:
    redis:
      hosts:
        <host1>:
          ansible_host: <addr1>
        <host2>:
          ansible_host: <addr2>
        <host3>:
          ansible_host: <addr3>
      vars:
        platform_release: 6.0
        redis_auth_enabled: true
        redis_replication_enabled: true
```

## Running the Playbook

To execute the Redis role, run the `redis` playbook:

```bash
ansible-playbook itential.deployer.redis -i <inventory>
```
