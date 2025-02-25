#!/usr/bin/python

# Copyright (c) 2024, Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.module_utils.common import yaml
from datetime import datetime

class ActionModule(ActionBase):

    _supports_check_mode = False
    _supports_async = False
    _requires_connection = False

    def run(self, tmp=None, task_vars=None):

        module_args = self._task.args.copy()

        result = dict(
            changed = False,
            valid = False,
            override_defaults = False
        )

        platform_release = module_args.get("platform_release")
        mongodb_version = module_args.get("mongodb_version")
        mongodb_packages = module_args.get("mongodb_packages")
        mongodb_python_packages = module_args.get("mongodb_python_packages")

        if platform_release:
            result["valid"] = True
        elif (mongodb_version and mongodb_packages and mongodb_python_packages):
            result["valid"] = True
            result["override_defaults"] = True
        else:
            raise AnsibleError("This is not a valid configuration of deployer! Either define " +
                "'platform_release' in all.vars or define each of these in the mongodb group to " +
                "override the default MongoDB version: 'mongodb_version', 'mongodb_packages', " +
                "'mongodb_python_packages'")

        return result