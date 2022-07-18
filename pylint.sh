#!/usr/bin/env bash

if [[ -z "${NETORG_HOME}" ]]; then
   echo "Please set NETORG_HOME environment variable before proceeding"
   exit 1
fi

source .venv/bin/activate 
pylint *.py
