#!/usr/bin/env bash

if [[ -z "${NETORG_HOME}" ]]; then
   echo "Please set NETORG_HOME environment variable before proceeding"
   exit 1
fi

cd $NETORG_HOME
source .venv/bin/activate 
python3 -m unittest
