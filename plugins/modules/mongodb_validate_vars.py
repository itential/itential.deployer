#!/usr/bin/python

# Copyright (c) 2024, Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mongodb_validate_vars

short_description: Inspect facts and inventory variables and fails if misconfigured

version_added: "3.0.0"

description: This module will inspect the gathered facts and other inventory values to determine
    if the Itential Ansible Deployer has been properly configured.

options:
    platform_release:
        description: The Itential Platform version that will be installed.
        required: false
        type: float
    mongodb_version:
        description: The MongoDB version that will be installed.
        required: false
        type: float
    mongodb_packages:
        description: The list of MongoDB packages that will be installed.
        required: false
        type: list
    mongodb_python_packages:
        description: The list of MongoDB python packages that will be installed.
        required: false
        type: list

author:
    - Steven Schattenberg (@steven-schattenberg-itential)
'''

EXAMPLES = r'''
- name: Validate vars for MongoDB
  itential.deployer.mongodb_validate_vars:
    platform_release: "{{ platform_release | default(omit) }}"
    mongodb_version: "{{ mongodb_version | default(omit) }}"
    mongodb_packages: "{{ mongodb_packages | default(omit) }}"
    mongodb_python_packages: "{{ mongodb_python_packages | default(omit) }}"
  register: mongodb_validate
'''

RETURN = r'''
override_defaults:
    description: Are the defaults going to be used
    type: bool
    returned: always
    sample: false
valid:
    description: Are the variables provided valid
    type: bool
    returned: always
    sample: false
'''