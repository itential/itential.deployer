# Certification Guide

## Overview

The certification playbooks validate an Itential installation after it has been deployed. Each playbook runs a set of checks against the target hosts, generates a Markdown report on the remote host, and fetches a copy to the Ansible control node.

Certification is read-only. It does not modify any configuration or restart any services.

## Playbooks

| Playbook | Description |
|----------|-------------|
| `itential.deployer.certify` | Run all certification playbooks (Redis + MongoDB + Platform) |
| `itential.deployer.certify_redis` | Certify Redis and Sentinel hosts |
| `itential.deployer.certify_mongodb` | Certify MongoDB hosts |
| `itential.deployer.certify_platform` | Certify Itential Platform hosts |

## Running Certification

Run all components at once:

```bash
ansible-playbook -i <inventory> itential.deployer.certify
```

Run a single component:

```bash
ansible-playbook -i <inventory> itential.deployer.certify_platform
```

Reports are saved in two locations after each run:

| Component | Remote default | Local default |
|-----------|---------------|---------------|
| Redis | `/var/tmp/itential-reports/redis/` | `/tmp/itential-reports/redis/` |
| Sentinel | `/var/tmp/itential-reports/sentinel/` | `/tmp/itential-reports/sentinel/` |
| MongoDB | `/var/tmp/itential-reports/mongodb/` | `/tmp/itential-reports/mongodb/` |
| Platform | `/var/tmp/itential-reports/platform/` | `/tmp/itential-reports/platform/` |

Each report is named `<component>-report-<inventory_hostname>.md`.

## Redis Certification Report

The Redis report runs on every host in the `redis_master` and `redis_replica` groups. Each host produces its own report.

### Sections

| Section | Description |
|---------|-------------|
| Host Details | OS, hardware, networking, SELinux status |
| Service Status | Systemd state and whether the redis-server process is running |
| Connectivity | `redis-cli PING` result using the admin user |
| Version Information | Redis server version string |
| Redis Metrics | Role (master/replica), connected slaves, replication link status, client count |
| Configuration File | Existence and permissions of `/etc/redis/redis.conf` and the systemd unit file |
| TLS Certificates | Full cert inspection when `redis_tls_enabled: true`; shows "DISABLED" otherwise |
| Redis User Auth Tests | Login test for each configured user |
| Recent Log Entries | Last 50 lines of the Redis log |
| Validation Summary | Overall PASSED/FAILED based on service active + connectivity |

### TLS Certificates (Redis)

Shown only when `redis_tls_enabled: true`.

| Check | Description |
|-------|-------------|
| Files table | Existence and permissions for the certificate, private key, and CA bundle |
| Certificate details | Subject and issuer |
| Validity | Not Before / Not After dates and a 30-day expiry warning |
| Subject Alternative Names | Full SAN list from the certificate |
| SAN correlation | Whether `inventory_hostname` and `ansible_host` appear in the SANs |
| Cert-Key Match | Confirms the certificate and private key are a matched pair |
| Chain Valid | Validates the certificate chain against the CA bundle |
| CA Bundle Validity | CA dates and expiry warning |
| Live TLS Handshake | Connects using `openssl s_client` and reports the verify return code |

### Redis User Auth Tests

The admin and itential users are always tested. The following users are only tested when the corresponding topology is present in the inventory:

| User | Tested when |
|------|-------------|
| `repluser` | `redis_replica` group has at least one host |
| `sentineluser` | `redis_sentinel` group has at least one host |
| `monitor` | `redis_monitor_user_enabled: true` |

## Sentinel Certification Report

The Sentinel report runs on every host in the `redis_sentinel` group.

### Sections

| Section | Description |
|---------|-------------|
| Host Details | OS, hardware, networking, SELinux status |
| Service Status | Systemd state and whether the redis-sentinel process is running |
| Connectivity | `redis-cli` PING to the sentinel port |
| Sentinel Detection | Whether the sentinel process was detected |
| Sentinel INFO | Role, master name, known sentinels, known replicas |
| Master Monitoring | The master set being monitored and its quorum, failover, and sync settings |
| Known Sentinels | List of sentinels in the cluster |
| Known Replicas | List of replicas known to this sentinel |
| Master Status | Whether the master is reachable (no flags indicating down) |
| Configuration File | Existence and permissions of `/etc/redis/sentinel.conf` |
| User Auth Tests | Login test for the sentineluser and monitor user |
| Recent Log Entries | Last 50 lines of the sentinel log |
| Validation Summary | Overall PASSED/FAILED |

## MongoDB Certification Report

The MongoDB report runs on every host in the `mongodb` group. Each host produces its own report.

### Sections

| Section | Description |
|---------|-------------|
| Host Details | OS, hardware, networking, SELinux status |
| Service Status | Systemd state and whether the mongod process is running |
| Connectivity | `mongosh` connection test |
| Version Information | MongoDB server version |
| Configuration File | Existence, permissions, and parsed data directory and log path |
| TLS Certificates | Full cert inspection when TLS is enabled in mongod.conf; shows "DISABLED" otherwise |
| Server Status | Output of `db.serverStatus()` |
| Replica Set | Status, configuration, and member details — only when replication is configured |
| User Accounts | List of configured MongoDB users |
| Databases | List of databases and their sizes |
| Recent Log Entries | Last 50 lines of the MongoDB log |
| Security | Authentication and security settings |
| Validation Summary | Overall PASSED/FAILED |

### TLS Certificates (MongoDB)

Shown only when TLS mode (`requireTLS`, `preferTLS`, or `allowTLS`) is configured in `/etc/mongod.conf`.

| Check | Description |
|-------|-------------|
| Files table | Existence and permissions for the combined PEM file and CA bundle |
| Certificate details | Subject and issuer |
| Validity | Not Before / Not After dates and a 30-day expiry warning |
| Subject Alternative Names | Full SAN list from the certificate |
| SAN correlation | Whether `inventory_hostname` and `ansible_host` appear in the SANs |
| Chain Valid | Validates the certificate chain against the CA bundle |
| CA Bundle Validity | CA dates and expiry warning |
| Live TLS Handshake | Connects using `openssl s_client` and reports the verify return code |

MongoDB uses a combined PEM file (cert + key concatenated), so cert-key match via public key comparison is not applicable.

## Platform Certification Report

The Platform report runs on every host in the `platform` and `platform_secondary` groups.

### Host Details

Operating system distribution, kernel, architecture, CPU, memory, disk mounts, networking, SELinux status, and firewalld state.

### Service Status

Systemd service state and whether the Itential Platform process is running.

### Configuration Files

Confirms the properties file and systemd unit file are present and shows file permissions.

### Critical Configuration Properties

Key values read directly from `platform.properties`: MongoDB URL and TLS settings, Redis host and Sentinel configuration, webserver ports, log file paths, and the default admin username.

### Custom Services

The configured custom services directory.

### TLS Certificates

TLS certification covers two areas: the HTTPS webserver certificate and the MongoDB client CA.

#### HTTPS Webserver

| Check | Description |
|-------|-------------|
| Files table | Existence and permissions for the certificate, private key, and CA bundle |
| Certificate details | Subject, issuer, serial number, signature algorithm, public key algorithm |
| Validity | Not Before / Not After dates and a 30-day expiry warning |
| CA Bundle Validity | Dates and expiry warning — only shown when the CA bundle is present on the server |
| Subject Alternative Names | Full SAN list from the certificate |
| SAN correlation | Whether `inventory_hostname` and `ansible_host` appear in the SANs |
| Cert-Key Match | Confirms the certificate and private key are a matched pair |
| Chain Valid | Validates the certificate chain against the CA bundle — only checked when the CA bundle is present |
| Live TLS Handshake | Connects to the Platform HTTPS port using `openssl s_client` and reports the verify return code — only run when the CA bundle is present |

The HTTPS CA bundle (`ca-bundle.crt`) is not copied to the server by the deployer because it is not required for Platform to serve HTTPS. Its presence on the server is optional. When it is absent, Chain Valid and Live TLS Handshake report "NOT CHECKED" and "Not tested" respectively. This is expected behavior and is not a blocking condition.

#### MongoDB Client TLS

Shown only when `mongo_tls_enabled = true` in the properties file.

| Check | Description |
|-------|-------------|
| CA file table | Existence and permissions of the MongoDB CA bundle |
| CA details | Subject, issuer, validity dates, and 30-day expiry warning — only shown when the CA bundle is present |
| Live MongoDB TLS Handshake | Connects to the MongoDB primary using `openssl s_client` and the Platform CA bundle, reports the verify return code |

The MongoDB CA bundle is copied to the server by the deployer when `platform_mongodb_copy_certs: true`. It is required for Platform to validate the MongoDB server certificate when TLS is enabled.

The handshake test connects to the first host in the `mongodb_primary` group if defined, otherwise the first host in the `mongodb` group, otherwise `localhost`.

### Log Files

Confirms the Platform application log and webserver log files exist and shows their permissions.

### Node.js

Node.js version and executable path.

### Python

Python version, executable path, pip version, and installed module list.

### Connectivity

HTTP and HTTPS health check results (HTTP 200 from `/health/status`) and MongoDB and Redis connectivity status as reported by the health endpoint. MongoDB and Redis connectivity is only evaluated when the health endpoint returns a valid JSON response. When Platform is starting up or unreachable, connectivity shows as unknown rather than causing the certify run to fail.

## Variables

The following variables control where reports are written.

| Variable | Default | Description |
|----------|---------|-------------|
| `redis_certify_report_dir_remote` | `/var/tmp/itential-reports/redis` | Redis report directory on the target host |
| `redis_certify_report_dir_local` | `/tmp/itential-reports/redis` | Redis report directory on the control node |
| `redis_sentinel_certify_report_dir_remote` | `/var/tmp/itential-reports/sentinel` | Sentinel report directory on the target host |
| `redis_sentinel_certify_report_dir_local` | `/tmp/itential-reports/sentinel` | Sentinel report directory on the control node |
| `mongodb_certify_report_dir_remote` | `/var/tmp/itential-reports/mongodb` | MongoDB report directory on the target host |
| `mongodb_certify_report_dir_local` | `/tmp/itential-reports/mongodb` | MongoDB report directory on the control node |
| `platform_certify_report_dir_remote` | `/var/tmp/itential-reports/platform` | Platform report directory on the target host |
| `platform_certify_report_dir_local` | `/tmp/itential-reports/platform` | Platform report directory on the control node |

## TLS Coverage by Component

| Check | Platform | MongoDB | Redis |
|-------|----------|---------|-------|
| TLS enabled in config | Yes | Yes | Yes |
| Cert file exists | Yes | Yes | Yes |
| CA file exists | Yes | Yes | Yes |
| Cert expiry | Yes (full dates + 30-day warning) | Yes (full dates + 30-day warning) | Yes (full dates + 30-day warning) |
| CA expiry | Yes (full dates + 30-day warning) | Yes (full dates + 30-day warning) | Yes (full dates + 30-day warning) |
| Subject / Issuer | Yes | Yes | Yes |
| Subject Alternative Names | Yes | Yes | Yes |
| SAN correlation with inventory | Yes | Yes | Yes |
| Cert-key match | Yes | No (combined PEM) | Yes |
| Chain validation | Yes (when CA bundle present) | Yes (when CA bundle present) | Yes (when CA bundle present) |
| Live TLS handshake | Yes (when CA bundle present) | Yes | Yes |

MongoDB uses a combined PEM file (cert + key concatenated), so cert-key match via public key comparison is not applicable — the cert and key are always co-located in the same file.

## AIO TLS Example

When running certification against an all-in-one deployment with TLS enabled, set `platform_mongo_url` to a hostname or IP address that appears in the MongoDB certificate's Subject Alternative Names. The default `mongodb://localhost:27017` will not match the certificate SANs in most TLS deployments.

```yaml
platform:
  vars:
    platform_mongo_url: mongodb://<MongoServer>:27017/itential
    platform_mongo_tls_enabled: true
    platform_mongodb_copy_certs: true
    platform_mongodb_pki_src_dir: /path/to/certs
```

## HA TLS Example

When running certification against an HA deployment (3-node Redis + Sentinel + MongoDB cluster), use private IP addresses for `platform_mongo_url` and `platform_redis_sentinels` so that Platform connects via the private network. The MongoDB and Redis certs must include those private IPs as Subject Alternative Names.

```yaml
platform:
  vars:
    platform_mongo_url: "mongodb://<MongoSever1>:27017,<MongoSever2>:27017,<MongoSever3>:27017/itential?replicaSet=rs0"
    platform_mongo_tls_enabled: true
    platform_mongodb_copy_certs: true
    platform_mongodb_pki_src_dir: /path/to/certs

    platform_redis_tls_enabled: true
    platform_redis_copy_certs: true
    platform_redis_pki_src_dir: /path/to/certs

    platform_redis_sentinels:
      - host: <RedisSentienelSever1>
        port: 26379
      - host: <RedisSentienelSever3>
        port: 26379
      - host: <RedisSentienelSever3>
        port: 26379
```
