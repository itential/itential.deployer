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

- **Remote host:** `{{ platform_certify_report_dir_remote }}/<hostname>.md` (default: `/var/tmp/itential-reports/platform/`)
- **Control node:** `{{ platform_certify_report_dir_local }}/<hostname>.md` (default: `/tmp/itential-reports/platform/`)

## Platform Certification Report

The Platform report covers the following sections.

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

HTTP and HTTPS health check results (HTTP 200 from `/health/status`) and MongoDB and Redis connectivity status as reported by the health endpoint.

## Variables

The following variables control where reports are written.

| Variable | Default | Description |
|----------|---------|-------------|
| `platform_certify_report_dir_remote` | `/var/tmp/itential-reports/platform` | Report directory on the target host |
| `platform_certify_report_dir_local` | `/tmp/itential-reports/platform` | Report directory on the control node |

## AIO TLS Example

When running certification against an all-in-one deployment with TLS enabled, set `platform_mongo_url` to a hostname or IP address that appears in the MongoDB certificate's Subject Alternative Names. The default `mongodb://localhost:27017` will not match the certificate SANs in most TLS deployments.

```yaml
platform:
  vars:
    platform_mongo_url: mongodb://ip-10-0-0-10.ec2.internal:27017/itential
    platform_mongo_tls_enabled: true
    platform_mongodb_copy_certs: true
    platform_mongodb_pki_src_dir: /path/to/certs
```
