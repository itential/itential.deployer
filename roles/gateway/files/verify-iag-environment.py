#!/usr/bin/env python3

# This script will inspect various parts of the IAG environment returning
# some troubleshooting data. It is intended to be a simple test to verify the
# installation.

import os
import subprocess

# Get the list of user's environment variables
print("Gathering environment data...")
print(str(dict(os.environ, width=1)))

# Get the python configuration
print("Gathering python data...")
print(subprocess.run(["which","python3"], text=True, capture_output=True).stdout)
print(subprocess.run(["python3","--version"], text=True, capture_output=True).stdout)

# Get the ansible configuration
print("Gathering ansible data...")
print(subprocess.run(["ansible","--version"], text=True, capture_output=True).stdout)
print(subprocess.run(["ansible-galaxy","collection","list"], text=True, capture_output=True).stdout)

exit(0)
