# Ansible Collection - itential.deployer
An Itential environment is composed of several applications working in conjunction with one another, including:

- Itential Automation Platform (IAP)
- Itential Automation Gateway (IAG)
- Redis
- RabbitMQ (when using IAP version 23.1 and older)
- MongoDB

In many environments, these applications are installed across multiple systems to improve resiliency and performance. To assist users with such installations, Itential provides the **Itential Deployer**.

The Itential deployer can deploy supported Itential architectures.

## What are the supported architectures?

- All-in-one
- Minimal Architecture
- Highly Available Architecture
- Active/Standby Architecture
- Blue Green Architecture

### All-in-one
The All-In-One architecture is an architecture where all components are installed on the same instance.  This architecture lends itself well to development environments and “throw away” environments like those found in a CI/CD pipeline.  Security considerations are non-existent or use simple default passwords as the emphasis is placed on simplicity.

### Minimal Architecture
A Minimal Architecture is an architecture where all or most components are single instances and can not gracefully tolerate failures. This architecture lends itself well to development environments. It favors the engineer with its simplicity and enables them to do their work with few restrictions. Security considerations should lean towards openness and ease of use but at the same time capture the spirit of the other higher environments. In this architecture, each of the required Itential components is a single instance.  This architecture will exercise the network connectivity between the components and can be advantageous to deploy as a development environment.

The ideal minimal architecture will have 5 VM's with each hosting a single instance of the required components. An acceptable variation is to have 1 VM with everything hosted on it. The number of VM's and what is hosted where is less of a concern with the MA because the intent is simplicity and to enable engineers to build automations and not be a highly-available environment.

Itential recommends applying security principles to ALL environments. In the MA, this would include configuring all components to use authentication. Optionally, we recommend using SSL when communicating with components on other VMs but recognize that this should be enabled at the discretion of the customer.

### Highly Available Architecture
A Highly Available Architecture is an architecture where all or most components are redundant and can gracefully tolerate at least 1 catastrophic failure. This architecture is the recommended architecture for testing environments and simple production environments. The intent is to provide an environment that is as close to production as possible so that testing automations can provide confidence and expose potential problems sooner in the development lifecycle. Security considerations should mimic production requirements. In this architecture, each of the required Itential components is installed in clusters to provide stability, mimic production, and expose any issues with the clustering of the components. This could also serve as a production architecture.

The ideal HA2 environment will have 12 VMs:

- 2 VMs hosting IAP.
- 3 VMs hosting MongoDB configured as a replica set.
- 3 VMs hosting Redis configured as a highly available replica set using Redis Sentinel.
- 3 VMs hosting Rabbitmq configured as a rabbit cluster.
- 1 VM hosting IAG.

Itential recommends applying sound security principles to ALL environments. This would include configuring all components to use authentication within the HA2. Additionally, we recommend using SSL when communicating with components on other VMs and across clusters.

### Active/Standby Architecture
An Active/Standby Architecture (ASA) is an architecture (that is normally used for making HA2 architectures redundant) reserved for production environments where Disaster Recovery is required. It is not required that they be geographically redundant but they could be. The intent is to provide a standby environment that can be used in the event of a disaster on the active stack. The standby stack should be preconfigured to be quickly made into the active stack. Care needs to be taken that the same level of access to 3rd party systems existing in the standby stack matches those in the active stack. Security must be taken into account if this is used as a production environment.

The ideal ASA architecture will appear as two HA2 stacks except for MongoDB. One or more of the MongoDB instances must be hosted in the standby location as a replica of the primary. Ideally, the MongoDB cluster will consist of 5 members: 4 data-bearing members and a MongoDB arbiter. This will allow for a cluster of three mongos in the worst-case disaster scenario.

Itential recommends applying sound security principles to ALL environments. In the ASA, this would include configuring all components to use authentication and use SSL when communicating with components on other VMs and across clusters.

<!-- ### Blue/Green Architecture
This architecture requires two separate and complete Itential stacks. There is no constraint from a datacenter boundary, these stacks can exist in separate or the same datacenter. Control of the active environment is driven by the GTM load balancer. No configurations are shared between the stacks. No components are shared between the stacks. Any changes made to one will have zero impact on the other. The databases will need to be kept in sync so that when the inactive is made active it will have all the data. Switching from the active to inactive will require all users to login again.

This architecture is intended to reduce downtime as much as possible. It has the advantage of being two independent Itentials. Deployments and upgrades can be staged in advance during normal business hours against the inactive stack without impacting the active environment. Changes made on the blue stack will never effect the green. This includes code running adapters and applications, database documents such as workflows, and configurations. The actual deployment is when the load balancer is switched to the other stack. In flight jobs on the old stack will continue to run until they are complete. New jobs will start on the new stack using the new code, data models, and configurations.

The caveat to this architecture is that your job history is not immediately available after performing a switch. It is important to know which color ran the job as that is the stack that will have the job history. The stack that runs a job is where the history of that job will exist unless effort is made to reconcile the historical data. -->

## Deployer Prerequisites
The Itential Deployer is an ansible project and as such requires running on a control node. That node has its own set of dependencies.

### Required Python, Ansible, and Ansible modules
- **Itential Galaxy Access**: The Itential Deployer is hosted on the Itential Galaxy repository. An account is required to access Itential Galaxy. If you do not have an account, contact your Itential Professional Services representative.
- **Python Version**: The control node must be running Python 3.9 or later.
- **Ansible Version**: The control node must be running Ansible version 2.11 or later. To see which Ansible version is currently installed, execute the `ansible --version` command as shown below.

_Example: Confirming Ansible Version_

```bash
$ ansible --version
  ansible [core 2.12.2]
  config file = None
  configured module search path = ['/var/home/yourname/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/lib/python3.9/site-packages/ansible
  ansible collection location = /var/home/yourname/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/local/bin/ansible
  python version = 3.9.9 (main, Nov 19 2021, 00:00:00) [GCC 11.2.1 20210728 (Red Hat 11.2.1-1)]
  jinja version = 3.0.3
  libyaml = True
```
- **Required Ansible Modules**: The following ansible modules are required on the control node for the deployer to run.
  - 'ansible.posix': '>=0.0.1'
  - 'community.mongodb': '>=0.0.1'

**&#9432; Note:**
The Itential Deployer is an Ansible collection. As such, a familiarity with basic Ansible concepts is suggested before proceeding.

### Required public repos

### Ports & Networking
  In a clustered environment where components are installed on more than one host, the following network traffic flows need to be allowed.
| Source | Destination | Port | Description |
|---|---|---|---|
| IAP | MongoDB | 27017 | IAP connects to MongoDB |
| IAP | RabbitMQ | 5672/5671 | IAP connects to Rabbitmq for interprocess communication. 5671 is used for SSL if enabled. |
| IAP | Redis | 6379 | IAP connects to Redis for session tokens |
| IAP | Redis | 26379 | IAP connects to Redis Sentinel in a HA Redis set up |
| MongoDB | MongoDB | 27017 | Each MongoDB talks to the other MongoDBs for replication of the database |
| RabbitMQ | RabbitMQ | 5672/5671 | Each Rabbit talks to the other Rabbits for HA resiliency. 5671 is used for SSL if enabled. |
| RabbitMQ | RabbitMQ | 25672 | Each Rabbit talks to the other Rabbits to form a cluster |
| RabbitMQ | RabbitMQ | 4369 | epmd (Erlang Port Mapping Daemon) is a small additional daemon that runs alongside every RabbitMQ node and is used to discover what port a particular node listens on for inter-node communication |
| Redis | Redis | 6379 | Each Redis talks to the other Redis’s for replication |
| Redis | Redis | 26379 | Each Redis uses Redis Sentinel to monitor the Redis processes for HA resiliency |

### Certificates
The itential deployer is not responsible for creating any SSL certificates that may be used to further tighten security in the Itential ecosystem. However, if these certificates are provided it can upload and configure the platform to use them. The table below describes the certificates that can be used and what their purpose is.

| Certificate | Description |
|---|---|
| IAP webserver | Enables HTTPS communications with the IAP webserver. |
| IAG webserver | Enables HTTPS communications with the IAG webserver. |
| MongoDB | Enables secure communications with the MongoDB server. Also used for intra-node mongo replication. |
| Redis | Enables secure communications with the Redis server. Also used for intra-node redis replication. |
| LDAP | Enables secure communications with LDAP server. |

### Passwords
The deployer will create several user accounts in the dependent systems. It uses default passwords in all cases and those passwords can be overridden with the defined ansible variables. To override these variables just define the variable in the deployer host file.

<table>
  <tr>
    <th style="background-color: grey;"d>User Account</th>
    <th style="background-color: grey;">Default Password</th>
    <th style="background-color: grey;">Variable Name</th>
    <th style="background-color: grey;">Description</th>
  </tr>
  <tr>
    <th colspan="4" style="background-color: grey; font-weight: bold">MongoDB</th>
  </tr>
  <tr>
    <td>admin</td>
    <td>admin</td>
    <td>mongo_user_admin_password</td>
    <td>Has full root access to the mongo database.</td>
  </tr>
  <tr>
    <td>itential</td>
    <td>itential</td>
    <td>mongo_user_itential_password</td>
    <td>Has read and write access to the “itential” database only.</td>
  </tr>
  <tr>
    <td>localaaa</td>
    <td>localaaa</td>
    <td>mongo_user_localaaa_password</td>
    <td>Has read and write access to the “LocalAAA” database.  This is used by the Local AAA adapter for local, non-LDAP logins.</td>
  </tr>
  <tr>
    <th colspan="4" style="background-color: grey; font-weight: bold">Redis</th>
  </tr>
  <tr>
    <td>admin</td>
    <td>admin</td>
    <td>redis_user_admin_password</td>
    <td>Has full root access to the Redis database, all channels, all keys, all commands.</td>
  </tr>
  <tr>
    <td>itential</td>
    <td>itential</td>
    <td>redis_user_itential_password</td>
    <td>Has full access to the Redis database, all channels, all keys, EXCEPT the following commands: asking, cluster, readonly, readwrite, bgrewriteaof, bgsave, failover, flushall, flushdb, psync, replconf, replicaof, save, shutdown, sync.</td>
  </tr>
  <tr>
    <td>repluser</td>
    <td>repluser</td>
    <td>redis_user_repluser_password</td>
    <td>Has access to the minimum set of commands to perform replication: psync, replconf, ping.</td>
  </tr>
  <tr>
    <td>admin</td>
    <td>sentineladmin</td>
    <td>redis_user_sentineladmin_password</td>
    <td>Full root access to Redis Sentinel.</td>
  </tr>
  <tr>
    <td>sentineluser</td>
    <td>sentineluser</td>
    <td>redis_user_sentineluser_password</td>
    <td>Has access to the minimum set of commands to perform sentinel monitoring: multi, slaveof, ping, exec, subscribe, config|rewrite, role, publish, info, client|setname, client|kill, script|kill.</td>
  </tr>
  <tr>
    <th colspan="4" style="background-color: grey;">RabbitMQ</th>
  </tr>
  <tr>
    <td>admin</td>
    <td>admin</td>
    <td>rabbitmq_admin_password</td>
    <td>The admin user with root permissions in this rabbit install.</td>
  </tr>
  <tr>
    <td>itential</td>
    <td>itential</td>
    <td>rabbitmq_password</td>
    <td>The itential user used by IAP to connect. This user is assigned the "monitoring" tag.</td>
  </tr>
</table>

### Obtaining the Itential binaries
The IAP and IAG binary files are hosted on the Itential Nexus repository. An account is required to access Itential Nexus. If you do not have an account, contact your Itential Sales representative.

## Installing the Deployer
The Itential Deployer can be installed via the `ansible-galaxy` utility. To do this, [configure Ansible][Ansible Configuration File] to use the Itential and Ansible Galaxy servers when installing collections. On your control node:

1. Create a blank file named `ansible.cfg` in your working directory. This will be your new Ansible configuration file.
2. Open `ansible.cfg` in a text editor and add the following. Be sure to supply the proper credentials where relevant.

    ```ini
    [galaxy]
    server_list = itential_galaxy, release_galaxy

    [galaxy_server.itential_galaxy]
    url=https://registry.aws.itential.com/repository/ansible-galaxy/
    username=<USERNAME>
    password=<PASSWORD>

    [galaxy_server.release_galaxy]
    url=https://galaxy.ansible.com/
    ```

3. Execute the following command to install the Itential Deployer:

    ```bash
    ansible-galaxy collection install itential.deployer
    ```

#### Offline Installations

If your control node does not have Internet connectivity, the Itential Deployer and its dependencies can be downloaded via another system, copied to your control node, and installed manually.

**&#9432; Note:**
Some of the following collections may already be installed on your control node. To verify, use the `ansible-galaxy collection list` command.
:::

1. Download the following collections from the provided links:

    - [Itential Deployer]
    - [Community General]
    - [Community MongoDB]
    - [Ansible POSIX]

2. Copy the downloaded collections to your control node.
3. Install the collections using the following command:

    ```bash
    ansible-galaxy collection install <COLLECTION>.tar.gz
    ```

## Running the Deployer
Once you have have installed the Itential Deployer, run it to begin deploying Itential to your environment. This section details a basic deployment using required variables only.

### Step 0: Confirm requirements & gather host information
Before running the deployer we must ensure the following:

- **Compatible OS**: Any managed nodes to be configured by the Itential Deployer must use an operating system that is compatible with the target version of IAP (and, if applicable, IAG). For more information, refer to the [Itential Dependencies] page.
- **Hostnames**: Any hostnames used by managed nodes must be DNS-resolvable.
- **Administrative Privileges**: The `ansible` user must have administrative privileges on managed nodes.
- **SSH Access**: The control node must have SSH connectivity to all managed nodes.
- **Additional CentOS 7 Requirements**: Ensure that Python `setuptools-2.0` is installed on any CentOS 7 managed nodes.

**&#9432; Note:**
Although the Itential Deployer can be used to configure nodes that use any supported operating system, it is optimized for RHEL 8 and 9.

### Step 1: Download Installation Artifacts

Download the IAP binary along with any desired IAP adapters (and, if applicable, the IAG binary) from the [Itential Nexus Repository] to local storage.

**&#9432; Note:**
If you are unsure which files should be downloaded for your environment, contact your Itential Professional Services representative.
:::

### Step 2: Copy Installation Artifacts into the Files Directory

First, determine what directory the Itential Deployer is installed to by using the `ansible-galaxy collection list` command. In the following example, the Deployer directory is `/Users/<USER>/.ansible/collections/ansible_collections/itential/deployer`.

_Example: Determining the Deployer Directory_

```bash
% ansible-galaxy collection list

# /Users/<USER>/.ansible/collections/ansible_collections
Collection        Version
----------------- -------
ansible.netcommon 4.1.0
ansible.posix     1.5.4
ansible.utils     2.9.0
arista.avd        3.8.2
arista.cvp        3.6.0
arista.eos        6.0.0
community.general 7.3.0
community.mongodb 1.6.1
itential.deployer 1.0.0
```

Next, copy the files downloaded in the previous step to the `files` subdirectory.

_Example: Copying to the Files Directory_

```bash
cd <DEPLOYER-DIR>/files
cp ~/Downloads/itential-premium_2023.1.1.linux.x86_64.bin .
cp ~/Downloads/automation_gateway-3.198.19+2023.1.0-py3-none-any.whl .
```

### Step 3: Create the Inventory File

Using a text editor, create an inventory file that defines your deployment environment. To do this, assign your managed nodes to the relevant groups according to what components you would like to install on them. In the following example:

- All required variables have been defined.
- The managed node `example1.host.com` has been assigned to all groups, with the **exception** of the `gateway` group. As such, all components **except** IAG will be installed on this node.
- The managed node `example2.host.com` has been assigned to the `gateway` group. As such, IAG will be installed on this node.

**&#9432; Note:**
Itential recommends that all inventories follow the best practices outlined in the [Ansible documentation][Ansible Best Practices].

_Example: Creating the Inventory File_

```bash
mkdir -p ~/itential-inventories/dev
vi ~/itential-inventories/dev/hosts
```

</br>

_Example: Inventory File (YAML Format)_

```yaml
all:
  vars:
    iap_release: 2023.1

  children:
    redis:
        hosts:
            example1.host.com:

    rabbitmq:
        hosts:
            example1.host.com:

    mongodb:
        hosts:
            example1.host.com:

    platform:
        hosts:
            example1.host.com:
        vars:
            iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin

    gateway:
        hosts:
            example2.host.com:
        vars:
            iag_release: 2023.1
            iag_whl_file: automation_gateway-3.227.0+2023.1.9-py3-none-any.whl
```

### Step 4: Run the Itential Deployer

Navigate to the Deployer directory and execute the following run command.

_Example: Running the Itential Deployer_

```bash
ansible-playbook itential.deployer.site -i ~/itential-inventories/dev -v
```

### Step 5: Confirm Successful Installation

After the Itential Deployer is finished running, perform the following checks on each component to confirm successful installation.

#### IAP and IAG

Use a web browser to navigate to the login page of your IAP/IAG servers. By default, it is located at `http://<hostname>:3000` or `http://<hostname>:8083`, respectively. If the IAP/IAG login page is displayed, the installation was successful.

If the login page is not displayed, check that the relevant service is running on the affected server using the `sudo systemctl status automation-platform` or `sudo systemctl status automation-gateway` command, respectively. The output should look similar to the following examples.

_Example Output: IAP System Status_

```bash
$ sudo systemctl status automation-platform
● automation-platform.service - Itential Automation Platform Service
   Loaded: loaded (/usr/lib/systemd/system/automation-platform.service; enabled; vendor preset: disabled)
   Active: active (running) since Wed 2023-02-01 15:21:45 UTC; 21h ago
 Main PID: 177517 (Pronghorn core)
    Tasks: 203 (limit: 23501)
   Memory: 1.0G
   CGroup: /system.slice/automation-platform.service
           ├─177517 Pronghorn core
           ├─177556 Pronghorn AGManager Application
           ├─177577 Pronghorn AdminEssentials Application
           ├─177588 Pronghorn AppArtifacts Application
           ├─177606 Pronghorn AutomationCatalog Application
           ├─177622 Pronghorn AutomationStudio Application
           ├─177659 Pronghorn ConfigurationManager Application
           ├─177674 Pronghorn FormBuilder Application
           ├─177690 Pronghorn JsonForms Application
           ├─177708 Pronghorn Jst Application
           ├─177725 Pronghorn MOP Application
           ├─177738 Pronghorn OperationsManager Application
           ├─177758 Pronghorn Search Application
           ├─177784 Pronghorn Tags Application
           ├─177800 Pronghorn TemplateBuilder Application
           ├─177820 Pronghorn WorkFlowEngine Application
           ├─177833 Pronghorn WorkflowBuilder Application
           └─177860 Pronghorn local_aaa Adapter
```

</br>

_Example Output: IAG System Status_

```bash
$ sudo systemctl status automation-gateway
● automation-gateway.service - Itential Automation Gateway
   Loaded: loaded (/etc/systemd/system/automation-gateway.service; enabled; vendor preset: disabled)
   Active: active (running) since Tue 2023-01-17 16:48:29 UTC; 1 months 0 days ago
 Main PID: 94842 (automation-gate)
    Tasks: 10 (limit: 23435)
   Memory: 168.8M
   CGroup: /system.slice/automation-gateway.service
           ├─94842 /opt/automation-gateway/venv/bin/python3 /opt/automation-gateway/venv/bin/automation-gateway --properties-file=/etc/automation-gateway/propert>
           └─94844 /opt/automation-gateway/venv/bin/python3 /opt/automation-gateway/venv/bin/automation-gateway --properties-file=/etc/automation-gateway/propert>
```

#### MongoDB, Redis, and RabbitMQ

From the command line of each dependency server, use the `sudo systemctl status <service>` command to confirm that the relevant service is running. When executing the command, replace `<service>` with one of the following:

- **MongoDB**: `mongod`
- **Redis**: `redis`
- **RabbitMQ**: `rabbitmq-server`

The output should look similar to the following examples.

_Example Output: MongoDB Status_

```bash
$ sudo systemctl status mongod
● mongod.service - MongoDB Database Server
     Loaded: loaded (/usr/lib/systemd/system/mongod.service; enabled; preset: disabled)
     Active: active (running) since Thu 2023-06-22 04:49:56 CST; 20h ago
       Docs: https://docs.mongodb.org/manual
   Main PID: 54594 (mongod)
     Memory: 156.7M
        CPU: 46.078s
     CGroup: /system.slice/mongod.service
             └─54594 /usr/bin/mongod -f /etc/mongod.conf
```

</br>

_Example Output: Redis Status_

```bash
$ sudo systemctl status redis
● redis.service - Redis persistent key-value database
     Loaded: loaded (/usr/lib/systemd/system/redis.service; enabled; preset: disabled)
    Drop-In: /etc/systemd/system/redis.service.d
             └─limit.conf
     Active: active (running) since Thu 2023-06-22 04:47:39 CST; 20h ago
   Main PID: 15723 (redis-server)
     Status: "Ready to accept connections"
      Tasks: 5 (limit: 22862)
     Memory: 9.7M
        CPU: 13.409s
     CGroup: /system.slice/redis.service
             └─15723 "/usr/bin/redis-server 127.0.0.1:6379"
```

</br>

_Example Output: RabbitMQ Status_

```bash
$ sudo systemctl status rabbitmq-server
● rabbitmq-server.service - RabbitMQ broker
     Loaded: loaded (/usr/lib/systemd/system/rabbitmq-server.service; enabled; preset: disabled)
    Drop-In: /etc/systemd/system/rabbitmq-server.service.d
             └─limits.conf
     Active: active (running) since Thu 2023-06-22 04:48:15 CST; 20h ago
   Main PID: 24244 (beam.smp)
      Tasks: 25 (limit: 22862)
     Memory: 138.6M
        CPU: 1min 28.641s
     CGroup: /system.slice/rabbitmq-server.service
             ├─24244 /usr/lib64/erlang/erts-13.2.2.1/bin/beam.smp -W w -MBas ageffcbf -MHas ageffcbf -MBlmbcs 512 -MHlmbcs 512 -MMmcs 30 -pc uni>
             ├─24257 erl_child_setup 64000
             ├─24284 /usr/lib64/erlang/erts-13.2.2.1/bin/epmd -daemon
             ├─24307 /usr/lib64/erlang/erts-13.2.2.1/bin/inet_gethost 4
             ├─24308 /usr/lib64/erlang/erts-13.2.2.1/bin/inet_gethost 4
             └─24311 /bin/sh -s rabbit_disk_monitor
```

## Sample host files for supported architectures
Below are simplified sample host files that describe the basic configurations to produce the supported architectures. These are intended to be starting points only.

### All-in-one
Simple environment. IAP and all of its dependencies all on one host.

_Example: All-in-one Inventory File (YAML Format)_

```yaml
all:
  vars:
    iap_release: 2023.1

  children:
    redis:
        hosts:
            example1.host.com:

    rabbitmq:
        hosts:
            example1.host.com:

    mongodb:
        hosts:
            example1.host.com:

    platform:
        hosts:
            example1.host.com:
        vars:
            iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin

    gateway:
        hosts:
            example2.host.com:
        vars:
            iag_release: 2023.1
            iag_whl_file: automation_gateway-3.227.0+2023.1.9-py3-none-any.whl
```

### Minimal Architecture
Similar to All-in-one but installs components on separate hosts.

_Example: Minimal Architecture Inventory File (YAML Format)_

```yaml
all:
  vars:
    iap_release: 2023.1

  children:
    redis:
        hosts:
            redis.host.com:

    rabbitmq:
        hosts:
            rabbitmq.host.com:

    mongodb:
        hosts:
            mongodb.host.com:

    platform:
        hosts:
            automation-platform.host.com:
        vars:
            iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin

    gateway:
        hosts:
            automation-gateway.host.com:
        vars:
            iag_release: 2023.1
            iag_whl_file: automation_gateway-3.227.0+2023.1.9-py3-none-any.whl
```

### Highly Available Architecture
Fault tolerant architecture.

_Example: Highly Available Architecture Inventory File (YAML Format)_

```yaml
all:
  vars:
    iap_release: 2023.1
    # Instructs deployer to build a cluster of each
    redis_replication: true
    rabbitmq_cluster: true
    mongodb_replication: true

  children:
    redis:
        hosts:
            redis1.host.com:
            redis2.host.com:
            redis3.host.com:

    rabbitmq:
        hosts:
            rabbitmq1.host.com:
            rabbitmq2.host.com:
            rabbitmq3.host.com:

    mongodb:
        hosts:
            mongodb1.host.com:
            mongodb2.host.com:
            mongodb3.host.com:

    platform:
        hosts:
            automation-platform1.host.com:
            automation-platform2.host.com:
        vars:
            iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin

    gateway:
        hosts:
            automation-gateway1.host.com:
        vars:
            iag_release: 2023.1
            iag_whl_file: automation_gateway-3.227.0+2023.1.9-py3-none-any.whl
```

### Active/Standby Architecture


_Example: Active/Standby Architecture Inventory File (YAML Format)_

```yaml
all:
  vars:
    iap_release: 2023.1

  children:
    redis:
        hosts:
            datacenter1.redis1.host.com:
            datacenter1.redis2.host.com:
            datacenter1.redis3.host.com:

    redis_secondary:
        hosts:
            datacenter2.redis1.host.com:
            datacenter2.redis2.host.com:
            datacenter2.redis3.host.com:

    rabbitmq:
        hosts:
            datacenter1.rabbitmq1.host.com:
            datacenter1.rabbitmq2.host.com:
            datacenter1.rabbitmq3.host.com:

    rabbitmq_secondary:
        hosts:
            datacenter2.rabbitmq4.host.com:
            datacenter2.rabbitmq5.host.com:
            datacenter2.rabbitmq6.host.com:

    mongodb:
        hosts:
            datacenter1.mongodb1.host.com:
            datacenter1.mongodb2.host.com:
            datacenter2.mongodb3.host.com:
            datacenter2.mongodb4.host.com:

    mongodb_arbiter:
        hosts:
            datacenter3.mongodb-arbiter.host.com:

    platform:
        hosts:
            datacenter1.automation-platform1.host.com:
            datacenter1.automation-platform2.host.com:
        vars:
            iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin

    platform_secondary:
        hosts:
            datacenter2.automation-platform3.host.com:
            datacenter2.automation-platform4.host.com:
        vars:
            iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin

    gateway:
        hosts:
            datacenter2.automation-gateway1.host.com:
        vars:
            iag_release: 2023.1
            iag_whl_file: automation_gateway-3.227.0+2023.1.9-py3-none-any.whl
```

<!-- ### Blue/Green Architecture
_Example: Blue/Green Inventory File (YAML Format)_

```yaml
all:
  vars:
    iap_release: 2023.1

  children:
    redis:
        hosts:
            example1.host.com:

    rabbitmq:
        hosts:
            example1.host.com:

    mongodb:
        hosts:
            example1.host.com:

    platform:
        hosts:
            example1.host.com:
        vars:
            iap_bin_file: itential-premium_2023.1.1.linux.x86_64.bin

    gateway:
        hosts:
            example2.host.com:
        vars:
            iag_release: 2023.1
            iag_whl_file: automation_gateway-3.227.0+2023.1.9-py3-none-any.whl
``` -->

<!-- ### Available tags
The ansible execution can be more finely controled by using the builtin ansible tags. The below table defines the available tags and describes what they can do. -->

## Appendix A - Advanced Configuration Properities

Each component installed by the Itential Deployer can be granularly configured by defining additional variables in the relevant inventory file. These additional variables are detailed in the following tables.

**_MongoDB Variables_**

| Variable | Group | Type    | Description   | Example |
| :-------- | :----: | :------ | :------------- | :------- |
| `mongodb_replication`          | `all` | String  | Designates whether or not a MongoDB replica set is created from all managed nodes assigned to the `mongodb` group.  | `true` <br /> `false` |
| `mongodb_auth`    | `all` | Boolean | Designates whether or not MongoDB servers require authentication via username and password for connections.  | `true` <br /> `false` |
| `mongodb_tls`      | `all` | Boolean | Designates whether or not MongoDB servers secure their communications with TLS encryption.  | `true` <br /> `false` |
| `mongo_user_itential_password` | `all` | String  | The password of the MongoDB `itential` user.   | |
| `mongo_auth_keyfile_source`    | `all` | String  | The name of the `.pem` key file to be used for communication between members of the MongoDB replica set. This must be provided; it is not generated by the Itential Deployer. This is only required when `mongodb_replication` and `mongodb_auth` are set to `true`. | `mongo-replicaset-key.pem` |
| `mongo_cert_keyfile_source`    | `all` | String  | The name of the `.pem` key file that contains the TLS certificate and key to be used on MongoDB servers. This must be provided; it is not generated by the Itential Deployer. This is only required when `mongodb_tls` is set to `true`.   | `mongodb.pem` |
| `mongo_root_ca_file_source`    | `all` | String  | The name of the `.pem` key file obtained from a certificate authority that contains the root certificate chain. This must be provided; it is not generated by the Itential Deployer. This is only required when `mongodb_tls` is set to `true`.    | `rootCA.pem`  |

</br>

**_Redis Variables_**

| Variable | Group | Type    | Description   | Example |
| :-------- | :----: | :------ | :------------- | :------- |
| `redis_replication` | `all` | Boolean | Designates whether or not a Redis cluster is created from all managed nodes assigned to the `redis` group. If set to `true`, a cluster is created and Redis Sentinel is used to provide high availability (HA) monitoring. | `true` <br /> `false` |
| `redis_auth`        | `all` | Boolean | Designates whether or not Redis servers require authentication via username and password for connections.   | `true` <br /> `false` |

</br>

**_RabbitMQ Variables_**

| Variable | Group | Type    | Description   | Example |
| :-------- | :----: | :------ | :------------- | :------- |
| `rabbitmq_cluster` | `all` | Boolean | Designates whether or not a RabbitMQ cluster is created from all managed nodes assigned to the `rabbitmq` group. | `true` <br /> `false` |
| `rabbitmq_ssl`     | `all` | Boolean | Designates whether or not RabbitMQ nodes secure their communications with TLS encryption.   | `true` <br /> `false` |


## Appendix B - Offline Installs

## Appendix C - Definion of "Highly Available" dependencies
### Highly Available MongoDB
MongoDB clusters operate a primary/secondary model where data written to the primary will replicate to the secondary. There is much literature on the internet about Mongo clusters. That will not be covered here. However, it's important to note that Itential’s preferred MongoDB cluster will assume the following requirements:

- Authentication between the replica members done with either a shared key or X.509 certificate.
- The database will have an admin user able to perform any operation.
- The database will have an “itential” user that is granted the least amount of privileges required by the application.

Initial passwords are intended to be changed.

### Highly Available Redis
Redis clusters operate a primary/secondary model where data written to the primary will replicate to the secondary. There is much literature on the internet about Redis clusters. That will not be covered here. However, it's important to note that Itential’s preferred Redis cluster will assume the following requirements:

- Authentication between the replica members is done with users defined in the Redis config file.
- Redis will have an admin user able to perform any operation.
- Redis will have an “itential” user that is granted the least amount of privileges required by the application.
- Redis will have a replication user that is granted the least amount of privileges required by the replication process.
- Initial passwords are intended to be changed.
- Redis Sentinel will be included to monitor the Redis cluster and will be colocated with Redis.
- Redis Sentinel will have an admin user able to perform a Sentinel task.
- Redis nodes maintain a low latency connection between nodes to avoid replication failures.

### Highly Available Rabbitmq
Rabbitmq clusters operate independently of one another but they do require knowledge of one another. There is much literature on the internet about Rabbitmq clusters. That will not be covered here. However, it's important to note that Itential’s preferred Rabbitmq cluster will assume the following requirements:

- Rabbitmq nodes depend on DNS resolution. Itential will be using host files to accomplish this.
- Rabbitmq will have an admin user able to perform any operation.
- Rabbitmq will have an “itential” user that is granted the least amount of privileges required by the application.

Rabbitmq nodes maintain a low latency connection between nodes to avoid replication failures.
