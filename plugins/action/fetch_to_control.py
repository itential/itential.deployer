#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Itential LLC
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: fetch_to_control
short_description: Fetch file from remote node to control node
description:
    - Fetches a file from the remote node to the control node
    - Creates destination directories if they don't exist
    - Replaces existing files on the control node
    - This is an action plugin that runs on the control node
    - Uses the slurp module internally to read files from remote nodes
version_added: "1.0.0"
options:
    src:
        description:
            - Path to file on remote node
        required: true
        type: str
    dest:
        description:
            - Destination path on control node (full path including filename)
        required: true
        type: str
author:
    - Steven Schattenberg (steven.schattenberg@itential.com)
notes:
    - This is an action plugin, not a regular module
    - It must be placed in plugins/action/ directory of your collection
    - Internally uses the slurp module to read files from remote nodes
'''

EXAMPLES = r'''
# Fetch a report file
- name: Fetch remote file
  fetch_to_control:
    src: /tmp/itential-reports/report.md
    dest: /tmp/itential-reports/report.md
'''

RETURN = r'''
src:
    description: Source path on remote node
    type: str
    returned: always
dest:
    description: Destination path on control node
    type: str
    returned: always
size:
    description: Size of the fetched file in bytes
    type: int
    returned: success
changed:
    description: Whether the file was fetched
    type: bool
    returned: always
'''

import os
import base64
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp

        # Get parameters
        src = self._task.args.get('src')
        dest = self._task.args.get('dest')

        # Validate required parameters
        if not src:
            raise AnsibleActionFail("'src' parameter is required")
        if not dest:
            raise AnsibleActionFail("'dest' parameter is required")

        # Expand paths
        dest = os.path.expanduser(dest)
        dest_dir = os.path.dirname(dest)

        # Create destination directory on control node if it doesn't exist
        if dest_dir and not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir, mode=0o755)
            except Exception as e:
                raise AnsibleActionFail(f"Failed to create destination directory {dest_dir}: {str(e)}")

        # Remove existing file on control node if it exists
        if os.path.exists(dest):
            try:
                os.remove(dest)
            except Exception as e:
                raise AnsibleActionFail(f"Failed to remove existing file {dest}: {str(e)}")

        # Use slurp module to read file from remote node
        slurp_result = self._execute_module(
            module_name='slurp',
            module_args={'src': src},
            task_vars=task_vars
        )

        # Check if slurp failed
        if slurp_result.get('failed'):
            raise AnsibleActionFail(f"Failed to read remote file {src}: {slurp_result.get('msg', 'Unknown error')}")

        # Get the base64 encoded content
        content = slurp_result.get('content', '')
        if not content:
            raise AnsibleActionFail(f"No content returned from remote file {src}")

        # Decode base64 content
        try:
            decoded_content = base64.b64decode(content)
        except Exception as e:
            raise AnsibleActionFail(f"Failed to decode file content: {str(e)}")

        # Write content to control node
        try:
            with open(dest, 'wb') as f:
                f.write(decoded_content)
        except Exception as e:
            raise AnsibleActionFail(f"Failed to write file to {dest}: {str(e)}")

        # Build result
        result.update({
            'changed': True,
            'src': src,
            'dest': dest,
            'size': len(decoded_content),
            'msg': f"File fetched from {src} to {dest}"
        })

        return result