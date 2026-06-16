# TLS Configuration Guide

## Overview

TLS is **enabled by default** for every component the deployer manages. If you are deploying
to a non-production environment and want to skip TLS, you must explicitly disable it. In all
other cases, your main job is to tell the deployer where your certificates live on the Ansible
control node.

The deployer never generates certificates. You must provide them. The deployer copies them from
your control node to each target host and wires the paths into each component's configuration
file.

### What "TLS" means per component

| Component | What TLS controls |
| --- | --- |
| Redis | Encrypts connections between Redis nodes and from Itential Platform to Redis |
| MongoDB | Encrypts connections between MongoDB nodes and from Itential Platform to MongoDB |
| Itential Platform (HTTPS) | Encrypts browser and API connections to the Platform web server |
| Itential Platform (MongoDB client) | The CA cert Platform uses to trust the MongoDB TLS certificate |
| Itential Platform (Redis client) | The CA cert Platform uses to trust the Redis TLS certificate |

---

## Before You Start

### What you need

You need the following certificate files on your Ansible control node before running the deployer.
How you obtain them (internal CA, Let's Encrypt, self-signed) is outside the scope of this guide.

| Component | Files required |
| --- | --- |
| Redis | `<hostname>.crt`, `<hostname>.key`, `ca-bundle.crt` |
| MongoDB | `<hostname>.pem` (cert and key concatenated), `ca-bundle.crt` |
| Itential Platform (HTTPS) | `<hostname>.crt`, `<hostname>.key`, `ca-bundle.crt` |
| Itential Platform (MongoDB client) | `ca-bundle.crt` (the CA that signed the MongoDB cert) |
| Itential Platform (Redis client) | `ca-bundle.crt` (the CA that signed the Redis cert) |

### MongoDB certificate format

MongoDB requires a single `.pem` file that contains both the certificate and the private key
concatenated together. If your CA gives you separate files, combine them:

```bash
cat server.crt server.key > hostname.pem
chmod 600 hostname.pem
```

### Default filename convention

By default, the deployer looks for certificate files named after each target host's
`inventory_hostname` (for example, `mongodb01.example.com.pem`). You can override the filenames
in your inventory if you prefer shared or role-level certificates. See
[Certificate Filename Strategies](#certificate-filename-strategies) below.

---

## Redis TLS

TLS is **on by default** for Redis. The deployer will:

- Create `/etc/pki/redis/` on each Redis node.
- Copy your certificate files into that directory.
- Write a `redis.conf` that disables the plain TCP port and enables the TLS port.
- Configure Sentinel with TLS as well when Sentinel nodes are present.

### Set `redis_pki_src_dir`

You must set `redis_pki_src_dir` on your Redis nodes. This is the path on your Ansible
control node where the Redis certificate files live.

```yaml
redis_nodes:
  vars:
    redis_pki_src_dir: /home/deploy/certs/redis
```

That directory must contain:

```text
/home/deploy/certs/redis/
  redis01.example.com.crt
  redis01.example.com.key
  redis02.example.com.crt
  redis02.example.com.key
  redis03.example.com.crt
  redis03.example.com.key
  ca-bundle.crt
```

### Redis Sentinel TLS

Sentinel TLS is controlled by the same `redis_tls_enabled` flag as the data nodes. There is no
separate enable flag for Sentinel. When `redis_tls_enabled: true`, the deployer configures TLS
on every host in the `redis_sentinel` group using the same source directory (`redis_pki_src_dir`)
as the data nodes.

In the standard HA2 topology all three Redis hosts are members of both `redis_nodes` and
`redis_sentinel`. This means the certs you put in `redis_pki_src_dir` cover both roles on the
same host with no extra configuration. The deployer writes a separate `sentinel.conf` for each
Sentinel node, pointing to that node's cert files.

By default, Sentinel looks for files named `{{ inventory_hostname }}.crt` and
`{{ inventory_hostname }}.key` -- the same names as the Redis data node certs. On a host that
runs both Redis and Sentinel, those filenames resolve to the same files, so one cert serves
both processes. You only need to override `redis_sentinel_tls_cert_file` and
`redis_sentinel_tls_key_file` if you want Sentinel to use a different certificate than the
Redis data process on the same host.

The CA cert (`ca-bundle.crt`) is always shared between the Redis data process and Sentinel.

Sentinel is configured with `tls-auth-clients no` by default, meaning Sentinel does not
require clients to present a certificate when connecting. Override `redis_tls_auth_clients`
to `yes` only if your security policy requires mutual TLS across the entire cluster.

#### Using per-role certs for Sentinel

If you want all Sentinel nodes to share a single cert (with SANs covering all three hosts),
override the Sentinel cert file variables in `redis_nodes` alongside the data node overrides:

```yaml
redis_nodes:
  vars:
    redis_pki_src_dir: /home/deploy/certs/redis
    redis_tls_cert_file: redis.crt
    redis_tls_key_file: redis.key
    redis_sentinel_tls_cert_file: redis.crt
    redis_sentinel_tls_key_file: redis.key
```

### Disabling Redis TLS

Set `redis_tls_enabled: false` under your Redis group vars:

```yaml
redis_nodes:
  vars:
    redis_tls_enabled: false
```

### Redis variable reference

| Variable | Default | Description |
| --- | --- | --- |
| `redis_tls_enabled` | `true` | Enable or disable TLS for Redis and Sentinel |
| `redis_pki_src_dir` | `""` | **Required when TLS is on.** Path to certs on the control node |
| `redis_pki_base_dir` | `/etc/pki/redis` | Where certs land on the target host |
| `redis_tls_cert_file` | `{{ inventory_hostname }}.crt` | Server certificate filename |
| `redis_tls_key_file` | `{{ inventory_hostname }}.key` | Server private key filename |
| `redis_tls_ca_file` | `ca-bundle.crt` | CA bundle filename |
| `redis_sentinel_tls_cert_file` | `{{ inventory_hostname }}.crt` | Sentinel certificate filename |
| `redis_sentinel_tls_key_file` | `{{ inventory_hostname }}.key` | Sentinel private key filename |
| `redis_tls_auth_clients` | `no` | Require client certificates (`yes` or `no`) |
| `redis_tls_protocols` | `TLSv1.3` | Allowed TLS protocol versions |

---

## MongoDB TLS

TLS is **on by default** for MongoDB. The deployer will:

- Create `/etc/pki/mongodb/` on each MongoDB node.
- Copy your certificate files into that directory.
- Write a `mongod.conf` that enables `requireTLS` mode.
- Deploy a replica set authentication keyfile when replication is enabled.

### Set `mongodb_pki_src_dir`

Set `mongodb_pki_src_dir` on your MongoDB nodes:

```yaml
mongodb_node:
  vars:
    mongodb_pki_src_dir: /home/deploy/certs/mongodb
```

That directory must contain:

```text
/home/deploy/certs/mongodb/
  mongodb01.example.com.pem
  mongodb02.example.com.pem
  mongodb03.example.com.pem
  ca-bundle.crt
```

If replication is enabled, also place the replica set keyfile here:

```text
  replica.key
```

### Disabling MongoDB TLS

Set `mongodb_tls_enabled: false`. You can also leave TLS enabled but skip copying certs
(if certs are already on the target hosts) by setting `mongodb_tls_copy_certs: false`.

```yaml
mongodb_node:
  vars:
    mongodb_tls_enabled: false
```

### MongoDB variable reference

| Variable | Default | Description |
| --- | --- | --- |
| `mongodb_tls_enabled` | `true` | Enable or disable TLS for MongoDB |
| `mongodb_tls_copy_certs` | `true` | Copy certs from the control node. Set to `false` if certs are already in place |
| `mongodb_pki_src_dir` | `""` | **Required when copy is on.** Path to certs on the control node |
| `mongodb_pki_base_dir` | `/etc/pki/mongodb` | Where certs land on the target host |
| `mongodb_tls_server_cert_file` | `{{ inventory_hostname }}.pem` | Combined cert+key PEM filename |
| `mongodb_tls_ca_file` | `ca-bundle.crt` | CA bundle filename |
| `mongodb_auth_key_file` | `replica.key` | Replica set authentication keyfile name |

---

## Itential Platform TLS

Itential Platform has three independent TLS connections to configure:

1. **HTTPS** -- the Platform web server (browser and API access)
2. **MongoDB client** -- how Platform connects to MongoDB
3. **Redis client** -- how Platform connects to Redis

Each has its own source directory variable and its own copy flag. This lets you manage the
certificate bundles separately, which matters when your MongoDB, Redis, and HTTPS certs come
from different CAs.

### Set Platform source directories

```yaml
platform:
  vars:
    platform_https_pki_src_dir: /home/deploy/certs/platform/https
    platform_mongodb_pki_src_dir: /home/deploy/certs/mongodb
    platform_redis_pki_src_dir: /home/deploy/certs/redis
```

Directory contents expected:

```text
/home/deploy/certs/platform/https/
  platform01.example.com.crt
  platform01.example.com.key
  platform02.example.com.crt
  platform02.example.com.key
  ca-bundle.crt

/home/deploy/certs/mongodb/
  ca-bundle.crt           (only the CA bundle is needed here for Platform)

/home/deploy/certs/redis/
  ca-bundle.crt           (only the CA bundle is needed here for Platform)
```

Itential Platform only needs the CA bundle for MongoDB and Redis -- it does not need the
server-side certificates for those components.

### Disabling Platform TLS

Each TLS connection can be disabled independently:

```yaml
platform:
  vars:
    # Disable the HTTPS web server (serve HTTP only)
    platform_webserver_https_enabled: false

    # Disable Platform's TLS connection to MongoDB
    platform_mongo_tls_enabled: false

    # Disable Platform's TLS connection to Redis
    platform_redis_tls_enabled: false
```

To skip copying certs without disabling TLS (useful when certs are already deployed):

```yaml
platform:
  vars:
    platform_webserver_https_copy_certs: false
    platform_mongodb_copy_certs: false
    platform_redis_copy_certs: false
```

### Platform HTTPS variable reference

| Variable | Default | Description |
| --- | --- | --- |
| `platform_webserver_https_enabled` | `true` | Enable or disable the HTTPS listener |
| `platform_webserver_https_port` | `3443` | HTTPS port |
| `platform_webserver_https_copy_certs` | `true` | Copy HTTPS certs from the control node |
| `platform_https_pki_src_dir` | `""` | **Required when copy is on.** Path to HTTPS certs on the control node |
| `platform_pki_base_dir` | `/etc/pki/itential-platform` | Root PKI directory on the target |
| `platform_https_cert_file` | `{{ inventory_hostname }}.crt` | HTTPS certificate filename |
| `platform_https_key_file` | `{{ inventory_hostname }}.key` | HTTPS private key filename |
| `platform_https_ca_file` | `ca-bundle.crt` | HTTPS CA bundle filename |

### Platform MongoDB client variable reference

| Variable | Default | Description |
| --- | --- | --- |
| `platform_mongo_tls_enabled` | `true` | Enable TLS for Platform's MongoDB connection |
| `platform_mongodb_copy_certs` | `true` | Copy the MongoDB CA cert to the Platform node |
| `platform_mongodb_pki_src_dir` | `""` | **Required when copy is on.** Path to MongoDB CA on the control node |
| `platform_mongodb_ca_file` | `ca-bundle.crt` | MongoDB CA bundle filename |
| `platform_mongo_tls_allow_invalid_certificates` | `false` | Skip certificate validation (not recommended in production) |

### Platform Redis client variable reference

| Variable | Default | Description |
| --- | --- | --- |
| `platform_redis_tls_enabled` | `true` | Enable TLS for Platform's Redis connection |
| `platform_redis_copy_certs` | `true` | Copy the Redis CA cert to the Platform node |
| `platform_redis_pki_src_dir` | `""` | **Required when copy is on.** Path to Redis CA on the control node |
| `platform_redis_ca_file` | `ca-bundle.crt` | Redis CA bundle filename |

---

## Certificate Filename Strategies

By default, every component expects certificate files named after each target host's
`inventory_hostname`. For example, if your Redis nodes are named `redis01.example.com`,
`redis02.example.com`, and `redis03.example.com`, the deployer looks for:

```text
redis01.example.com.crt
redis01.example.com.key
redis02.example.com.crt
...
```

This works well but requires one certificate per host. Two alternatives reduce that burden.

### Option A: One certificate per role

Generate one certificate for each role, with Subject Alternative Names (SANs) covering all
hostnames in that role. Name the files something generic and override the filename variables
in your inventory.

```yaml
redis_nodes:
  vars:
    redis_pki_src_dir: /home/deploy/certs/redis
    redis_tls_cert_file: redis.crt
    redis_tls_key_file: redis.key
    redis_sentinel_tls_cert_file: redis.crt
    redis_sentinel_tls_key_file: redis.key

mongodb_node:
  vars:
    mongodb_pki_src_dir: /home/deploy/certs/mongodb
    mongodb_tls_server_cert_file: mongodb.pem

platform:
  vars:
    platform_https_pki_src_dir: /home/deploy/certs/platform/https
    platform_https_cert_file: platform.crt
    platform_https_key_file: platform.key
```

The SANs on the Redis cert would need to list all Redis node hostnames:

```text
DNS:redis01.example.com, DNS:redis02.example.com, DNS:redis03.example.com
```

### Option B: One certificate for everything

Use a single wildcard or multi-domain certificate across all roles. This is the simplest
approach for lab or development environments.

```yaml
all:
  vars:
    redis_pki_src_dir: /home/deploy/certs/shared
    redis_tls_cert_file: shared.crt
    redis_tls_key_file: shared.key
    redis_sentinel_tls_cert_file: shared.crt
    redis_sentinel_tls_key_file: shared.key

    mongodb_pki_src_dir: /home/deploy/certs/shared
    mongodb_tls_server_cert_file: shared.pem

    platform_https_pki_src_dir: /home/deploy/certs/shared
    platform_mongodb_pki_src_dir: /home/deploy/certs/shared
    platform_redis_pki_src_dir: /home/deploy/certs/shared
    platform_https_cert_file: shared.crt
    platform_https_key_file: shared.key
```

Your shared cert directory would look like:

```text
/home/deploy/certs/shared/
  shared.crt
  shared.key
  shared.pem        (cat shared.crt shared.key > shared.pem)
  ca-bundle.crt
```

---

## Simplest Working Example

This is the minimum inventory configuration required to deploy a full HA2 stack with TLS. It
assumes all your certificates are signed by a single internal CA, you have one cert per host
(the default), and your cert files are organized by role in subdirectories under
`/home/deploy/certs/`.

```yaml
all:
  vars:
    platform_release: 6

  children:
    redis_master:
      hosts:
        redis01.example.com:

    redis_replica:
      hosts:
        redis02.example.com:
        redis03.example.com:

    redis_sentinel:
      hosts:
        redis01.example.com:
        redis02.example.com:
        redis03.example.com:

    redis_nodes:
      hosts:
        redis01.example.com:
        redis02.example.com:
        redis03.example.com:
      vars:
        redis_pki_src_dir: /home/deploy/certs/redis

    mongodb_primary:
      hosts:
        mongodb01.example.com:

    mongodb_replica:
      hosts:
        mongodb02.example.com:
        mongodb03.example.com:

    mongodb_node:
      hosts:
        mongodb01.example.com:
        mongodb02.example.com:
        mongodb03.example.com:
      vars:
        mongodb_pki_src_dir: /home/deploy/certs/mongodb

    platform:
      hosts:
        platform01.example.com:
        platform02.example.com:
      vars:
        platform_encryption_key: <64-char hex string>
        platform_packages:
          - itential-platform-<version>.noarch.rpm
        platform_mongo_url: >-
          mongodb://mongodb01.example.com:27017,mongodb02.example.com:27017,
          mongodb03.example.com:27017/itential?replicaSet=rs0
        platform_redis_sentinels:
          - host: redis01.example.com
            port: 26379
          - host: redis02.example.com
            port: 26379
          - host: redis03.example.com
            port: 26379
        platform_https_pki_src_dir: /home/deploy/certs/platform
        platform_mongodb_pki_src_dir: /home/deploy/certs/mongodb
        platform_redis_pki_src_dir: /home/deploy/certs/redis
```

Control node certificate layout for this example:

```text
/home/deploy/certs/
  redis/
    redis01.example.com.crt
    redis01.example.com.key
    redis02.example.com.crt
    redis02.example.com.key
    redis03.example.com.crt
    redis03.example.com.key
    ca-bundle.crt
  mongodb/
    mongodb01.example.com.pem
    mongodb02.example.com.pem
    mongodb03.example.com.pem
    ca-bundle.crt
    replica.key
  platform/
    platform01.example.com.crt
    platform01.example.com.key
    platform02.example.com.crt
    platform02.example.com.key
    ca-bundle.crt
```

---

## Common Mistakes

### Missing `*_pki_src_dir`

The deployer fails early if a TLS component is enabled (the default) but the corresponding
source directory variable is not set. The error references a missing or empty source path.
Set the appropriate `*_pki_src_dir` variable for each role group.

### MongoDB `.pem` file format

MongoDB requires a single file containing both the certificate and private key. If your CA
delivers them separately, combine them before running the deployer:

```bash
cat server.crt server.key > mongodb01.example.com.pem
chmod 600 mongodb01.example.com.pem
```

### Itential Platform needs three source directories

Itential Platform connects to three services over TLS (its own HTTPS listener, MongoDB, and
Redis) and uses a separate source directory variable for each. A common mistake is setting only
`platform_https_pki_src_dir` and forgetting `platform_mongodb_pki_src_dir` and
`platform_redis_pki_src_dir`.

### Redis TLS variables belong on `redis_nodes`

The `redis_tls_enabled` and `redis_pki_src_dir` variables apply to all Redis data nodes.
Set them under the `redis_nodes` group, which should contain all Redis hosts: master and
replicas. Sentinel-specific cert file overrides (`redis_sentinel_tls_cert_file`,
`redis_sentinel_tls_key_file`) are also set here since Sentinel runs on the same hosts.

### CA bundle filename

The deployer looks for a file named `ca-bundle.crt` in the source directory by default. If
your CA delivers a file with a different name, either rename it or override the CA filename
variable for the relevant role (`redis_tls_ca_file`, `mongodb_tls_ca_file`,
`platform_https_ca_file`, etc.).
