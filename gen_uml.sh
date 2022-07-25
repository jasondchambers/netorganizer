#!/usr/bin/env bash

if [[ -z "${NETORG_HOME}" ]] ; then
   (>&2 echo "Please set NETORG_HOME environment variable before proceeding")
   exit 2
fi

dot -Tpng netorg.dot  > netorg.png
