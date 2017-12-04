#!/bin/bash

sql_file=streeTunes.sql

set -x

if [ $# -gt 0 ]; then
  case $1 in
    "remove")
      sql_file=remove_streeTunes.sql
      ;;
    *)
      echo "unknown command: $1"
      exit 1
  esac
fi

mysql -u root < ${sql_file}
