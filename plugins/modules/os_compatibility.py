#!/usr/bin/python

# Copyright (c) 2024, Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: os_compatibility

short_description: Inspect facts and determine if the host is compatible

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "3.0.0"

description: This module will inspect the host facts and determine if the host is compatible for
    installation of the Itential stack. The stack requires a dnf package manager and Redhat family
    of linux of specific major versions.

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Steven Schattenberg (@steven-schattenberg-itential)
'''

EXAMPLES = r'''
# Pass in a message
- name: Determine compatibility
  itential.deployer.os_compatibility:
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
compatible:
    description: Is this operating system compatible with the Itential platform
    type: bool
    returned: always
    sample: false
os_version:
    description: A normalized string representing the OS and major version
    type: str
    returned: always
    sample: 'RedHat8'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.facts.compat import ansible_facts

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict()

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        compatible=False,
        os_version="",
        os="",
        version=""
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
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

    # Normalize the distribution and major version
    result["os_version"] = facts["distribution"].lower() + "-" + facts["distribution_major_version"]
    result["os"] = facts["distribution"].lower()
    result["version"] = facts["distribution_major_version"]

    # If its a RedHat family of linux then set compatible to True
    if facts["os_family"].lower() == "redhat":
        if facts["distribution"].lower() == "redhat" or facts["distribution"].lower() == "rocky":
            if int(facts["distribution_major_version"]) >= 8:
                result["compatible"] = True
        if facts["distribution"].lower() == "amazon":
            if int(facts["distribution_major_version"]) >= 2023:
                result["compatible"] = True

    # Fail the module if this host is not compatible
    if result["compatible"] == False:
        module.fail_json(msg='This is not a supported OS family!', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()