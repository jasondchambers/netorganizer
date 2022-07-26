#!/usr/bin/env bash

if [[ -z "${NETORG_HOME}" ]] ; then
   (>&2 echo "Please set NETORG_HOME environment variable before proceeding")
   exit 2
fi

set -eo pipefail

OS=`uname`
case $OS in
  'Linux')
    echo "Installing for Linux"
    apt update
    echo "Installing pip3"
    echo "==============="
    apt install -y python3-pip
    echo "Installing python3-venv"
    echo "======================="
    apt install -y python3-venv
    ;;
  'Darwin')
    echo "Installing for macOS"
    python3 -m pip install --upgrade pip
    ;;
esac

echo "Creating virtual environment"
echo "============================"
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

echo "Testing the installation"
echo "========================"
$NETORG_HOME/unittest.sh
