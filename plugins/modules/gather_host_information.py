#!/usr/bin/python

# Copyright (c) 2026, Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: gather_host_information

short_description: Inspect facts and gather interesting data

version_added: "3.0.0"

description: This module will inspect the host facts and gather interesting data to be used in the
    verification and certification of environments.

author:
    - Steven Schattenberg (@steven-schattenberg-itential)
'''

EXAMPLES = r'''
- name: Gather standard facts
  itential.deployer.gather_host_information:
'''

RETURN = r'''
details:
    description: Details from the host
    type: object
    returned: always
    sample: false
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.facts.compat import ansible_facts

def build_disk_list(ansible_mounts):
    """Build simplified disk list from ansible_mounts data"""
    disk_list = []

    for item in ansible_mounts:
        if 'size_total' in item:
            disk_list.append({
                'mount': item['mount'],
                'size_gb': round(item['size_total'] / 1024 / 1024 / 1024, 2)
            })

    return disk_list

def build_interface_list(facts):
    """Build simplified interface information"""
    interfaces = []

    # Get list of all interfaces
    interface_names = facts.get('interfaces', [])

    for iface_name in interface_names:
        # Skip loopback
        if iface_name == 'lo':
            continue

        # Get the interface details
        iface_data = facts.get(iface_name, {})

        if not iface_data or not isinstance(iface_data, dict):
            continue

        interface_info = {
            'name': iface_name,
            'active': iface_data.get('active', False),
            'type': iface_data.get('type', 'unknown'),
            'ipv4': iface_data.get('ipv4', {}),
            'ipv6': iface_data.get('ipv6', [])
        }

        interfaces.append(interface_info)

    return interfaces

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict()

    # seed the result dict in the object
    result = dict(
        changed=False,
        details=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # Get the facts from the host
    facts = ansible_facts(module)

    # Gather OS information...
    result["os"] = {}
    result["os"]["distribution"] = facts.get("distribution", "unknown")
    result["os"]["distribution_version"] = facts.get("distribution_version", "unknown")
    result["os"]["os_family"] = facts.get("os_family", "unknown")
    result["os"]["kernel"] = facts.get("kernel", "unknown")
    result["os"]["architecture"] = facts.get("architecture", "unknown")
    result["os"]["hostname"] = facts.get("hostname", "unknown")
    result["os"]["fqdn"] = facts.get("fqdn", "unknown")

    # Gather hardware information...
    result["hardware"] = {}
    result["hardware"]["cpu"] = {}
    result["hardware"]["cpu"]["processor_count"] = facts.get("processor_count", 0)
    result["hardware"]["cpu"]["processor_cores"] = facts.get("processor_cores", 0)
    result["hardware"]["cpu"]["processor_vcpus"] = facts.get("processor_vcpus", 0)
    result["hardware"]["cpu"]["processor_threads_per_core"] = facts.get("processor_threads_per_core", 0)
    result["hardware"]["cpu"]["processor"] = facts.get("processor", [])
    result["hardware"]["memory"] = {}
    result["hardware"]["memory"]["memtotal_mb"] = facts.get("memtotal_mb", 0)
    result["hardware"]["memory"]["memfree_mb"] = facts.get("memfree_mb", 0)
    result["hardware"]["memory"]["swaptotal_mb"] = facts.get("swaptotal_mb", 0)
    result["hardware"]["disk"] = build_disk_list(facts.get("mounts", []))

    # Gather security information...
    result["security"] = {}
    result["security"]["selinux"] = facts.get("selinux", {"status": "not available"})

    # Is firewalld running?
    firewalld = facts.get('services', {}).get('firewalld.service')
    if firewalld:
        result["security"]["firewalld"] = firewalld

    # Gather networking information...
    result["networking"] = {}
    result["networking"]["interfaces"] = build_interface_list(facts)
    result["networking"]["default_ipv4"] = facts.get("default_ipv4", {})
    result["networking"]["default_ipv6"] = facts.get("default_ipv6", {})

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()