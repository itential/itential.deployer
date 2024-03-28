# Overview

The playbook and roles in this section install and configure RabbitMQ for the Itential Automation Platform.  There are currently three RabbitMQ-related roles:

* `rabbitmq` – Installs RabbitMQ and performs a base configuration.
* `rabbitmq_cluster` – Configures RabbitMQ clustering.
* `rabbitmq_ssl` – Configures RabbitMQ SSL.

# Roles

## RabbitMQ Role

The `rabbitmq` role performs a base install of RabbitMQ including any OS packages required. It installs the appropriate version Erlang.  It creates the appropriate Linux users, directories, log files, and systemd services. It will create the required RabbitMQ users with a default password (see table). It will start the rabbitmq-server service when complete.

| User Name | Default Password | Description
| :-------- | :--------------- | :----------
| admin | admin | The admin user with root permissions in this RabbitMQ install.
| itential | itential | The itential user used by IAP to connect.

:::(Warning) (⚠ Warning: ) It is assumed that these default passwords will be changed to meet more rigorous standards. These are intended to be defaults strictly used just for ease of the installation.  It is highly recommended that sensitive data be encrypted using Ansible Vault.

## RabbitMQ Cluster

The `rabbitmq_cluster` role performs the steps to run RabbitMQ as a cluster of nodes.  It assumes a cluster of 3 and that the first host defined in the inventory will be used as the primary. It will modify the RabbitMQ config file to enable the cluster. It will write the hostname to each RabbitMQ node’s host file (RabbitMQ clustering requires DNS resolution). It creates the required Erlang cookie used by the RabbitMQ nodes to join a cluster. It invokes each RabbitMQ node to join the cluster. It enables queue mirroring. It will restart the rabbitmq-server service when complete.

More info on rabbit cluster: https://www.rabbitmq.com/clustering.html 

## RabbitMQ SSL Role

The `rabbitmq_ssl` performs the steps to require TLS when communicating with the RabbitMQ server. It uploads the certificates to the correct location. It is NOT responsible for making the certificates. It will make a number of edits to the RabbitMQ config to enable TLS. It will restart the rabbitmq-server service when complete.

More info on rabbit TLS: https://www.rabbitmq.com/ssl.html 

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

The following table lists the default variables that are shared between the RabbitMQ-related roles, located in `roles/common_vars/defaults/main/rabbitmq.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `rabbitmq_vhost` | `all` | String | The name of the RabbitmMQ vhost. | `iap`
| `rabbitmq_ssl` | `all` | Boolean | Flag to enable SSL. <br>`true` - enable HTTPS when connecting to rabbit, disable HTTP. <br>`false` - disable HTTPS when connecting to rabbit, enable HTTP. | `false`

## RabbitMQ Role Variables

The variables in this section may be overridden in the inventory in the `rabbmitmq` group vars.

The following table lists the default variables located in `roles/rabbitmq/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `rabbitmq_config` | `rabbitmq` | String | The location of the RabbitMQ configuration file. | `/etc/rabbitmq/rabbitmq.conf`
| `rabbitmq_port` | `rabbitmq` | Integer | The default listen port. | `5672`
| `rabbitmq_mgt_console_port` | `rabbitmq` | Integer | The default management console listen port. | `15672`
| `rabbitmq_owner` | `rabbitmq` | String | The RabbitMQ Linux user. | `rabbitmq`
| `rabbitmq_group` | `rabbitmq` | String | The RabbitMQ Linux group. | `rabbitmq`
| `rabbitmq_bind_ipv6` | `rabbitmq` | Boolean | Flag to enable binding to IPv6. | `true`
| `rabbitmq_bind_addr` | `rabbitmq` | String | The hostnames/IP addresses on which RabbitMQ will listen for client connections. | `127.0.0.1`
| `rabbitmq_user` | `rabbitmq` | String | The user used by IAP to connect to RabbitMQ. | `itential`
| `rabbitmq_password` | `rabbitmq` | String | The default password for the RabbitMQ user. | `itential`
| `rabbitmq_admin_user` | `rabbitmq` | String | The admin user with root permissions in this RabbitMQ install. | `admin`
| `rabbitmq_admin_password` | `rabbitmq` | String | The default password for the admin user. | `admin`

:::(Warning) (⚠ Warning: ) It is assumed that these default passwords will be changed to meet more rigorous standards. These are intended to be defaults strictly used just for ease of the installation.  It is highly recommended that sensitive data be encrypted using Ansible Vault.

## RabbitMQ Cluster Role Variables

The variables in this section may be overridden in the inventory in the `rabbmitmq` group vars.

The following table lists the default variables located in `roles/rabbitmq_cluster/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `rabbitmq_cluster` | `rabbitmq` | Boolean | Flag to enable clustering. | `false`
| `rabbitmq_erlang_cookie` | `rabbitmq` | String | The location of the Erlang cookie file. | `/var/lib/rabbitmq/.erlang.cookie`
| `rabbitmq_cluster_port` | `rabbitmq` | Integer | The default RabbitMQ cluster listen port. | `25672`
| `rabbitmq_epmd_port` | `rabbitmq` | Integer | The default RabbitMQ Erlang Port Mapping Daemon listen port. | `4369`

## RabbitMQ SSL Role Variables

The variables in this section may be overridden in the inventory in the `rabbmitmq` group vars.

The following table lists the default variables located in `roles/rabbitmq_ssl/defaults/main.yml`.

| Variable | Group | Type | Description | Default Value
| :------- | :---- | :--- | :---------- | :------------
| `rabbitmq_ssl_dir` | `rabbitmq` | String | The directory containing the SSL certificates and keys. | `/etc/rabbitmq/ssl`
| `rabbitmq_ssl_port` | `rabbitmq` | Integer| The RabbitMQ SSL listen port. | `5671`

# Configuring SSL

The `rabbit_ssl` roles does not generate SSL certificates.  They must be generated by the user and placed in the `rabbitmq/files` directory on the Ansible control node.

The following table shows the source and destination locations for the files.

| File | Source Location | Destination Location
| :--- | :-------------- | :-------------------
| Server Cert | `{{ role_path }}/files/server_certificate.pem` | `{{ rabbitmq_ssl_dir }}/serverCert.pem`
| Server Key | `{{ role_path }}/files/server_key.pem` | `{{ rabbitmq_ssl_dir }}/serverKey.pem`
| CA Cert | `{{ role_path }}/files/ca_certificate.pem` | `{{ rabbitmq_ssl_dir }}/ca_certificate.pem`

# Building the Inventory

To install and configure RabbitMQ, add a `rabbitmq` group and host to your inventory.  The following inventory shows a basic RabbitMQ configuration with a single RabbitMQ node with no SSL.

## Example Inventory - Single RabbitMQ Node, No Clustering or SSL

```
all:
    vars:
        iap_release: 2023.1

    children:
        rabbitmq:
            hosts:
                <host1>:
                    ansible_host: <addr1>
```

To enable clustering, add two additional nodes to the `rabbitmq` group and add the `rabbitmq_cluster` flag to the `rabbitmq` group vars and set it to `true`.

## Example Inventory - Configure RabbitMQ Cluster

```
all:
    vars:
        iap_release: 2023.1

    children:
        rabbitmq:
            hosts:
                <host1>:
                    ansible_host: <addr1>
                <host2>:
                    ansible_host: <addr2>
                <host3>:
                    ansible_host: <addr3>
            vars:
                rabbitmq_cluster: true
```

To configure a RabbitMQ SSL, add the `rabbitmq_ssl` flag to the `all` group vars and set it to `true`.

## Example Inventory - Configure RabbitMQ SSL

```
all:
    vars:
        iap_release: 2023.1
        rabbitmq_ssl: true

    children:
        rabbitmq:
            hosts:
                <host1>:
                    ansible_host: <addr1>
                <host2>:
                    ansible_host: <addr2>
                <host3>:
                    ansible_host: <addr3>
            vars:
                rabbitmq_cluster: true
```

# Running the Playbook

To execute all RabbitMQ roles, run the `rabbitmq.yml` playbook:

```
ansible-playbook rabbitmq.yml -i <inventory>
```

You can also run select RabbitMQ roles by using the following tags:

* `rabbitmq_install`
* `rabbitmq_cluster`
* `rabbitmq_ssl`

To execute only the `rabbitmq` role (skipping the RabbitMQ Cluster and RabbitMQ SSL roles), run the `itential.deployer.rabbitmq` playbook with the `rabbitmq_install` tag:

```
ansible-playbook itential.deployer.rabbitmq -i <inventory> --tags rabbitmq_install
```

To execute only the RabbitMQ Cluster role (skipping the RabbitMQ and RabbitMQ SSL roles), run the `itential.deployer.rabbitmq` playbook with the `rabbitmq_cluster` tag:

```
ansible-playbook itential.deployer.rabbitmq -i <inventory> --tags rabbitmq_cluster
```

To execute only the RabbitMQ SSL role (skipping the RabbitMQ and RabbitMQ Cluster roles), run the `itential.deployer.rabbitmq` playbook with the `rabbitmq_ssl` tag:

```
ansible-playbook itential.deployer.rabbitmq -i <inventory> --tags rabbitmq_ssl
```