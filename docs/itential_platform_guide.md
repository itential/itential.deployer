# Itential Platform Guide

The playbook and role in this section install and configure Itential Platform.  There is currently
one role:

* `platform` – Installs Itential Platform and performs a base configuration.

## Roles

### Platform Role

The `platform` role performs a base install of Itential Platform including any OS packages
required. It includes the appropriate version of Python, Pip, Jinja, and TextFSM. It handles a few
security vulnerabilities. It creates the appropriate Linux users, directories, log files, and
systemd services.

It will install the source code for each adapter that is listed. It will also install any listed
custom adapters. It can install from a Git URL or using an adapter archive generated by Adapter
Builder.

It will install app-artifacts, which is an optional Itential application that is primarily used
only in development environments for packaging use cases together for deployment. It will restart
the automation-platform service when complete.

When there is a device configured in the `gateway` group this role will also install and configure
an IAG adapter that points to the gateway server(s) named in the `gateway` group.

## Variables

### Static Variables

The variables located in the `vars` directory of each role are "static" and not meant to be
overridden by the user.  Since these variable files are included at run-time based on the Itential
Platform release and OS major version, they have a higher precedence than the variables in the
inventory and are not easily overridden.

| Variable | Group | Type | Description | Default Value |
| :------- | :---- | :--- | :---------- | :------------ |
| `platform_install_dir` | `platform` | String | The Itential Platform installation directory. | `/opt/itential/platform/server` |
| `platform_log_dir` | `platform` | String | The Itential Platform log directory. | `/var/log/itential` |

### Global Variables

The variables in this section are configured in the inventory in the `all` group vars.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| `platform_release` | Fixed-point | Designates the Itential Platform major version. | N/A |

The `platform_release` must be defined in the inventory.  This variable, along with the OS major
version, is used to determine the static variables. When `platform_release` is not defined then each
installed component must explicitly list the packages that will be installed.  This allows for an
easy installation for most use cases and a convenient and explicit way to customize a non-standard
install.

### Platform Role Variables

The variables in this section may be overridden in the inventory in the `platform` group vars. In
most cases accepting the defaults is what you want except for in some more advanced installations.

The variable `platform_encryption_key` is required for this role to run. This value must be a 64
character hexadecimal string.

The following approaches may be followed for generating an encryption key:

- Generating a randomized key value: `openssl rand -hex 32`
- Generating a key value using an existing password value as a base: `printf '%s' “$PASSWORD” | sha256sum | head -c 64`

Whichever approach you use to generate the key, ensure the result is persisted in a secrets
repository for safe keeping before applying it to your Itential Platform installation. Losing
access to this key means losing access to secret values stored inside of Itential Platform.

More info on the encryption key:
<https://docs.itential.com/docs/platform-6-installation#create-the-encryption-key>

#### Installation Variables

These variables will effect how the installation occurs.

| Variable | Group | Type | Description | Default Value |
| :------- | :---- | :--- | :---------- | :------------ |
| `platform_packages` | `platform` | List of Strings | The Itential Platform RPMs to install. The items can either be filenames or URLs. | N/A |
| `repository_username` | `platform` | String | The username for authentication of the repository. | N/A |
| `repository_password` | `platform` | String | The password for authentication of the repository. | N/A |
| `repository_api_key` | `platform` | String | The API for authentication of the repository. Can be used instead of username/password for authentication.| N/A |

If `platform_packages` contains URLs, either `repository_api_key` or `repository_username` and
`repository_password` must be defined.

#### Authentication Variables

These variables control authentication and user session behaviors. The following table lists the
default variables located in `roles/platform/defaults/main/authentication.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_auth_unique_sessions_enabled | Boolean | If true, logs out existing sessions for a user when they log in with a new session. | `false` |
| platform_auth_admin_groups | List(Object) | Members of these groups will be implicitly assigned with admin permissions. | { "provenance": "Local AAA", "group": "pronghorn_admin" } |
| platform_auth_broker_principal_enabled | Boolean | Enables a AAA adapter to custom build the principal object for a user with a "buildPrincipal" method. | `false` |
| platform_auth_session_cookie_name | String | The name of the cookie used for a user session. | `token` |
| platform_auth_session_ttl | Integer | The time in minutes before a user session expires. | 60 |
| platform_default_user_enabled | Boolean | Enables a default user to be used for login when SSO is not configured and no AAA Adapter exists. | `true` |
| platform_default_user_username | String | The username of the default user. | `admin` |
| platform_default_user_password | String | The password of the default user. | `admin` |

#### Broker Variables

These variables control device broker behaviors. The following table lists the default variables
located in `roles/platform/defaults/main/brokers.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_device_broker_default_adapter_priority | List(String) | A list of adapter types that manages the devices. |  |
| platform_device_broker_run_command_adapter_preference | String | Runs a command on a device. |  |
| platform_broker_validation_enabled | Boolean | If true, the platform will perform strict JSON Schema validation on messages into the brokers and coming back to the broker layer from adapters. | false |

#### Integration Worker Variables

These variables control integration worker behaviors. The following table lists the default
variables located in `roles/platform/defaults/main/integration_worker.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_integration_thread_count | Integer | The number of threads available for API requests. | 5 |
| platform_integration_timeout | Integer | The number of milliseconds until an integration request times out. | 15000 |

#### Logger Variables

These variables control logging and syslog integration behaviors. The following table lists the
default variables located in `roles/platform/defaults/main/logging.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_log_max_files | Integer | The maximum number of each log file to keep as rotation occurs. | 100 |
| platform_log_max_file_size | Integer | The maximum file size in bytes of each log file before rotation occurs. | 1048576 |
| platform_log_level | String | The minimum log level to display in the log file. | `info` |
| platform_log_dir | String | The absolute directory path where log files are written. | `/var/log/itential/platform` |
| platform_log_filename | String | The name of the primary platform log file. | `platform.log` |
| platform_log_level_console | String | The minimum log level to display in the console (stdout). | `warn` |
| platform_webserver_log_directory | String | The absolute directory path where webserver log files are written. | `/var/log/itential/platform` |
| platform_webserver_log_filename | String | The name of the webserver log file. | `webserver.log` |
| platform_log_level_syslog | String | The minimum log level to send to the syslog server. | `warning` |
| platform_syslog_host | String | The hostname or IP address of the syslog server. | `localhost` |
| platform_syslog_port | Integer | The port number of the syslog server. | 514 |
| platform_syslog_protocol | String | The protocol to use when sending logs to the syslog server. | `udp4` |
| platform_syslog_facility | String | The syslog facility to use when sending logs to the syslog server. | `local0` |
| platform_syslog_type | String | The syslog message format to use when sending logs to the syslog server. | `BSD` |
| platform_syslog_path | String | The path to the syslog server file. | `/dev/log` |
| platform_syslog_pid | String | The process property to include as the process id in the syslog message. | `process.pid` |
| platform_syslog_localhost | String | The hostname to include in the syslog message. | `localhost` |
| platform_syslog_app_name | String | The process property to include as the application name in the syslog message. | `process.title` |
| platform_syslog_eol | String | The end of line character to include in the syslog message. |  |

#### Platform UI Variables

These variables control UI behaviors. The following table lists the default variables located in
`roles/platform/defaults/main/platform_ui.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_ui_layout_file | String | Path to the layout file extended in pug templates. |  |
| platform_ui_home_file | String | Path to the HTML file that will be displayed as the home page for the UI. | `node_modules/@itential/iap-ui/build/index.html` |
| platform_ui_login_file | String | Path to the HTML file that will be displayed as the login page for the UI. | `node_modules/@itential/iap-ui/build/index.html` |
| platform_ui_profile_file | String | Path to the HTML file that will be displayed as the profile page for the UI. | `node_modules/@itential/iap-ui/build/index.html` |
| platform_ui_favicon_file | String | Path to the favicon file that will be displayed in the browser tab. | `ui/img/favicon.ico` |
| platform_ui_apple_touch_icon_file | String | Path to the apple touch icon file that will be displayed on iOS devices. | `ui/img/apple-touch-icon.png` |

#### Redis Variables

These variables control Redis integration behaviors. The following table lists the default
variables located in `roles/platform/defaults/main/redis.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_redis_db | Integer | The Redis keyspace (database number) to use for the connection. | 0 |
| platform_redis_auth_enabled | String | Flag to enable Redis authentication. | `true` |
| platform_redis_username | String | The username to use when connecting to Redis. | `itential` |
| platform_redis_password | String | The password to use when connecting to Redis. | `itential` |
| platform_redis_max_retries_per_request | Integer |  The maximum number of times to retry a request to Redis when the connection is lost. | 20 |
| platform_redis_max_heartbeat_write_retries | Integer | The maximum number of times to retry writing a heartbeat message to Redis from a service. | 20 |
| platform_redis_host | String | The hostname of the Redis server. Not used when connecting to Redis Sentinels. | `localhost` |
| platform_redis_port | Integer | The port to use when connecting to this Redis instance. | 6379 |
| platform_redis_sentinels | List(Object) | The list of Redis Sentinel servers (hostnames and ports) to use for high availability. |  |
| platform_redis_sentinel_username | String | The username to use when connecting to Sentinel. | `sentineluser` |
| platform_redis_sentinel_password | String | The password to use when connecting to Sentinel. | `sentineluser` |
| platform_redis_name | String | The Redis primary name. This only has meaning when Redis is running with replication enabled. The sentinels will monitor this node and consider it down only when the sentinels agree. Note: The primary name should not include special characters other than: .-_ and no whitespaces. | `itentialmaster` |
| platform_redis_tls | Object | Redis TLS configuration options for secure connections. Refer to NodeJS TLS library for all supported options. |  |

#### SNMP Variables

These variables control SNMP behaviors. The following table lists the default variables located in
`roles/platform/defaults/main/snmp.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_snmp_alarm_configs | List(Object) |  | `{ "ip": "localhost", "community": "public", "type": "trap", "properties": { "port": 161, "retries": 1, "timeout": 5000, "transport": "udp4", "trapPort": 162, "version": "V1" } }` |

#### Vault Variables

These variables control Hashicorp Vault integration behaviors. The following table lists the
default variables located in `roles/platform/defaults/main/vault.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_configure_vault | Boolean | Flag to enable/disable configuring Vault in Itential Platform | `false` |
| platform_vault_token_dir | String | The directory to store the vault root key in | `{{ platform_install_dir }}/keys` |
| platform_vault_url | String | The URL to the Hashicorp Vault server. | `http://localhost:8200` |
| platform_vault_auth_method | String | The authorization method to connect to Hashicorp Vault. Either token or approle. | `token` |
| platform_vault_role_id | String | Hashicorp Vault Role ID used for AppRole authentication. |  |
| platform_vault_secret_id | String | Hashicorp Vault Secret ID used for AppRole login. |  |
| platform_vault_approle_path | String | The path where the AppRole was enabled. |  |
| platform_vault_token_file | String | The file path to a token file. The token is used for authentication to access Vault secrets. | `{{ platform_vault_token_dir }}/vault.token` |
| platform_vault_secrets_endpoint | String | The endpoint for the Secrets Engine that is used. | `itential/data` |
| platform_vault_read_only | Boolean | If true, only reads secrets from Hashicorp Vault. Otherwise, the platform can write secrets to Vault for storage. | `true` |

#### Webserver Variables

These variables control basic webserver behaviors. The following table lists the default variables
located in `roles/platform/defaults/main/webserver.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_webserver_cache_control_enabled | Boolean | A toggle to instruct the webserver to include HTTP cache control headers on the response. | `false` |
| platform_webserver_timeout | Integer | Timeout to use for incoming HTTP requests to the platform API, in milliseconds. | 300000 |
| platform_webserver_response_header_access_control_allow_origin | String | The value of the HTTP Access-Control-Allow-Origin header returned to clients. | `"*"` |
| platform_webserver_http_enabled | Boolean | If true, allows the webserver to respond to insecure HTTP requests. | `true` |
| platform_webserver_http_port | Integer | The port on which the webserver listens for HTTP requests. | 3000 |
| platform_webserver_https_enabled | Boolean | If true, allows the webserver to respond to secure HTTPS requests. | `false` |
| platform_webserver_https_port | Integer | The port on which the webserver listens for HTTPS requests. | 3443 |
| platform_webserver_https_key | String | The path to the public key file used for HTTPS connections. | `/opt/itential/platform/keys/key.pem` |
| platform_webserver_https_passphrase | String | The passphrase for the private key used to enable TLS sessions. |  |
| platform_webserver_https_cert | String | The path to the certificate file used for HTTPS connections. | `/opt/itential/platform/keys/cert.pem` |
| platform_webserver_https_secure_protocol | String | The set of allowed SSL/TLS protocol versions. | `TLSv1_2_method` |
| platform_webserver_https_ciphers | String |  The allowed SSL/TLS cipher suite. | `ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA256:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA` |
| platform_webserver_https_client_reneg_limit | Integer | Specifies the number of renegotiations that are allowed in a single HTTPS connection. | 3 |
| platform_webserver_https_client_reneg_window | Integer | Specifies the time renegotiation window in seconds for a single HTTPS connection. | 600 |
| platform_webserver_http_allowed_optional_verbs | List(String) | The set of allowed HTTP verbs in addition to those defined in the standard HTTP/1.1 protocol. |  |

#### Workflow Worker Variables

These variables control Workflow Engine behaviors. The following table lists the default variables
located in `roles/platform/defaults/main/workflow_worker.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_task_worker_enabled | Boolean | If true, will start working tasks immediately after the server startup process is complete. If false, the task worker must be enabled manually via the UI/API. | `true` |
| platform_job_worker_enabled | Boolean | If true, will allow jobs to be started after the server startup process is complete. If false, API calls to start Jobs will return an error until enabled manually via the UI/API. | `true` |

#### MongoDB Variables

These variables control MongoDB integration behaviors. The following table lists the default
variables located in `roles/platform/defaults/main/mongodb.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_mongo_auth_enabled | Boolean | Instructs the MongoDB driver to use the configured username/password when connecting to MongoDB. | `true` |
| platform_mongo_user | String | The username to use when connecting to MongoDB. | `itential` |
| platform_mongo_password | String | The password to use when connecting to MongoDB. | `itential` |
| platform_mongo_auth_db | String | The name of the database that the MongoDB user must authenticate against. |  |
| platform_mongo_bypass_version_check | Boolean | If true, the server will not check if it is connecting to a compatible MongoDB version. | `false` |
| platform_mongo_db_name | String | The name of the MongoDB logical database to connect to. | `itential` |
| platform_mongo_url | String | The MongoDB connection string. For a replica set this will include all members of the replica set. For Mongo Atlas this will be the SRV connection format. | `mongodb://localhost:27017` |
| platform_mongo_tls_enabled | Boolean | Instruct the MongoDB driver to use TLS protocols when connecting to the database. | `false` |
| platform_mongo_tls_allow_invalid_certificates | Boolean | If true, disables the validation checks for TLS certificates on other servers in the cluster and allows the use of invalid or self-signed certificates to connect. | `false` |
| platform_mongo_tls_ca_file | String | The .pem file that contains the root certificate chain from the Certificate Authority. Specify the file name of the .pem file using absolute paths. |  |
| platform_mongo_max_pool_size | Integer | The maximum number of connections in a connection pool. Each application/adapter has its own connection pool. |  |

#### Platform Variables

These variables control core platform behaviors. The following table lists the default variables
located in `roles/platform/defaults/main/platform.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_mongodb_root_ca_file_destination | String | Destination as referenced by itential user when connecting from itential host. This is ultimately stored in the mongo database to be read by Itential Platform, therefore this is the location as seen from the Itential Platform host. | `/opt/itential/keys/mongo-rootCA.pem` |
| platform_package_dependencies | List(String) | Required OS packages for install. | `glibc-common, openldap, openldap-clients, openssl, git` |
| platform_python_base_dependencies | List(String) | Required python packages for install. | `pip, setuptools, wheel` |
| platform_python_executable | String | The python executable locations. These will be symlinks to the appropriate executables in /usr/bin. | `/usr/bin/python{{ platform_python_version }}` |
| platform_pip_executable | String | The pip executable locations. These will be symlinks to the appropriate executables in /usr/bin. | `/usr/bin/pip{{ platform_python_version }}` |
| platform_configure_iag_adapters | Boolean | Should the platform configure and add any IAG adapters that it discovers? Based on the presence of devices in the gateway group this will build adapter configs for each that it finds and insert them into the mongo database. | `true` |
| platform_iag_adapter_token_timeout | Integer | If the IAG adapters are configured, set the token timeout. The default value is 3600000 milliseconds (60 minutes). | 3600000 |
| platform_user | String | The default user that runs the server process. | `itential` |
| platform_group | String | The default group that runs the server process. | `itential` |
| platform_upload_using_rsync | Boolean | Flag to determine whether to use rsync when uploading artifacts. | `false` |
| platform_delete_package_lock_file | Boolean | Flag to remove the package-lock.json file before running the NPM install. | `true` |
| platform_disable_git_safe_repo_checks | Boolean | Flag to disable Git safe repo check. | `true` |
| platform_npm_ignore_scripts | Boolean | Flag to prevent the NPM scripts from running when running the NPM install. | `true` |
| platform_app_artifacts_enabled | Boolean | Flag to install app-artifacts. | `false` |

#### Server Variables

These variables control Itential server behaviors. The following table lists the default variables
located in `roles/platform/defaults/main/server.yml`.

| Variable | Type | Description | Default Value |
| :------- | :--- | :---------- | :------------ |
| platform_profile_id | String | The name of the profile document to load from the MongoDB where legacy configuration properties are stored. Not required for installations that are using environment variables or a properties file. | |
| platform_server_id | String | An identifier for the server instance. This is used to uniquely identify the server in a multi-server environment. If not provided, the server will generate one on startup. | `{{ inventory_hostname }}` |
| platform_services | List | A whitelist of services (applications/adapters) to initialize on startup of the platform. If no value is given, all services will be initialized. |  |
| platform_service_blacklist | List | The service type that will be denied CRUD operation access. |  |
| platform_encrypted | Boolean | Indicates whether the platform is using encrypted code files. | `true` |
| platform_shutdown_timeout | Integer | The amount of time a service should wait before shutting down, in seconds. | 3 |
| platform_service_launch_delay | Integer | The application/adapter launch delay, in seconds. | 1 |
| platform_service_launch_timeout | Integer | The application/adapter launch timeout, in seconds. | 600 |
| platform_service_health_check_interval | Integer | How often to update service health, measured in seconds. | 5 |
| platform_service_health_check_unhealthy_threshold | Integer | The number of failed health checks in a row before a service is considered to be “unhealthy”. | 3 |
| platform_dead_process_check_enabled | Boolean | If true, the platform will periodically check for dead processes. | `false` |
| platform_dead_process_check_interval | Integer | How often to check if application/adapter stopped sending healthcheck pings, in seconds. | 5 |
| platform_dead_process_max_period | Integer | Maximum time period for application/adapter without sending healthcheck ping, in seconds. | 15 |
| platform_service_crash_recovery_max_retries | Integer | Specifies the amount of times services will retry on crash before stopping. | 10 |
| platform_service_crash_recovery_reset_retries_after_ms | Integer | Specifies the amount of times between each retry before the count will reset in milliseconds. | 60000 |
| platform_external_request_timeout | Integer | The timeout for external API requests, in seconds. | 5 |
| platform_device_count_polling_interval | Integer | The interval for how often IAP polls for the number of devices, in hours. | 24 |
| platform_audit_enabled | Boolean | If true, the platform will track detailed audit events. | `false` |

## Building the Inventory

### Example Inventory - Single Itential Platform Node

To install and configure Itential Platform, add a `platform` group and host(s) to your inventory
and configure the `platform_release` and `platform_packages`. The URLs in `platform_packages`
supports Sonatype Nexus, JFrog Artifactory and Gitlab. It is recommended to use
`repository_username` and `repository_password` for Nexus and `repository_api_key` for
Artifactory and Gitlab.  The following inventory shows a basic Itential Platform configuration
with a single node.

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    platform:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_packages:
          - <rpm1>
          - <rpmN>
```

### Example Inventory - Install Adapters

To install Itential adapters, add the `platform_adapters` flag to the `platform` group and set it
to `true`, and configure the adapters in the `platform_adapters` variable.

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    platform:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_packages:
          - <rpm1>
          - <rpmN>
        platform_adapters:
          - <git_repo1>
          - <git_repoN>
          - <zip_archive1>
          - <zip_archiveN>
```

### Example Inventory - Install App-Artifact

To install App-Artifacts, add the `platform_app_artifacts_enabled` flag to the `platform` group and
set it to `true` and configure the `platform_app_artifacts_source_file`.

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    platform:
      hosts:
        host1:
          ansible_host: addr1
      vars:
        platform_app_artifacts_enabled: true
        platform_app_artifacts_source_file: archive1
```

### Example Inventory - Use Hashicorp Vault

To configure the Platform to integrate with Hashicorp Vault for secrets management

```yaml
all:
  vars:
    platform_release: 6.0

  children:
    platform:
      hosts:
        <host1>:
          ansible_host: <addr1>
      vars:
        platform_configure_vault: true
        platform_vault_url: http://hashi-vault-example.com:8200
```

## Running the Playbook

To execute all Platform roles, run the `platform` playbook:

```bash
ansible-playbook itential.deployer.platform -i <inventory>
```

The Platform playbook and role supports the following tags:

| Tag | Tasks |
| :-- | :---- |
| configure_os | Create required accounts and directories<br>Configure sudoers and firewalld |
| install_dependencies | Install NodeJS and Python |
| install_nodejs | Install NodeJS |
| install_python | Install Python |
| install_platform | Install Itential Platform |
| install_adapters | Install Itential Platform adapters |
| install_app_artifacts | Install Itential Platform App Artifacts |
| configure_selinux | Configure SELinux |
| configure_vault | Configure Hashicorp Vault |
| configure_platform | Configure Itential Platform systemd service and properties file |

For example, to regenerate the systemd service script and platform.properties file run the platform 
playbook with the `configure_platform` tag:

```bash
ansible-playbook itential.deployer.platform -i <inventory> --tags configure_platform
```
