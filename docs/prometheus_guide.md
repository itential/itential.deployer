# Overview
The playbook and roles discussed in this section can install and configure [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/) as well as a set of metrics exporters that can be used to help monitor the Itential platform. It is an optional role and is not required for operation of the Itential platform.

# Roles
There is currently one role responsible for installing all of the necessary components.

## Prometheus Role
The `Prometheus` role performs a base installation of [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/) and a suite of exporters that expose the metrics from each of the IAP dependencies. It is intended to be run against its own VM and can not be collocated with the other applications. Specifically, Prometheus and Grafana will be installed on a separate VM while each of the exporters must be installed on the VM where they are exposing metrics. For example, to expose MongoDB metrics the MongoDB exporter must be installed on the Mongo VMs.

Each exporter is a lightweight Go application that exposes the metrics on a standard HTTP endpoint. Each exporter requires a port to be opened so that Prometheus can access the metrics that are being exposed by the exporter. The following ports will be utilised by this role:

| Exporter         | Port | Description                                                                                                                       |
| ---------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------- |
| [node exporter](https://github.com/prometheus/node_exporter)    | 9100 | The node exporter is installed on ALL VMs and will expose system and sysadmin type metrics.                                       |
| [process exporter](https://github.com/ncabatoff/process-exporter) | 9256 | The process exporter is installed on `platform` VMs and will expose individual processes from IAP.                                |
| [mongo exporter](https://github.com/percona/mongodb_exporter) | 9216 | The mongo exporter is installed on `mongodb` VMs and will expose information about the MongoDB installation and any replica sets. |
| [redis exporter](https://github.com/oliver006/redis_exporter)  | 9121 | The redis exporter is installed on `redis` VMs and will expose information about the Redis installation and any replica sets.     |
| rabbitmq exporter | 15692 | RabbitMQ ships with its own exporter. It just needs to be enabled which this role will do. |
| IAP exporter | 3000 | IAP ships with its own exporter already enabled. IAP metrics are exposed at `/prometheus_metrics`. Nothing needs to be done. |

The Grafana installation will include some basic dashboards that can immediately provide monitoring value of your Itential installation.

# Variables

## Global Variables
This role has no global variables. They must all be set with the `prometheus` device group.

## Prometheus Role Variables

| Variable | Group | Type | Description | Default Value | Required?
| :------- | :---- | :--- | :---------- | :------------ | :--------
| `prometheus_user` | `prometheus` | string | The prometheus linux user. | `prometheus` | No |
| `prometheus_group` | `prometheus` | string | The prometheus linux group. | `prometheus` | No |
| `prometheus_port` | `prometheus` | Integer | The port that the prometheus application is exposed on. | 9090 | No |
| `prometheus_download_url` | `prometheus` | string | The public URL where the prometheus application can be downloaded from. | `https://github.com/prometheus/prometheus/releases/download/v2.53.0/prometheus-2.53.0.linux-amd64.tar.gz` | No |
| `prometheus_dir` | `prometheus` | string | The root installation directory where prometheus will be installed. | `/opt/prometheus` | No |
| `prometheus_db_path` | `prometheus` | string | The directory path where prometheus will store its database. | `/opt/prometheus/data` | No |
| `prometheus_db_retention` | `prometheus` | string | The string representing the amount of time that prometheus will retain its data. 30 days. | `30d` | No |
| `prometheus_scrape_interval` | `prometheus` | string | The string representing the amount of time that transpires between metrics scrapes by prometheus, 15 seconds. | `15s` | No |
| `prometheus_evaluation_interval` | `prometheus` | string | The string representing the amount of time that transpires between evaluations for prometheus to query for alerting, 15 seconds. | `15s` | No |
| `prometheus_node_exporter_download_url` | `prometheus` | string | The public URL where this exporter can be downloaded from. | `https://github.com/prometheus/node_exporter/releases/download/v1.8.1/node_exporter-1.8.1.linux-amd64.tar.gz` | No |
| `prometheus_node_exporter_port` | `prometheus` | Integer | The port that the exporter will use to expose its metrics. | 9100 | No |
| `prometheus_process_exporter_download_url` | `prometheus` | string | The public URL where this exporter can be downloaded from. | `https://github.com/ncabatoff/process-exporter/releases/download/v0.8.2/process-exporter-0.8.2.linux-amd64.tar.gz` | No |
| `prometheus_process_exporter_port` | `prometheus` | Integer | The port that the exporter will use to expose its metrics. | 9256 | No |
| `prometheus_redis_exporter_download_url` | `prometheus` | string | The public URL where this exporter can be downloaded from. | `https://github.com/oliver006/redis_exporter/releases/download/v1.61.0/redis_exporter-v1.61.0.linux-amd64.tar.gz` | No |
| `prometheus_redis_exporter_port` | `prometheus` | Integer | The port that the exporter will use to expose its metrics. | 9121 | No |
| `prometheus_mongo_exporter_download_url` | `prometheus` | string | The public URL where this exporter can be downloaded from. | `https://github.com/percona/mongodb_exporter/releases/download/v0.40.0/mongodb_exporter-0.40.0.linux-amd64.tar.gz` | No |
| `prometheus_mongo_exporter_port` | `prometheus` | Integer | The port that the exporter will use to expose its metrics. | 9216 | No |
| `prometheus_grafana` | `prometheus` | boolean | Instructs the roles to perform the installation of Grafana or not. Must be set to `true` for installation to run. | false | No |
| `prometheus_grafana_user` | `prometheus` | string | The Grafana linux user. | `grafana` | No |
| `prometheus_grafana_group` | `prometheus` | string | The Grafana linux group. | `grafana` | No |
| `prometheus_grafana_port` | `prometheus` | Integer | The Grafana port that is used by the application. | 3000 | No |
| `prometheus_grafana_repo_url` | `prometheus` | string | The public URL where the grafana application can be downloaded from. | `https://rpm.grafana.com` | No |
| `prometheus_grafana_gpg_key` | `prometheus` | string | The public URL where the grafana gpg key can be downloaded from. | `https://rpm.grafana.com/gpg.key` | No |
| `prometheus_grafana_install_dir` | `prometheus` | string | The root installation directory where grafana will be installed. | `/etc/grafana` | No |
| `prometheus_grafana_dashboard_dir` | `prometheus` | string | The directory path where the dashboards are uploaded to. | `/etc/grafana/provisioning/dashboards` | No |
| `prometheus_grafana_allow_ui_updates` | `prometheus` | boolean | A flag to enable/disable saving dashboards in the grafana UI. | false | No |

# Building Your Inventory
To install and configure Prometheus and Grafana, add a `prometheus` group and host to your inventory.
## Example Inventory
```
all:
  vars:
    iap_release: 2023.1

  children:
    prometheus:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        grafana: true
```
# Running the Playbook
To execute the installation of Prometheus and Grafana, run the `prometheus` playbook:
```
ansible-playbook itential.deployer.prometheus -i <inventory>
```
You can also selectively execute portions of the role by using the following tags:
| Tag               | Description                                                                                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| prometheus_server | This will execute the tasks to install the Prometheus Server only.                                                                                    |
| [node_exporter](https://github.com/prometheus/node_exporter)     | This will execute the tasks to install the node exporter. The node exporter is installed on ALL VMs and will expose system and sysadmin type metrics. |
| [process_exporter](https://github.com/ncabatoff/process-exporter)  | This will execute the tasks to install the process exporter. The process exporter is installed on `platform` VMs.                                   |
| [mongo_exporter](https://github.com/percona/mongodb_exporter)    | This will execute the tasks to install the mongo exporter. The mongo exporter is installed on `mongodb` VMs.                                        |
| [redis_exporter](https://github.com/oliver006/redis_exporter)    | This will execute the tasks to install the redis exporter. The redis exporter is installed on `redis` VMs.                                          |
| rabbitmq_metrics  | This will execute the tasks to install the rabbitmq exporter. The process exporter is installed on `rabbitmq` VMs.                                  |
| grafana           | This will execute the tasks to install the Grafana. This only runs against `prometheus` VMs.                                                        |
|                   |                                                                                                                                                       |