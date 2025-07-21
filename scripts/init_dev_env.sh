#! /bin/bash

#
# This script is intended to be used by Itential engineers for setting up their Deployer
# development environments. It takes two arguments - a root directory and the URL of the
# Deployer Git repo. The Deployer collection will be cloned into the directory
# $ROOT_DIR/ansible_collections/itential/deployer. A default ansible.cfg will be created that
# points Ansible to the cloned Deployer collection. Users must be in the
# $ROOT_DIR/ansible_collections/itential/deployer directory when running the Deployer in order
# to guarantee the correct playbooks and roles are executed.
#
# Example usage:
#   $ sh init_dev_env.sh ~/deployer_workspace git@github.com:<USER>/deployer.git
#

if [ "$#" -ne 2 ]
then
  echo "Usage: $0 <ROOT_DIR> <DEPLOYER_GIT_REPO>"
  exit 1
fi

ROOT_DIR=$1
DEPLOYER_GIT_REPO=$2

echo "Root directory: "$ROOT_DIR
echo "Git repo: "$DEPLOYER_GIT_REPO

ITENTIAL_DIR=$ROOT_DIR/ansible_colllections/itential
DEPLOYER_DIR=$ITENTIAL_DIR/deployer

if [ ! -d $ITENTIAL_DIR ]; then
    echo "Creating itential collection directory: "$ITENTIAL_DIR
    mkdir -p $ITENTIAL_DIR
else
    echo "itential collection directory already exists!"
fi

cd $ITENTIAL_DIR

if [ ! -d $DEPLOYER_DIR ]; then
  echo "Cloning deployer git repo"
  git clone $DEPLOYER_GIT_REPO deployer
else
  echo "Deployer directory already exists!"
fi

if [ ! -f $DEPLOYER_DIR/ansible.cfg ]; then
    echo "Creating ansible.cfg"
    cd $DEPLOYER_DIR
    cat > ansible.cfg <<EOF
[defaults]
host_key_checking = False
collections_path=$ROOT_DIR:~/.ansible/collections
callbacks_enabled=profile_tasks
log_path = ./ansible.log
EOF
else
    echo "ansible.cfg already exists!"
fi
