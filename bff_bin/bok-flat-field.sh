#!/bin/sh
_src=${1:-$(pwd)}
source ${_src}/bff_etc/bok-flat-field.sh ${_src} prod

_command=${2:-"status"}
source ${BFF_BIN}/functions.sh

case $(echo ${_command} | tr '[A-Z]' '[a-z]') in
  start*)
    write_green "Execute: FLASK_DEBUG=True FLASK_ENV=Development FLASK_APP=${BFF_SRC}/bok-flat-field.py flask run"
    ;;
  stop*)
    _pid=$(ps -ef | pgrep -f 'python3' | pgrep  -f flask | grep -v grep)
    [[ ! -z "${_pid}" ]] && write_green "Execute: kill -9 ${_pid}" || write_red "bok-flat-field application is not running"
    ;;
  status*)
    _pid=$(pidof bok-flat-field)
    [[ -z "${_pid}" ]] && write_red "bok-flat-field application is not running"
    ;;
esac
