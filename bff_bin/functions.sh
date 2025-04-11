#!/bin/sh

function write_blue() {
  printf "\033[0;34m${1}\033[0m\n"
}

function write_blue_dh() {
  printf "\033[0;34m\033#3${1}\n\033#4${1}\033[0m\n"
}

function write_cyan() {
  printf "\033[0;36m${1}\033[0m\n"
}

function write_cyan_dh() {
  printf "\033[0;36m\033#3${1}\n\033#4${1}\033[0m\n"
}

function write_green() {
  printf "\033[0;32m${1}\033[0m\n"
}

function write_green_dh() {
  printf "\033[0;32m\033#3${1}\n\033#4${1}\033[0m\n"
}

function write_magenta() {
  printf "\033[0;35m${1}\033[0m\n"
}

function write_magenta_dh() {
  printf "\033[0;35m\033#3${1}\n\033#4${1}\033[0m\n"
}

function write_red() {
  printf "\033[0;31m${1}\033[0m\n"
}

function write_red_dh() {
  printf "\033[0;31m\033#3${1}\n\033#4${1}\033[0m\n"
}

function write_yellow() {
  printf "\033[0;33m${1}\033[0m\n"
}

function write_yellow_dh() {
  printf "\033[0;33m\033#3${1}\n\033#4${1}\033[0m\n"
}

function sha256sum() {
  openssl sha256 "$@" | awk '{print $2}'
}
