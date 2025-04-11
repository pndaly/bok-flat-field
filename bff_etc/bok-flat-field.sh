#!/bin/sh


# +
# edit as you see fit
# -
export BFF_HOME=${1:-$(pwd)}
export BFF_TYPE=${2:-"prod"}
export BFF_APP_HOST=10.30.1.7
export BFF_APP_PORT=5096


# +
# env(s)
# -
export BFF_BIN=${BFF_HOME}/bff_bin
export BFF_ETC=${BFF_HOME}/bff_etc
export BFF_LOG=${BFF_HOME}/bff_log
export BFF_SRC=${BFF_HOME}/bff_src


# +
# PYTHONPATH
# -
export PYTHONPATH=${BFF_HOME}:${BFF_SRC}
