#!/usr/bin/python

# Copyright (c) 2024, Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mongodb_config_state

short_description: Inspect facts and determine the configuration state of MongoDB.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "3.0.0"

description: This module will inspect the configuration of MongoDB and report back
    with simple boolean values the state of the running MongoDB configuration. For
    example, it will provide boolean values on the state of replication and on the
    state of authorization.

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Steven Schattenberg (@steven-schattenberg-itential)
'''

EXAMPLES = r'''
# Pass in a message
- name: Determine MongoDB config state
  itential.deployer.mongodb_config_state:
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
replication_enabled:
    description: Is replication enabled, true or false
    type: bool
    returned: always
    sample: false
auth_enabled:
    description: Is auth enabled, true or false
    type: bool
    returned: always
    sample: false
primary:
    description: The name of the primary server
    type: str
    returned: always
    sample: "example.host.com"
members:
    description: The list of members in the replica set or empty list
    type: arr
    returned: always
    sample: ["example1.host.com", "example2.host.com", "example3.host.com"]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.facts.compat import ansible_facts
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from bson.json_util import dumps

def build_connection_string(args):
    return "mongodb://" + args["login_host"] + ":" + str(args["login_port"]) + "/" + args["login_database"]

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        login_database=dict(type='str', required=False, default='admin', no_log=False),
        login_host=dict(type='str', required=True, no_log=False),
        login_port=dict(type='int', required=False, default=27017, no_log=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        replication_enabled=False,
        auth_enabled=False,
        primary="",
        members=[]
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

    uri = build_connection_string(module.params)

    client = MongoClient(uri)
    database = client.get_database("admin")
    hello = database.command("hello")

    if "setName" in hello:
        result["replication_enabled"] = True
        result["primary"] = hello["primary"]
        result["members"] = hello["hosts"]

    try:
        user = database.command('usersInfo')
    except OperationFailure:
        result["auth_enabled"] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()