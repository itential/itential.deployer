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

### Replica Priority

Controls which replica Sentinel prefers to promote during failover.
Lower values = higher priority (more likely to be promoted).

**Default:** `auto` (calculates based on position)

**Options:**
- `auto` - Automatic priority based on inventory order:
  - Master: 10
  - First replica: 50
  - Second replica: 100
  - Third replica: 150, etc.
- `0` - Never promote this replica
- `1-255` - Explicit priority value

**Examples:**
```yaml
# Use automatic priorities (recommended)
redis_replica_priority: auto

# Set explicit priority
redis_replica_priority: 25

# Prevent promotion (standby only)
redis_replica_priority: 0
```

**Per-host override in inventory:**
```ini
[redis-replica]
replica1 redis_replica_priority=10
replica2 redis_replica_priority=50
replica3 redis_replica_priority=0  # Never promote
```

## Automatic Redis Maxmemory Calculation

When `redis_maxmemory_bytes` is set to `auto`, the installation process automatically calculates the Redis `maxmemory` value based on the system's total available RAM.

The following formula is used:
`maxmemory = max(redis_maxmemory_min_mb, system_ram × redis_maxmemory_ratio)`

The `max()` function ensures Redis always receives **at least the configured minimum memory**, even on systems with small amounts of RAM.

After the calculation, the value is converted to **bytes**, since Redis expects the `maxmemory` configuration parameter to be specified in bytes.

---

### Example

For a system with **10 GB of RAM**:

* system ram = 10240 MB
* redis max memory ratio = 0.60

The calculation becomes: 10240 × 0.60 = 6144 MB

Converted to bytes: 6144 x 1024 x 1024 = 6442450944 bytes

This value will be written to the Redis configuration as:

`maxmemory 6442450944`

### Manual Override

If `redis_maxmemory_bytes` is set to a numeric value instead of `auto`, the automatic calculation is skipped and the specified value is used directly.

Example:

`redis_maxmemory_bytes: 8589934592`

This will configure Redis with:

`maxmemory 8589934592`

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
| `redis_bind` | String | A space-separated list of hostnames/IP addresses on which Redis listeners will be created. | `bind 127.0.0.1 {{ ansible_default_ipv4.address }}` |
| `redis_tls_enabled` | Boolean | Flag to enable TLS connections. | `false` |
| `redis_tls_port` | Integer | The Redis TLS listen port. | Varies by platform |
| `redis_tls_auth_clients` | String | TLS client authentication setting. | `no` |
| `redis_tls_protocols` | String | Enabled TLS protocol versions. | `TLSv1.2 TLSv1.3` |
| `redis_maxmemory_bytes` | String/Integer | Maximum memory Redis can use (maxmemory). When set to auto, the installer calculates the value from the system RAM using: `maxmemory = max(redis_maxmemory_min_mb, system_ram × redis_maxmemory_ratio)`. If a numeric value is provided, that value (in bytes) is used directly and the automatic calculation is skipped. | `auto` |
| `redis_maxmemory_ratio` | Float | Define how much memory the system will use. Only work if `redis_maxmemory_bytes` is configured as auto. Default value 0.6 means 60%. | `0.60` |
| `redis_maxmemory_min_mb` | Integer | This parameter defines the minimum amount of memory Redis is allowed to use, even if the automatic calculation would result in a smaller value. It acts as a safety floor for the maxmemory calculation. | `512` |
| `redis_certify_report_dir_remote` | String | Remote directory for certification reports. | `/var/tmp/itential-reports/redis` |
| `redis_certify_report_dir_local` | String | Local directory for certification reports. | `/tmp/itential-reports/redis` |

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
| `redis_prometheus_user_enabled` | Boolean | Flag to enable the prometheus user | `false` |

### Replication Variables

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `redis_replicaof` | String | The Redis replicaof setting.<br>Use replicaof to make a Redis instance a copy of another Redis server. | "{{ groups['redis_master'][0] }} {{ redis_port}}" |
| `redis_replica_priority` | String/Integer | Controls which replica Sentinel prefers to promote during failover.<br>Refer to Replica Priority section above for details. | `auto` |

### Sentinel Variables

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `redis_sentinel_conf_file` | String | The location of the Redis Sentinel configuration file. | `/etc/redis/sentinel.conf` |
| `redis_sentinel_log` | String | The location of the Redis Sentinel log file. | `/var/log/redis/sentinel.log` |
| `redis_sentinel_port` | Integer | The Redis Sentinel listen port | `26379` |
| `redis_sentinel_bind` | String | A space-separated list of hostnames/IP addresses on which Redis listeners will be created. | `bind 127.0.0.1 {{ ansible_default_ipv4.address }}` |
| `redis_sentinel_master_name` | String | The Redis master name | `itentialmaster` |
| `redis_sentinel_quorum` | String | The Sentinel quorum setting.<br>Auto-calculate quorum based on sentinel count (recommended).<br>Set to explicit number to override (must be <= number of sentinels). | `auto` |
| `redis_sentinel_certify_report_dir_remote` | String | Remote directory for Sentinel certification reports. | `/var/tmp/itential-reports/sentinel` |
| `redis_sentinel_certify_report_dir_local` | String | Local directory for Sentinel certification reports. | `/tmp/itential-reports/sentinel` |

### PKI Variables

The following table lists the PKI-related variables located in `roles/redis/defaults/main/pki.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `redis_pki_base_dir` | String | Base directory for Redis PKI files. | `/etc/pki/redis` |
| `redis_pki_private_subdir` | String | Subdirectory name for private keys. | `private` |
| `redis_pki_private_dir` | String | Full path to private keys directory. | `{{ redis_pki_base_dir }}/{{ redis_pki_private_subdir }}` |
| `redis_pki_src_dir` | String | Source directory on Ansible controller containing certificates. | `""` |
| `redis_pki_owner` | String | Owner for PKI directories and files. | `redis` |
| `redis_pki_group` | String | Group for PKI directories and files. | `redis` |
| `redis_tls_cert_src` | String | Full source path for Redis server certificate on controller. | `{{ redis_pki_src_dir }}/{{ redis_tls_cert_dest }}` |
| `redis_tls_key_src` | String | Full source path for Redis server private key on controller. | `{{ redis_pki_src_dir }}/{{ redis_tls_key_dest }}` |
| `redis_tls_ca_src` | String | Full source path for CA bundle on controller. | `{{ redis_pki_src_dir }}/{{ redis_tls_ca_dest }}` |
| `redis_tls_dh_params_src` | String | Full source path for DH parameters on controller. | `{{ redis_pki_src_dir }}/{{ redis_tls_dh_params_dest }}` |
| `redis_sentinel_tls_cert_src` | String | Full source path for Sentinel certificate on controller. | `{{ redis_pki_src_dir }}/{{ redis_sentinel_tls_cert_dest }}` |
| `redis_sentinel_tls_key_src` | String | Full source path for Sentinel private key on controller. | `{{ redis_pki_src_dir }}/{{ redis_sentinel_tls_key_dest }}` |

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

To install and configure Redis, add a `redis_master` group and host(s) to your inventory.  The following
inventory shows a basic Redis configuration with a single Redis node with authentication.

### Example Inventory - Single Redis Node

```yaml
all:
  children:
    redis_master:
      hosts:
        <host1>:
          ansible_host: <addr1>
    vars:
        platform_release: 6
```

### Example Inventory - Single Redis Node, Override Source URL

```yaml
all:
  children:
    redis_master:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_release: 6
        redis_source_url: https://github.com/redis/redis/archive/7.2.7.tar.gz
```

### Example Inventory - Single Redis Node, Install Using Packages

```yaml
all:
  children:
    redis_master:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_release: 6
        redis_install_from_source: false
```

To configure a Redis replica set, add the replica hosts to the `redis_replica` group and configure the `redis_replicaof` variable.

### Example Inventory - Configure Redis Replication

```yaml
all:
  vars:
    platform_release: 6
  children:
    redis_master:
      hosts:
        <host1>:
          ansible_host: <addr1>

    redis_replica:
      hosts:
        <host2>:
          ansible_host: <addr2>
        <host3>:
          ansible_host: <addr3>
      vars:
        redis_replicaof: <master-hostname-or-ip> <redis-port> # defaults to "{{ groups['redis_master'][0] }} {{ redis_port}}"
```

To configure Sentinels, add the sentinel hosts to the `redis_sentinel` group.

```yaml
all:
  vars:
    platform_release: 6
  children:
    redis_master:
      hosts:
        <host1>:
          ansible_host: <addr1>

    redis_replica:
      hosts:
        <host2>:
          ansible_host: <addr2>
        <host3>:
          ansible_host: <addr3>
      vars:
        redis_replicaof: <master-hostname-or-ip> <redis-port> # defaults to "{{ groups['redis_master'][0] }} {{ redis_port}}"

    redis_sentinel:
      hosts:
        <host4>:
          ansible_host: <addr4>
        <host5>:
          ansible_host: <addr5>
        <host6>:
          ansible_host: <addr6>
```

## Running the Playbook

To execute the Redis role, run the `redis` playbook:

```bash
ansible-playbook itential.deployer.redis -i <inventory>
```