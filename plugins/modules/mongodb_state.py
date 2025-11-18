#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mongodb_state
short_description: Detect MongoDB configuration state
description:
    - Checks if MongoDB service is running
    - Detects if MongoDB has authentication enabled
    - Detects if TLS/SSL is enabled
    - Detects if MongoDB is a replica set or standalone
    - Identifies the primary host in a replica set
    - Lists all replica set members with detailed status
    - Validates admin credentials if provided
'''

RETURN = r'''
mongodb_running:
    description: Whether MongoDB is running
    type: bool
    returned: always
    sample: true
tls_enabled:
    description: Whether TLS/SSL is enabled
    type: bool
    returned: always
    sample: true
tls_mode:
    description: TLS mode (disabled, allowTLS, preferTLS, requireTLS)
    type: str
    returned: always
    sample: "requireTLS"
tls_certificate_key_file:
    description: Path to TLS certificate file
    type: str
    returned: when tls_enabled is true
    sample: "/etc/ssl/mongodb.pem"
tls_ca_file:
    description: Path to TLS CA file
    type: str
    returned: when tls_enabled is true
    sample: "/etc/ssl/ca.pem"
'''

import traceback
import ssl as ssl_lib
import socket
import subprocess
import re
from datetime import datetime

try:
    from pymongo import MongoClient
    from pymongo.errors import (
        OperationFailure,
        ConnectionFailure,
        ServerSelectionTimeoutError,
        ConfigurationError
    )
    HAS_PYMONGO = True
    PYMONGO_IMP_ERR = None
except ImportError:
    HAS_PYMONGO = False
    PYMONGO_IMP_ERR = traceback.format_exc()

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


class MongoDBStateDetector:
    """Detect MongoDB configuration state"""

    def __init__(self, module):
        self.module = module
        self.host = module.params['host']
        self.port = module.params['port']
        self.admin_user = module.params.get('admin_user')
        self.admin_password = module.params.get('admin_password')
        self.login_database = module.params['login_database']
        self.connect_timeout = module.params['connect_timeout']
        self.ssl = module.params['ssl']
        self.ssl_cert_reqs = module.params['ssl_cert_reqs']
        self.hosts = module.params.get('hosts', [])
        self.service_name = module.params['service_name']
        self.check_service = module.params['check_service']
        self.fail_if_not_running = module.params['fail_if_not_running']
        self.check_local = module.params['check_local']

        # Initialize with proper defaults
        self.result = {
            'changed': False,
            'mongodb_running': False,
            'port_open': False,
            'connection_host': '',
            'bind_ip': '',
            'service_running': False,
            'service_enabled': False,
            'service_state': '',
            'auth_enabled': False,
            'auth_valid': False,
            'tls_enabled': False,
            'tls_mode': '',
            'tls_certificate_key_file': '',
            'tls_ca_file': '',
            'replication_enabled': False,
            'replica_set_name': '',
            'primary_host': self.host,
            'primary_port': self.port,
            'is_primary': False,
            'mongodb_version': '',
            'members': [],
            'member_count': 0,
            'healthy_members': 0,
            'connection_successful': False,
            'error': '',
        }

    def get_mongodb_config(self):
        """Read MongoDB configuration file and extract relevant settings"""
        config_paths = [
            '/etc/mongod.conf',
            '/etc/mongodb.conf',
            '/usr/local/etc/mongod.conf'
        ]

        config_data = {
            'bind_ip': '',
            'tls_enabled': False,
            'tls_mode': '',
            'tls_certificate_key_file': '',
            'tls_ca_file': '',
        }

        for config_path in config_paths:
            try:
                with open(config_path, 'r') as f:
                    content = f.read()

                    # Extract bindIp
                    match = re.search(r'bindIp:\s*([^\n]+)', content)
                    if match:
                        config_data['bind_ip'] = match.group(1).strip()

                    # Check for TLS/SSL settings (new style - net.tls)
                    tls_mode_match = re.search(r'tls:\s*\n\s*mode:\s*([^\n]+)', content)
                    if tls_mode_match:
                        tls_mode = tls_mode_match.group(1).strip()
                        config_data['tls_enabled'] = tls_mode in ['allowTLS', 'preferTLS', 'requireTLS']
                        config_data['tls_mode'] = tls_mode

                    # Check for old style SSL settings (net.ssl)
                    ssl_mode_match = re.search(r'ssl:\s*\n\s*mode:\s*([^\n]+)', content)
                    if ssl_mode_match and not config_data['tls_enabled']:
                        ssl_mode = ssl_mode_match.group(1).strip()
                        config_data['tls_enabled'] = ssl_mode in ['allowSSL', 'preferSSL', 'requireSSL']
                        config_data['tls_mode'] = ssl_mode

                    # TLS certificate file
                    cert_match = re.search(r'certificateKeyFile:\s*([^\n]+)', content)
                    if cert_match:
                        config_data['tls_certificate_key_file'] = cert_match.group(1).strip()

                    # TLS CA file
                    ca_match = re.search(r'CAFile:\s*([^\n]+)', content)
                    if ca_match:
                        config_data['tls_ca_file'] = ca_match.group(1).strip()

                    # If we found config, break
                    if config_data['bind_ip'] or config_data['tls_enabled']:
                        break

            except (FileNotFoundError, PermissionError):
                continue

        return config_data

    def check_tls_from_server(self, client):
        """Check TLS status from server's perspective"""
        try:
            # Get server status
            server_status = client.admin.command('serverStatus')

            # Check if there's connection info
            if 'connections' in server_status:
                # In newer versions, can check connection.tls
                pass

            # Try to get command line opts to see TLS settings
            try:
                cmd_line_opts = client.admin.command('getCmdLineOpts')
                parsed = cmd_line_opts.get('parsed', {})

                # Check net.tls settings
                if 'net' in parsed:
                    net_config = parsed['net']

                    # Check new TLS style
                    if 'tls' in net_config:
                        tls_config = net_config['tls']
                        if 'mode' in tls_config:
                            mode = tls_config['mode']
                            self.result['tls_enabled'] = mode in ['allowTLS', 'preferTLS', 'requireTLS']
                            self.result['tls_mode'] = mode
                        if 'certificateKeyFile' in tls_config:
                            self.result['tls_certificate_key_file'] = tls_config['certificateKeyFile']
                        if 'CAFile' in tls_config:
                            self.result['tls_ca_file'] = tls_config['CAFile']

                    # Check old SSL style
                    elif 'ssl' in net_config:
                        ssl_config = net_config['ssl']
                        if 'mode' in ssl_config:
                            mode = ssl_config['mode']
                            self.result['tls_enabled'] = mode in ['allowSSL', 'preferSSL', 'requireSSL']
                            self.result['tls_mode'] = mode
                        if 'PEMKeyFile' in ssl_config:
                            self.result['tls_certificate_key_file'] = ssl_config['PEMKeyFile']
                        if 'CAFile' in ssl_config:
                            self.result['tls_ca_file'] = ssl_config['CAFile']

            except OperationFailure:
                # Not authorized to run getCmdLineOpts
                pass

        except Exception as e:
            self.module.warn(f"Could not check TLS status from server: {str(e)}")

    def detect_tls_config(self):
        """Detect TLS configuration from config file"""
        config = self.get_mongodb_config()

        # Update bind_ip
        if config['bind_ip']:
            self.result['bind_ip'] = config['bind_ip']

        # Update TLS settings from config
        if config['tls_enabled']:
            self.result['tls_enabled'] = True
            self.result['tls_mode'] = config['tls_mode']
            self.result['tls_certificate_key_file'] = config['tls_certificate_key_file']
            self.result['tls_ca_file'] = config['tls_ca_file']

    def check_service_status(self):
        """Check if MongoDB service is running via systemd"""
        if not self.check_service:
            return None

        try:
            # Check if service is active
            result = subprocess.run(
                ['systemctl', 'is-active', self.service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            service_active = result.returncode == 0
            service_state = result.stdout.strip() if result.stdout else ''

            # Check if service is enabled
            result = subprocess.run(
                ['systemctl', 'is-enabled', self.service_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            service_enabled = result.returncode == 0

            self.result['service_running'] = service_active
            self.result['service_enabled'] = service_enabled
            self.result['service_state'] = service_state

            return service_active

        except FileNotFoundError:
            self.module.warn("systemctl not found - skipping service check")
            return None
        except subprocess.TimeoutExpired:
            self.module.warn("systemctl command timed out")
            return None
        except Exception as e:
            self.module.warn(f"Could not check service status: {str(e)}")
            return None

    def check_port_open(self, host, port):
        """Check if a specific host:port is accessible"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)

        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except (socket.gaierror, socket.timeout, OSError):
            return False
        finally:
            sock.close()

    def find_accessible_host(self):
        """
        Find which host MongoDB is actually accessible on.
        Tries: configured host, localhost, 127.0.0.1, bind IP from config
        """
        # Detect TLS config first to get bind_ip
        self.detect_tls_config()

        # Build list of hosts to try
        hosts_to_try = [self.host]

        if self.check_local:
            # Add localhost variants if not already the configured host
            if self.host not in ['localhost', '127.0.0.1']:
                hosts_to_try.extend(['localhost', '127.0.0.1'])

            # Add bind IP if found and different
            bind_ip = self.result.get('bind_ip', '')
            if bind_ip and bind_ip not in hosts_to_try:
                # Handle multiple bind IPs (comma-separated)
                for ip in bind_ip.split(','):
                    ip = ip.strip()
                    if ip and ip not in hosts_to_try:
                        hosts_to_try.append(ip)

        # Try each host
        accessible_hosts = []
        for test_host in hosts_to_try:
            if self.check_port_open(test_host, self.port):
                accessible_hosts.append(test_host)

        if accessible_hosts:
            # Prefer localhost/127.0.0.1 for local connections
            if 'localhost' in accessible_hosts:
                return 'localhost', True
            elif '127.0.0.1' in accessible_hosts:
                return '127.0.0.1', True
            else:
                return accessible_hosts[0], True

        # Nothing accessible
        self.result['port_open'] = False
        return '', False

    def is_mongodb_running(self):
        """
        Determine if MongoDB is running by checking:
        1. Systemd service status (if applicable)
        2. Port accessibility on various hosts
        3. Basic MongoDB ping
        """
        # Check systemd service
        service_running = self.check_service_status()

        # Find accessible host
        accessible_host, port_open = self.find_accessible_host()

        if not port_open:
            self.result['mongodb_running'] = False
            self.result['port_open'] = False
            return False

        self.result['port_open'] = True
        self.result['connection_host'] = accessible_host

        # Determine if we should try TLS connection
        use_tls = self.ssl or self.result.get('tls_enabled', False)

        # Try a quick MongoDB ping on the accessible host
        try:
            connection_params = {
                'host': accessible_host,
                'port': self.port,
                'serverSelectionTimeoutMS': 3000,
                'connectTimeoutMS': 3000,
            }

            # Add TLS if detected or configured
            if use_tls:
                connection_params['tls'] = True
                connection_params['tlsAllowInvalidCertificates'] = True  # For initial connection test

            client = MongoClient(**connection_params)
            client.admin.command('ping')
            client.close()
            self.result['mongodb_running'] = True
            # Update the host to use for further connections
            self.host = accessible_host
            return True
        except Exception as e:
            # If TLS failed, try without TLS
            if use_tls:
                try:
                    client = MongoClient(
                        host=accessible_host,
                        port=self.port,
                        serverSelectionTimeoutMS=3000,
                        connectTimeoutMS=3000,
                    )
                    client.admin.command('ping')
                    client.close()
                    self.result['mongodb_running'] = True
                    self.result['tls_enabled'] = False  # Correct the TLS detection
                    self.host = accessible_host
                    return True
                except Exception:
                    pass

            self.result['mongodb_running'] = False
            self.result['error'] = f"Port open but MongoDB not responding: {str(e)}"
            return False

    def get_ssl_context(self):
        """Create SSL context if SSL is enabled"""
        # Use detected TLS status or explicit SSL parameter
        use_tls = self.ssl or self.result.get('tls_enabled', False)

        if not use_tls:
            return None

        cert_reqs_map = {
            'CERT_NONE': ssl_lib.CERT_NONE,
            'CERT_OPTIONAL': ssl_lib.CERT_OPTIONAL,
            'CERT_REQUIRED': ssl_lib.CERT_REQUIRED
        }

        return {
            'tls': True,
            'tlsAllowInvalidCertificates': True,  # Be permissive for state detection
        }

    def connect(self, host=None, port=None, username=None, password=None, auth_db=None):
        """Create MongoDB connection"""
        host = host or self.host
        port = port or self.port

        connection_params = {
            'host': host,
            'port': port,
            'serverSelectionTimeoutMS': self.connect_timeout,
            'connectTimeoutMS': self.connect_timeout,
            'socketTimeoutMS': self.connect_timeout,
        }

        # Add SSL if configured or detected
        ssl_params = self.get_ssl_context()
        if ssl_params:
            connection_params.update(ssl_params)

        # Add authentication if provided
        if username and password:
            connection_params['username'] = username
            connection_params['password'] = password
            connection_params['authSource'] = auth_db or self.login_database

        try:
            client = MongoClient(**connection_params)
            # Force connection
            client.admin.command('ping')
            return client, None
        except Exception as e:
            return None, str(e)

    def check_auth_status(self):
        """Check if authentication is enabled"""
        # Try without auth first
        client, error = self.connect()

        if client:
            try:
                # Try a command that requires auth if enabled
                client.admin.command('listDatabases')
                self.result['auth_enabled'] = False
                self.result['connection_successful'] = True

                # Now that we have a connection, check TLS from server side
                self.check_tls_from_server(client)

                return client
            except OperationFailure as e:
                if 'unauthorized' in str(e).lower() or 'authentication' in str(e).lower():
                    self.result['auth_enabled'] = True
                else:
                    client.close()
                    self.module.fail_json(
                        msg=f"MongoDB error: {str(e)}",
                        **self.result
                    )
            finally:
                if self.result['auth_enabled']:
                    client.close()

        # If auth is required, try with credentials
        if self.result['auth_enabled'] and self.admin_user and self.admin_password:
            client, error = self.connect(
                username=self.admin_user,
                password=self.admin_password,
                auth_db=self.login_database
            )

            if client:
                try:
                    client.admin.command('ping')
                    self.result['auth_valid'] = True
                    self.result['connection_successful'] = True

                    # Check TLS from server side
                    self.check_tls_from_server(client)

                    return client
                except Exception as e:
                    self.result['auth_valid'] = False
                    self.module.fail_json(
                        msg=f"Authentication failed: {str(e)}",
                        **self.result
                    )
            else:
                self.result['auth_valid'] = False
                self.module.fail_json(
                    msg=f"Cannot connect with provided credentials: {error}",
                    **self.result
                )

        # No valid connection
        if not self.result['connection_successful']:
            error_msg = "Cannot connect to MongoDB."
            if self.result['auth_enabled']:
                error_msg += " Authentication is enabled but no admin credentials provided."
            self.module.fail_json(
                msg=error_msg,
                **self.result
            )

        return None

    def get_version(self, client):
        """Get MongoDB version"""
        try:
            build_info = client.admin.command('buildInfo')
            self.result['mongodb_version'] = build_info.get('version', '')
        except Exception as e:
            self.module.warn(f"Could not get MongoDB version: {str(e)}")
            self.result['mongodb_version'] = ''

    def check_replication(self, client):
        """Check if MongoDB is a replica set and get detailed member info"""
        try:
            is_master = client.admin.command('isMaster')

            # Check if part of replica set
            if 'setName' in is_master:
                self.result['replication_enabled'] = True
                self.result['replica_set_name'] = is_master.get('setName', '')
                self.result['is_primary'] = is_master.get('ismaster', False)

                # Get primary host
                if 'primary' in is_master:
                    primary_parts = is_master['primary'].split(':')
                    self.result['primary_host'] = primary_parts[0]
                    if len(primary_parts) > 1:
                        self.result['primary_port'] = int(primary_parts[1])

                # Get detailed replica set status
                try:
                    rs_status = client.admin.command('replSetGetStatus')
                    rs_config = None

                    # Try to get replica set config for additional details
                    try:
                        rs_config = client.admin.command('replSetGetConfig')
                    except OperationFailure:
                        pass  # Not primary or not authorized

                    members = []
                    primary_optime = None

                    # Find primary optime for lag calculation
                    for member in rs_status.get('members', []):
                        if member.get('stateStr') == 'PRIMARY':
                            primary_optime = member.get('optimeDate')
                            break

                    # Process each member
                    for member in rs_status.get('members', []):
                        name = member.get('name', '')
                        host_parts = name.split(':')

                        # Get member config if available
                        member_config = None
                        if rs_config and 'config' in rs_config:
                            for cfg_member in rs_config['config'].get('members', []):
                                if cfg_member.get('host') == name:
                                    member_config = cfg_member
                                    break

                        # Calculate replication lag
                        replication_lag = 0
                        if primary_optime and member.get('optimeDate'):
                            try:
                                lag_delta = primary_optime - member.get('optimeDate')
                                replication_lag = int(lag_delta.total_seconds())
                            except:
                                replication_lag = 0

                        # Determine member role
                        state_str = member.get('stateStr', 'UNKNOWN')
                        is_arbiter = (member_config and member_config.get('arbiterOnly', False)) or state_str == 'ARBITER'

                        member_info = {
                            'name': name,
                            'host': host_parts[0] if host_parts else name,
                            'port': int(host_parts[1]) if len(host_parts) > 1 else 27017,
                            'state': member.get('state', 0),
                            'state_str': state_str,
                            'health': member.get('health', 0),
                            'uptime': member.get('uptime', 0),
                            'optime': str(member.get('optimeDate', '')),
                            'is_self': member.get('self', False),
                            'is_primary': state_str == 'PRIMARY',
                            'is_secondary': state_str == 'SECONDARY',
                            'is_arbiter': is_arbiter,
                            'replication_lag': replication_lag,
                        }

                        # Add optional fields if available
                        if 'lastHeartbeat' in member:
                            member_info['last_heartbeat'] = str(member['lastHeartbeat'])
                        if 'lastHeartbeatRecv' in member:
                            member_info['last_heartbeat_recv'] = str(member['lastHeartbeatRecv'])
                        if 'pingMs' in member:
                            member_info['ping_ms'] = member['pingMs']
                        if 'syncSourceHost' in member:
                            member_info['sync_source'] = member.get('syncSourceHost', '')

                        # Add config details if available
                        if member_config:
                            member_info['priority'] = member_config.get('priority', 1)
                            member_info['votes'] = member_config.get('votes', 1)
                            member_info['hidden'] = member_config.get('hidden', False)

                        members.append(member_info)

                    self.result['members'] = members
                    self.result['member_count'] = len(members)
                    self.result['healthy_members'] = sum(1 for m in members if m['health'] == 1)

                except OperationFailure as e:
                    # Not authorized or not primary - get basic member info from isMaster
                    self.module.warn(f"Could not get detailed replica set status: {str(e)}")

                    # Fallback to basic info from isMaster
                    basic_members = []

                    # Add hosts
                    for host in is_master.get('hosts', []):
                        host_parts = host.split(':')
                        basic_members.append({
                            'name': host,
                            'host': host_parts[0],
                            'port': int(host_parts[1]) if len(host_parts) > 1 else 27017,
                            'state_str': 'PRIMARY' if host == is_master.get('primary') else 'SECONDARY',
                            'is_primary': host == is_master.get('primary'),
                            'is_secondary': host != is_master.get('primary'),
                            'is_arbiter': False,
                        })

                    # Add arbiters
                    for arbiter in is_master.get('arbiters', []):
                        arbiter_parts = arbiter.split(':')
                        basic_members.append({
                            'name': arbiter,
                            'host': arbiter_parts[0],
                            'port': int(arbiter_parts[1]) if len(arbiter_parts) > 1 else 27017,
                            'state_str': 'ARBITER',
                            'is_primary': False,
                            'is_secondary': False,
                            'is_arbiter': True,
                        })

                    if basic_members:
                        self.result['members'] = basic_members
                        self.result['member_count'] = len(basic_members)

            else:
                # Standalone MongoDB
                self.result['replication_enabled'] = False
                self.result['is_primary'] = True
                self.result['primary_host'] = self.host
                self.result['primary_port'] = self.port
                self.result['members'] = []
                self.result['member_count'] = 0

        except Exception as e:
            self.module.warn(f"Could not check replication status: {str(e)}")

    def find_primary_from_hosts(self):
        """Check multiple hosts to find the primary"""
        if not self.hosts:
            return

        for host in self.hosts:
            try:
                if self.admin_user and self.admin_password:
                    client, error = self.connect(
                        host=host,
                        port=self.port,
                        username=self.admin_user,
                        password=self.admin_password
                    )
                else:
                    client, error = self.connect(host=host, port=self.port)

                if client:
                    is_master = client.admin.command('isMaster')
                    if is_master.get('ismaster', False):
                        self.result['primary_host'] = host
                        client.close()
                        break
                    client.close()
            except Exception:
                continue

    def detect(self):
        """Main detection logic"""
        # First check if MongoDB is running
        if not self.is_mongodb_running():
            error_msg = "MongoDB is not running"

            # Add helpful context
            if self.result['service_running']:
                error_msg += f" (systemd service is active, but "
                if not self.result['port_open']:
                    error_msg += f"port {self.port} is not accessible. "
                    error_msg += f"Check MongoDB bind_ip configuration in /etc/mongod.conf)"
                else:
                    error_msg += "not responding to connections)"
            elif self.result['service_state']:
                error_msg += f" (service state: {self.result['service_state']})"

            self.result['error'] = error_msg

            if self.fail_if_not_running:
                self.module.fail_json(msg=error_msg, **self.result)
            else:
                return self.result

        # MongoDB is running, proceed with full detection
        client = self.check_auth_status()

        if not client:
            return self.result

        try:
            # Get MongoDB version
            self.get_version(client)

            # Check replication status and get member details
            self.check_replication(client)

            # If we have multiple hosts, try to find primary
            if self.result['replication_enabled'] and self.hosts:
                self.find_primary_from_hosts()

        finally:
            client.close()

        return self.result


def main():
    module_args = dict(
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=27017),
        admin_user=dict(type='str', required=False, no_log=False),
        admin_password=dict(type='str', required=False, no_log=True),
        login_database=dict(type='str', default='admin'),
        connect_timeout=dict(type='int', default=5000),
        ssl=dict(type='bool', default=False),
        ssl_cert_reqs=dict(
            type='str',
            default='CERT_REQUIRED',
            choices=['CERT_NONE', 'CERT_OPTIONAL', 'CERT_REQUIRED']
        ),
        hosts=dict(type='list', elements='str', required=False),
        service_name=dict(type='str', default='mongod'),
        check_service=dict(type='bool', default=True),
        fail_if_not_running=dict(type='bool', default=False),
        check_local=dict(type='bool', default=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_PYMONGO:
        module.fail_json(
            msg=missing_required_lib('pymongo'),
            exception=PYMONGO_IMP_ERR
        )

    detector = MongoDBStateDetector(module)
    result = detector.detect()

    module.exit_json(**result)


if __name__ == '__main__':
    main()