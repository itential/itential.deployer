# Certificate Deployment Scenarios - Configuration Guide

## Overview

The deployer supports 3 certificate deployment scenarios by configuring filename variables in your inventory.

| Scenario | Use Case | Certificates Needed |
|----------|----------|---------------------|
| **Scenario 1** | Per-host certificates (most secure) | One unique cert per server |
| **Scenario 2** | Per-role certificates (simplified management) | One cert shared per role |
| **Scenario 3** | Single multi-domain certificate (simplest) | One cert for everything |

---

## Scenario 1: Per-Host Certificates (Current - Most Secure)

**Certificate Structure:**
```
certificates/
  mongodb/
    mongo_host1.ec2.internal.pem
    mongo_host2.ec2.internal.pem
    mongo_host3.ec2.internal.pem
    ca-bundle.crt
  platform/
    platform_host1.ec2.internal.crt
    platform_host1.ec2.internal.key
    platform_host2.ec2.internal.crt
    platform_host2.ec2.internal.key
    ca-bundle.crt
  ...
```

**Inventory Configuration:**
```yaml
# MongoDB
mongodb:
  vars:
    mongodb_pki_src_dir: "<path/to/local/certs>/certificates/mongodb"
    # Default: mongodb_tls_server_cert_filename: "{{ inventory_hostname }}.pem"
    # No override needed - this is the default

# Platform
platform:
  vars:
    platform_https_pki_src_dir: "<path/to/local/certs>/certificates/platform"
    # Default: platform_https_cert_filename: "{{ inventory_hostname }}.crt"
    # Default: platform_https_key_filename: "{{ inventory_hostname }}.key"
    # No override needed

# Redis
redis:
  vars:
    redis_pki_src_dir: "<path/to/local/certs>/certificates/redis"
    # Default: redis_tls_cert_filename: "{{ inventory_hostname }}.crt"
    # Default: redis_tls_key_filename: "{{ inventory_hostname }}.key"
    # No override needed

# Gateway
gateway:
  vars:
    gateway_pki_src_dir: "<path/to/local/certs>/certificates/gateway"
    # Default: gateway_https_cert_filename: "{{ inventory_hostname }}.crt"
    # Default: gateway_https_key_filename: "{{ inventory_hostname }}.key"
    # No override needed
```

**Pros:**
- ✅ Most secure (compromise of one server doesn't affect others)
- ✅ Easy to rotate individual server certificates
- ✅ Clear audit trail (which cert on which server)

**Cons:**
- ❌ More certificates to manage
- ❌ More certificate generation overhead

---

## Scenario 2: Per-Role Certificates (Simplified Management)

**Certificate Structure:**
```
certificates/
  mongodb/
    mongodb.pem          (shared by all MongoDB servers)
    ca-bundle.crt
    replica.key
  platform/
    platform.crt         (shared by all Platform servers)
    platform.key
    client.pem
    mongodb-client.key
    ca-bundle.crt
  redis/
    redis.crt            (shared by all Redis servers)
    redis.key
    ca-bundle.crt
  gateway/
    gateway.crt          (shared by all Gateway servers)
    gateway.key
    ca-bundle.crt
```

**Inventory Configuration:**
```yaml
# MongoDB - All servers use mongodb.pem
mongodb:
  vars:
    mongodb_pki_src_dir: "<path/to/local/certs>/certificates/mongodb"
    mongodb_tls_server_cert_filename: "mongodb.pem"

# Platform - All servers use platform.crt/key
platform:
  vars:
    platform_https_pki_src_dir: "<path/to/local/certs>/certificates/platform"
    platform_https_cert_filename: "platform.crt"
    platform_https_key_filename: "platform.key"

# Redis - All servers use redis.crt/key
redis:
  vars:
    redis_pki_src_dir: "<path/to/local/certs>/certificates/redis"
    redis_tls_cert_filename: "redis.crt"
    redis_tls_key_filename: "redis.key"

# Gateway - All servers use gateway.crt/key
gateway:
  vars:
    gateway_pki_src_dir: "<path/to/local/certs>/certificates/gateway"
    gateway_https_cert_filename: "gateway.crt"
    gateway_https_key_filename: "gateway.key"
```

**Certificate Requirements:**
- Subject Alternative Names (SANs) must include all server hostnames/IPs for each role
- Example MongoDB cert SANs: `DNS:mongo_host1.ec2.internal, DNS:mongo_host2.ec2.internal, DNS:mongo_host3.ec2.internal`

**Pros:**
- ✅ Fewer certificates to manage
- ✅ Simpler certificate generation (one per role)
- ✅ Easy to deploy new servers (just copy same cert)

**Cons:**
- ❌ Certificate compromise affects all servers in that role
- ❌ Certificate rotation requires updating all servers
- ❌ Larger certificate files (many SANs)

---

## Scenario 3: Single Multi-Domain Certificate (Simplest)

**Certificate Structure:**
```
certificates/
  shared.crt             (one cert for all servers)
  shared.key
  ca-bundle.crt
```

**Inventory Configuration:**
```yaml
# MongoDB
mongodb:
  vars:
    mongodb_pki_src_dir: "<path/to/local/certs>/certificates"
    mongodb_tls_server_cert_filename: "shared.pem"

# Platform
platform:
  vars:
    platform_https_pki_src_dir: "<path/to/local/certs>/certificates"
    platform_mongodb_pki_src_dir: "<path/to/local/certs>/certificates"
    platform_https_cert_filename: "shared.crt"
    platform_https_key_filename: "shared.key"

# Redis
redis:
  vars:
    redis_pki_src_dir: "<path/to/local/certs>/certificates"
    redis_tls_cert_filename: "shared.crt"
    redis_tls_key_filename: "shared.key"

# Gateway
gateway:
  vars:
    gateway_pki_src_dir: "<path/to/local/certs>/certificates"
    gateway_https_cert_filename: "shared.crt"
    gateway_https_key_filename: "shared.key"
```

**Certificate Requirements:**
- Multi-domain certificate with SANs listing all hostnames and IPs across all servers and roles:

```
Subject Alternative Names:
  DNS:mongo_host1.ec2.internal
  DNS:mongo_host2.ec2.internal
  DNS:platform_host1.ec2.internal
  DNS:platform_host2.ec2.internal
  DNS:redis_host1.ec2.internal
  DNS:gateway_host1.ec2.internal
  IP:10.1.1.10
  IP:10.1.1.11
  ...
```

**Generation Example:**
```bash
openssl req -new -x509 -days 365 -key shared.key -out shared.crt \
  -subj "/CN=itential-infrastructure" \
  -addext "subjectAltName=DNS:mongo_host1.ec2.internal,DNS:mongo_host2.ec2.internal,DNS:platform_host1.ec2.internal,IP:10.1.1.10,IP:10.1.1.11"
```

**Note for MongoDB:**
- Need to create `.pem` file (combined cert+key):
  ```bash
  cat shared.crt shared.key > shared.pem
  chmod 600 shared.pem
  ```

**Pros:**
- ✅ Simplest to manage (one certificate)
- ✅ Easy to deploy anywhere
- ✅ Fast certificate rotation (update once, deploy everywhere)

**Cons:**
- ❌ Least secure (compromise affects everything)
- ❌ Single point of failure
- ❌ Large SAN list if many servers
- ❌ Must regenerate certificate when adding new servers

---

## Comparison Matrix

| Feature | Scenario 1<br>(Per-Host) | Scenario 2<br>(Per-Role) | Scenario 3<br>(Multi-Domain) |
|---------|--------------------------|--------------------------|------------------------------|
| **Certificates to manage** | High | Medium | Low (1) |
| **Security level** | Highest | Medium | Lowest |
| **Certificate generation** | Complex | Moderate | Simple |
| **Rotation complexity** | Low (per server) | Medium (per role) | High (everything at once) |
| **New server deployment** | Need new cert | Copy role cert | Regenerate cert with new SANs |
| **SAN requirements** | Single hostname | Multiple hostnames | All hostnames across all roles |
| **Blast radius if compromised** | One server | One role | Everything |

---

## Migration Between Scenarios

### From Scenario 1 → Scenario 2

**Step 1:** Generate role-level multi-domain certificates with SANs
```bash
# Example: MongoDB cert with all MongoDB server SANs
openssl req -new -x509 -days 365 -key mongodb.key -out mongodb.crt \
  -subj "/CN=mongodb" \
  -addext "subjectAltName=DNS:mongo_host1.ec2.internal,DNS:mongo_host2.ec2.internal,DNS:mongo_host3.ec2.internal"

cat mongodb.key mongodb.crt > mongodb.pem
```

**Step 2:** Update inventory to use role filenames
```yaml
mongodb:
  vars:
    mongodb_tls_server_cert_filename: "mongodb.pem"  # Changed
```

**Step 3:** Update certificates directory structure
```bash
# Old structure: certificates/mongodb/mongo_host1.ec2.internal.pem
# New structure: certificates/mongodb/mongodb.pem
```

### From Scenario 2 → Scenario 3

**Step 1:** Generate multi-domain certificate covering all servers across all roles
```bash
openssl req -new -x509 -days 365 -key shared.key -out shared.crt \
  -subj "/CN=itential-infrastructure" \
  -addext "subjectAltName=DNS:mongo_host1.ec2.internal,DNS:mongo_host2.ec2.internal,DNS:platform_host1.ec2.internal,DNS:platform_host2.ec2.internal,..."

cat shared.crt shared.key > shared.pem
```

**Step 2:** Update inventory to use multi-domain filenames
```yaml
mongodb:
  vars:
    mongodb_pki_src_dir: "<path/to/local/certs>/certificates"  # Single directory
    mongodb_tls_server_cert_filename: "shared.pem"

platform:
  vars:
    platform_https_pki_src_dir: "<path/to/local/certs>/certificates"
    platform_https_cert_filename: "shared.crt"
    platform_https_key_filename: "shared.key"

redis:
  vars:
    redis_pki_src_dir: "<path/to/local/certs>/certificates"
    redis_tls_cert_filename: "shared.crt"
    redis_tls_key_filename: "shared.key"

gateway:
  vars:
    gateway_pki_src_dir: "<path/to/local/certs>/certificates"
    gateway_https_cert_filename: "shared.crt"
    gateway_https_key_filename: "shared.key"
```

---

## Quick Reference - Variable Override Locations

All filename variables can be overridden in your inventory:

**MongoDB:**
- `mongodb_tls_server_cert_filename`
- `mongodb_tls_ca_cert_filename`
- `mongodb_replica_keyfile_filename`

**Platform:**
- `platform_https_cert_filename`
- `platform_https_key_filename`
- `platform_https_ca_filename`
- `platform_mongodb_ca_filename`
- `platform_mongodb_client_cert_filename`
- `platform_mongodb_client_key_filename`

**Redis:**
- `redis_tls_cert_filename`
- `redis_tls_key_filename`
- `redis_tls_ca_cert_filename`

**Gateway:**
- `gateway_https_cert_filename`
- `gateway_https_key_filename`
- `gateway_https_ca_filename`

---

## Example: Mixed Scenario (Advanced)

You can even mix scenarios per role:

```yaml
# MongoDB: Per-host (most critical)
mongodb:
  vars:
    mongodb_tls_server_cert_filename: "{{ inventory_hostname }}.pem"

# Platform: Per-host (user-facing)
platform:
  vars:
    platform_https_cert_filename: "{{ inventory_hostname }}.crt"
    platform_https_key_filename: "{{ inventory_hostname }}.key"

# Redis: Per-role (internal, less critical)
redis:
  vars:
    redis_tls_cert_filename: "redis.crt"
    redis_tls_key_filename: "redis.key"

# Gateway: Per-role (behind load balancer)
gateway:
  vars:
    gateway_https_cert_filename: "gateway.crt"
    gateway_https_key_filename: "gateway.key"
```

---

## Key Takeaway

**The deployer is flexible!** You don't need code changes - just configure the filename variables in your inventory to match your certificate structure. The `{{ inventory_hostname }}` default supports Scenario 1, but you can override it for Scenarios 2 and 3.

**Multi-Domain Certificates:** In Scenarios 2 and 3, certificates use Subject Alternative Names (SANs) to list multiple hostnames, allowing one certificate to be used across multiple servers.