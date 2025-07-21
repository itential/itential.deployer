#! /bin/bash

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
