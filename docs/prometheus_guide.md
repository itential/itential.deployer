# Prometheus and Grafana Roles

The playbooks and roles discussed in this section install and configure
[Prometheus](https://prometheus.io/), [Grafana](https://grafana.com/) and a set of metrics
exporters that can be used to help monitor the Itential platform. Prometheus and Grafana can be
installed on separate hosts or can be co-located together. They should not be co-located with the
other Itential-related hosts. The exporters will be installed on the Itential-related hosts where
they are exposing metrics. For example, the MongoDB exporter will be installed on the `mongodb`
hosts.

**&#9432; Note:**
These are optional playbooks and roles and are not required for operation of the Itential platform.

## Setup

In order to run the Prometheus playbooks and roles, the `prometheus.prometheus` collection must be
installed manually. It does not get installed automatically when the `itential.deployer` collection
is installed. Also, this playbook requires prometheus version >= 0.22.0.

```bash
ansible-galaxy collection install prometheus.prometheus
```

If you see the following error when running the Prometheus-related playbooks:

```bash
objc[58735]: +[__NSCFConstantString initialize] may have been in progress in another thread when fork() was called.
objc[58735]: +[__NSCFConstantString initialize] may have been in progress in another thread when fork() was called. We cannot safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
ERROR! A worker was found in a dead state
```

Set this environment variable:

```bash
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

## Roles

There are currently two `itential.deployer` and several `prometheus.prometheus` roles responsible
for installing all of the necessary components.

## Deployer Roles

### Prometheus Install Role

The `itential.deployer.prometheus` role performs a base installation of
[Prometheus](https://prometheus.io/) by calling the `prometheus.prometheus.prometheus` role. It
then configures the Prometheus scrape targets dynamically based on the Itential-related hosts in
the inventory. By default, the scrape targets will use the `inventory_hostname` of the host and the
exporter default web listen port.  Optionally, the scrape targets can be specified using the
`<exporter>_web_listen_address` in the inventory.

### Grafana Install Role

The `itential.deployer.grafana` role performs a base installation of
[Grafana](https://grafana.com/). The Grafana installation will include some basic dashboards that
can immediately provide monitoring value of your Itential installation.

## Prometheus Roles

The Prometheus and Exporter roles in this section are part of the
[Ansible Prometheus Collection](https://galaxy.ansible.com/ui/repo/published/prometheus/prometheus/).

### Prometheus Role

The `itential.deployer` uses the community Prometheus role. Refer to the [`prometheus.prometheus.prometheus`](https://prometheus-community.github.io/ansible/branch/main/prometheus_role.html#ansible-collections-prometheus-prometheus-prometheus-role) documentation for all available configuration parameters.

### Exporter Roles

The `itential.deployer` uses the following community Prometheus exporter roles (refer to the linked documentation for all available configuration parameters):

- [`prometheus.prometheus.redis_exporter`](https://prometheus-community.github.io/ansible/branch/main/redis_exporter_role.html#ansible-collections-prometheus-prometheus-redis-exporter-role)
- [`prometheus.prometheus.mongodb_exporter`](https://prometheus-community.github.io/ansible/branch/main/mongodb_exporter_role.html#ansible-collections-prometheus-prometheus-mongodb-exporter-role)
- [`prometheus.prometheus.node_exporter`](https://prometheus-community.github.io/ansible/branch/main/node_exporter_role.html#ansible-collections-prometheus-prometheus-node-exporter-role)
- [`prometheus.prometheus.process_exporter`](https://prometheus-community.github.io/ansible/branch/main/process_exporter_role.html#ansible-collections-prometheus-prometheus-process-exporter-role)

Each exporter is a lightweight Go application that exposes the metrics on a standard HTTP endpoint. Each exporter requires a port to be opened so that Prometheus can access the metrics that are being exposed by the exporter. The following ports will be utilized by these roles:

| Exporter | Default Port | Description |
| -------- | ------------ | ----------- |
| [node exporter](https://github.com/prometheus/node_exporter) | 9100 | The node exporter is installed on all Itential-related hosts and will expose system and sysadmin type metrics. |
| [process exporter](https://github.com/ncabatoff/process-exporter) | 9256 | The process exporter is installed on `platform` and `gateway` hosts and will expose individual processes from Itential Platform and IAG. |
| [mongodb exporter](https://github.com/percona/mongodb_exporter) | 9216 | The mongo exporter is installed on `mongodb` hosts and will expose information about the MongoDB installation and any replica sets. |
| [redis exporter](https://github.com/oliver006/redis_exporter) | 9121 | The redis exporter is installed on `redis` hosts and will expose information about the Redis installation and any replica sets. |

#### Process Exporter Notes

The process exporter role by default will monitor all processes on the host. To monitor only
Itential-related processes, add the `process_exporter_names` to the groups vars in the inventory.
Refer to the [Example Inventory](#example-inventory) section.

## Variables

### Global Variables

There are no global variables.

### Prometheus Role Variables

All Prometheus variables are handled by the `prometheus.prometheus.prometheus` role.  Refer to the
[Prometheus Role](#prometheus-role) section.

### Exporters Role Variables

All exporter variables are handled by the exporter roles. Refer to the documentation links in the
[Exporter Roles](#exporter-roles) section.

### MongoDB Exporter Recommendations

We recommend setting the `mongodb_exporter_global_conn_pool` variable to `true` in the `mongodb`
group variables section when MongoDB replication is enabled.  Otherwise the exporter may consume
all available file descriptors and cause the mongod process to crash.

```yaml
all:
  children:
    mongodb:
      hosts:
        <MONGODB-HOST-1>:
        <MONGODB-HOST-N>:
    vars:
      mongodb_replication_enabled: true
      mongodb_exporter_global_conn_pool: true
```

### Grafana Role Variables

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `grafana_user` | String | The Grafana linux user. | `grafana` |
| `grafana_group` | String | The Grafana linux group. | `grafana` |
| `grafana_port` | Integer | The Grafana port that is used by the application. | `3000` |
| `grafana_repo_url` | String | The public URL where the grafana application can be downloaded from. | `https://rpm.grafana.com` |
| `grafana_gpg_key` | String | The public URL where the grafana gpg key can be downloaded from. | `https://rpm.grafana.com/gpg.key` |
| `grafana_install_dir` | String | The root installation directory where grafana will be installed. | `/etc/grafana` |
| `grafana_dashboard_dir` | String | The directory path where the dashboards are uploaded to. | `/etc/grafana/provisioning/dashboards` |
| `grafana_allow_ui_updates` | Boolean | A flag to enable/disable saving dashboards in the grafana UI. | `false` |

## Building Your Inventory

To install and configure Prometheus and Grafana, add `prometheus` and `grafana` groups and hosts to
your inventory (in addition to the other Itential-related groups and hosts).

### Example Inventory

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    redis:
      hosts:
        <REDIS-HOST-1>:
        <REDIS_HOST-N>:
      vars:
        redis_exporter_password: <REDIS-PROMETHEUS-PASSWORD>

    mongodb:
      hosts:
        <MONGODB-HOST-1>:
        <MONGODB-HOST-N>:
      vars:
        mongodb_exporter_admin_password: <MONGODB-ADMIN-PASSWORD>

    platform:
      hosts:
        <PLATFORM-HOST-1>:
        <PLATFORM-HOST-N>:
      vars:
        platform_encryption_key: <openssl rand -hex 32> # 64-length hex string, representing a 256-bit AES  encryption key.
        process_exporter_names: |
          {% raw %}
            - cmdline:
                - Pronghorn
            - cmdline:
                - python3
          {% endraw %}

    gateway:
      hosts:
        <GATEWAY-HOST-1>:
        <GATEWAY-HOST-N>:
      vars:
        process_exporter_names: |
          {% raw %}
            - cmdline:
                - python3.9
          {% endraw %}

    prometheus:
      hosts:
        <PROMETHEUS-HOST>:

    grafana:
      hosts:
        <GRAFANA-HOST>:
```

## Running the Playbooks

To execute the installation of Prometheus, Grafana and all the exporters, run the `prometheus_site` playbook:

```bash
ansible-playbook itential.deployer.prometheus_site -i <inventory>
```

To install Prometheus only, run the `prometheus` playbook:

```bash
ansible-playbook itential.deployer.prometheus -i <inventory>
```

To install Grafana only, run the `grafana` playbook:

```bash
ansible-playbook itential.deployer.grafana -i <inventory>
```

To install the exports, run the `prometheus_exporters` playbook:

```bash
ansible-playbook itential.deployer.prometheus_exports -i <inventory>
```

You can also selectively execute portions of the role by using the following tags:

| Tag  | Description |
| ---- | ----------- |
| `prometheus_install` | This will execute the tasks to install Prometheus. |
| `itential_scrape_config_install` | This will execute the task to create the Itential scrape config file. |
| `node_exporter_install`  | This will execute the tasks to install the node exporter. The node exporter is installed on all Itential-related hosts and will expose system and sysadmin type metrics. |
| `process_exporter_install` | This will execute the tasks to install the process exporter. The process exporter is installed on `platform` and `gateway` hosts. |
| `mongodb_exporter_install` | This will execute the tasks to install the mongo exporter. The mongo exporter is installed on `mongodb` hosts. |
| `redis_exporter_install` | This will execute the tasks to install the redis exporter. The redis exporter is installed on `redis` hosts. |
| `grafana_install` | This will execute the tasks to install Grafana. |
