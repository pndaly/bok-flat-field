#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +
# import(s)
# -
from astropy.time import Time
from flask import Flask
from flask import render_template
from datetime import datetime
from datetime import timedelta
from threading import Lock
from threading import Thread
from typing import Any

import argparse
import logging
import logging.config
import math
import os
import socket
import urllib.request


# +
# __doc__
# -
__doc__ = """ 
    Execute:
        FLASK_DEBUG=True FLASK_ENV=Development FLASK_APP=${BFF_SRC}/bok-flat-field.py flask run
    CLI:
        echo BOK90 BFF 123 COMMAND UBAND ON    | nc -w 5  10.30.3.41 5750
        echo BOK90 BFF 123 COMMAND UBAND OFF   | nc -w 5  10.30.3.41 5750
        echo BOK90 BFF 123 COMMAND HALOGEN ON  | nc -w 5  10.30.3.41 5750
        echo BOK90 BFF 123 COMMAND HALOGEN OFF | nc -w 5  10.30.3.41 5750
        echo BOK90 BFF 123 COMMAND ALL ON      | nc -w 5  10.30.3.41 5750
        echo BOK90 BFF 123 COMMAND ALL OFF     | nc -w 5  10.30.3.41 5750
        echo BOK90 BFF 123 REQUEST ALL         | nc -w 5  10.30.3.41 5750
    Route(s):
        /halogen/on
        /halogen/off
        /uband/on
        /uband/off
        /all/on
        /all/off
        /status
"""


# +
# constant(s)
# -
FALSE_VALUES = [0, False, '0', 'false', 'f', 'FALSE', 'F']
BFF_APP_HOST = os.getenv('BFF_APP_HOST', 'localhost')
BFF_APP_PORT = os.getenv('BFF_APP_PORT', 5096)
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
ISO_PATTERN = '[0-9]{4}-[0-9]{2}-[0-9]{2}[ T?][0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}'
LOG_CLR_FMT = '%(log_color)s%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s line:%(lineno)-5d Message: %(message)s'
LOG_CSL_FMT = '%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s line:%(lineno)-5d Message: %(message)s'
LOG_FIL_FMT = '%(asctime)-20s %(levelname)-9s %(filename)-15s %(funcName)-15s line:%(lineno)-5d Message: %(message)s'
LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
MAX_BYTES = 9223372036854775807
NG_COMMANDS = {
    "halogen_on":  "BOK90 FLATFIELD 123 COMMAND HALOGEN ON",
    "halogen_off": "BOK90 FLATFIELD 123 COMMAND HALOGEN OFF",
    "uband_on":    "BOK90 FLATFIELD 123 COMMAND UBAND ON",
    "uband_off":   "BOK90 FLATFIELD 123 COMMAND UBAND OFF",
    "all_on":      "BOK90 FLATFIELD 123 COMMAND ALL ON",
    "all_off":     "BOK90 FLATFIELD 123 COMMAND ALL OFF",
    "status":      "BOK90 FLATFIELD 123 REQUEST ALL"
}
NG_LEN = 256
NG_PORT = 5750
NG_SERVER = '10.30.3.41'
NG_TIMEOUT = 5.0
TRUE_VALUES = [1, True, '1', 'true', 't', 'TRUE', 'T']


# +
# function(s)
# -
def get_isot(ndays: float = 0.0) -> str:
    return f'{(datetime.now() + timedelta(days=ndays)).isoformat()}'

def get_utc(ndays: float = 0.0) -> str:
    return f'{(datetime.utcnow() + timedelta(days=ndays)).isoformat()}'


# +
# class: bffLogger() inherits from the object class
# -
class bffLogger(object):

    # +
    # method: __init__
    # -
    def __init__(self, name: str = '', level: str = LOG_LEVELS[0]):

        # get arguments(s)
        self.name = name
        self.level = level

        # define some variables and initialize them
        self.__msg = None
        self.__logdir = f'{os.getenv("BFF_LOG", os.getcwd())}'
        if not os.path.exists(self.__logdir) or not os.access(self.__logdir, os.W_OK):
            self.__logdir = os.getcwd()
        self.__logfile = f'{self.__logdir}/{self.__name}.log'

        # logger dictionary
        bff_dictionary = {

            # logging version
            'version': 1,

            # do not disable any existing loggers
            'disable_existing_loggers': False,

            # use the same formatter for everything
            'formatters': {
                'bffColoredFormatter': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': LOG_CLR_FMT,
                    'log_colors': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'white,bg_red',
                    }
                },
                'bffConsoleFormatter': {
                    'format': LOG_CSL_FMT
                },
                'bffFileFormatter': {
                    'format': LOG_FIL_FMT
                }
            },

            # define file and console handlers
            'handlers': {
                'colored': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'bffColoredFormatter',
                    'level': self.__level,
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'bffConsoleFormatter',
                    'level': self.__level,
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'backupCount': 10,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'bffFileFormatter',
                    'filename': self.__logfile,
                    'level': self.__level,
                    'maxBytes': MAX_BYTES
                }
            },

            # make this logger use file and console handlers
            'loggers': {
                self.__name: {
                    'handlers': ['colored', 'file'],
                    'level': self.__level,
                    'propagate': True
                }
            }
        }

        # configure logger
        logging.config.dictConfig(bff_dictionary)

        # get logger
        self.logger = logging.getLogger(self.__name)

    # +
    # Decorator(s)
    # -
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str = ''):
        self.__name = name if name.strip() != '' else os.getenv('USER')

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level: str = ''):
        self.__level = level.upper() if (level.strip() != '' and level.upper() in LOG_LEVELS) else LOG_LEVELS[0]


# +
# logger
# -
log = bffLogger('bok-flat-field').logger


# +
# class: SingletonMeta()
# -
class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


# +
# class: NgClient()
# -
class NgClient(metaclass=SingletonMeta):

    # +
    # method: __init__()
    # -
    def __init__(self, host: str = NG_SERVER, port: int = NG_PORT, timeout: float = NG_TIMEOUT, log: Any = None) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.log = log

        self.__commands = {
            'halogen_on': self.halogen_on,
            'halogen_off': self.halogen_off,
            'uband_on': self.uband_on,
            'uband_off': self.uband_off,
            'all_on': self.all_on,
            'all_off': self.all_off,
            'status': self.status
        }
        self.__command = ''
        self.__reset__()
        self.__dump__()

    # +
    # getter(s)
    # -
    @property
    def answer(self) -> str:
        return self.__answer

    @property
    def commands(self) -> dict:
        return self.__commands

    @property
    def error(self) -> str:
        return self.__error

    @property
    def host(self) -> str:
        return self.__host

    @property
    def log(self) -> str:
        return f"{self.__log}"

    @property
    def port(self) -> int:
        return self.__port

    @property
    def command(self) -> str:
        return self.__command

    @property
    def sock(self):
        return self.__sock

    @property
    def timeout(self) -> float:
        return self.__timeout

    # +
    # setters(s)
    # -
    @host.setter
    def host(self, host: str = NG_SERVER) -> None:
        self.__host = host if host.strip() != '' else NG_SERVER

    @log.setter
    def log(self, log: Any = None) -> None:
        self.__log = log

    @port.setter
    def port(self, port: int = NG_PORT) -> None:
        self.__port = port if port > 0 else NG_PORT

    @command.setter
    def command(self, command: str = NG_COMMANDS['status'])-> None:
        self.__command = command if command[:-1] in [_ for _ in NG_COMMANDS] else NG_COMMANDS['status']

    @timeout.setter
    def timeout(self, timeout: float = NG_TIMEOUT) -> None:
        self.__timeout = timeout if 0.0 < timeout < 60.0 else NG_TIMEOUT

    # +
    # method: __dump__()
    # -
    def __dump__(self):
        if self.__log:
            self.__log.debug(f"self.__answer  = {self.__answer}")
            self.__log.debug(f"self.__error   = {self.__error}")
            self.__log.debug(f"self.__host    = {self.__host}")
            self.__log.debug(f"self.__port    = {self.__port}")
            self.__log.debug(f"self.__timeout = {self.__timeout}")

    # +
    # method: __ping__()
    # -
    def __ping__(self) -> bool:
        _r = os.system(f"ping -c 1 {NG_SERVER}")
        return True if _r == 0 else False

    # +
    # method: __reset__()
    # -
    def __reset__(self) -> None:
        self.__answer = f""
        self.__error = f""
        self.__sock = None

    # +
    # method: connect()
    # -
    def connect(self) -> None:
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect((socket.gethostbyname(self.__host), self.__port))
            self.__sock.settimeout(self.__timeout)
        except Exception as _ec:
            self.__error = f'{_ec}'
            self.__sock = None

    # +
    # method: disconnect()
    # -
    def disconnect(self) -> None:
        if self.__sock is not None and hasattr(self.__sock, 'close'):
            try:
                self.__sock.close()
            except Exception as _ed:
                self.__error = f'{_ed}'
        self.__sock = None

    # +
    # method: talk()
    # -
    def talk(self) -> None:
        try:
            if self.__sock is not None and hasattr(self.__sock, 'send'):
                self.__sock.send(f'{self.__command}'.encode())
            if self.__sock is not None and hasattr(self.__sock, 'recv'):
                self.__answer = self.__sock.recv(NG_LEN)
                self.__answer = self.__answer.decode()
        except Exception as _et:
            self.__error = f'{_et}'

    # +
    # method: execute()
    # -
    def execute(self) -> None:
        self.connect()
        self.talk()
        self.disconnect()

    # +
    # method: __command__()
    # -
    def __command__(self, cmd: str = '') -> dict:
        # declare output
        _result = {"command": cmd, "answer": "", "result": "", "error": "", "MST": get_isot(0.0), "UTC": get_utc(0.0)}

        # check we know it
        if cmd.strip() not in [_v for _k, _v in NG_COMMANDS.items()]:
            _result = {**_result, **{"error": f"unknown command"}}
            if self.__log:
                self.__log.error(f"{_result}")
            return _result
        if self.__log:
            self.__log.info(f"{_result}")

        # reset and dump parameter(s)
        self.__command = f"{cmd}\n"
        self.__reset__()
        self.__dump__()

        # check machine is alive
        if not self.__ping__():
            _result = {**_result, **{"error": f"NG server {NG_SERVER} is down"}}
            if self.__log:
                self.__log.error(f"{_result}")
            return _result
        if self.__log:
            self.__log.info(f"{_result}")

        # execute the command/request
        self.execute()
        self.__dump__()

        # parse answer
        if self.__answer.strip() == '':
            _result = {**_result, **{"error": f"{NG_SERVER} no answer"}}
            if self.__log:
                self.__log.error(f"{_result}")
            return _result
        else:
            _result = {**_result, **{"answer": self.__answer}}
        if self.__log:
            self.__log.info(f"{_result}")

        # return
        try:
            _com = self.__command.strip().split()
            if self.__log:
                self.__log.info(f"_com={_com}")
            _ans = self.__answer.strip().split()
            if self.__log:
                self.__log.info(f"_ans={_ans}")
            if 'BOK90' in _com[0] and 'FLATFIELD' in _com[1] and '123' in _com[2] and 'COMMAND' in _com[3]:
                if 'UBAND' in _com[4] and 'ON' in _com[5] and 'OK' in _ans[3]:
                    _result = {**_result, **{"result": "UBAND ON"}}
                elif 'UBAND' in _com[4] and 'OFF' in _com[5] and 'OK' in _ans[3]:
                    _result = {**_result, **{"result": "UBAND OFF"}}
                elif 'HALOGEN' in _com[4] and 'ON' in _com[5] and 'OK' in _ans[3]:
                    _result = {**_result, **{"result": "HALOGEN ON"}}
                elif 'HALOGEN' in _com[4] and 'OFF' in _com[5] and 'OK' in _ans[3]:
                    _result = {**_result, **{"result": "HALOGEN OFF"}}
                elif 'ALL' in _com[4] and 'ON' in _com[5] and 'OK' in _ans[3]:
                    _result = {**_result, **{"result": "ALL ON"}}
                elif 'ALL' in _com[4] and 'OFF' in _com[5] and 'OK' in _ans[3]:
                    _result = {**_result, **{"result": "ALL OFF"}}
            else:
                _result = {**_result, **{"error": f"unknown error"}}
                if self.__log:
                    self.__log.error(f"{_result}")
        except Exception as _ie:
                _result = {**_result, **{"error": f"{_ie}"}}
                if self.__log:
                    self.__log.error(f"{_result}")
        if self.__log:
            self.__log.info(f"{_result}")
        return _result

    # +
    # method: __request__()
    # -
    def __request__(self, cmd: str = '') -> dict:
        # declare output
        _result = {"command": cmd, "answer": "", "result": "", "error": "", "MST": get_isot(0.0), "UTC": get_utc(0.0)}

        # check we know it
        if cmd.strip() not in [_v for _k, _v in NG_COMMANDS.items()]:
            _result = {**_result, **{"error": f"unknown request"}}
            if self.__log:
                self.__log.error(f"{_result}")
            return _result
        if self.__log:
            self.__log.info(f"{_result}")

        # reset and dump parameter(s)
        self.__command = f"{cmd}\n"
        self.__reset__()
        self.__dump__()

        # check machine is alive
        if not self.__ping__():
            _result = {**_result, **{"error": f"NG server {NG_SERVER} is down"}}
            if self.__log:
                self.__log.error(f"{_result}")
            return _result
        if self.__log:
            self.__log.info(f"{_result}")

        # execute the command/request
        self.execute()
        self.__dump__()

        # parse answer
        if self.__answer.strip() == '':
            _result = {**_result, **{"error": f"{NG_SERVER} no answer"}}
            if self.__log:
                self.__log.error(f"{_result}")
            return _result
        else:
            _result = {**_result, **{"answer": self.__answer}}
        if self.__log:
            self.__log.info(f"{_result}")

        # return
        try:
            _ans = self.__answer.strip().split()
            if 'BOK90' in _ans[0] and 'FLATFIELD' in _ans[1] and '123' in _ans[2]:
                # BOK90 FLATFIELD 123 0 0
                if '0' in _ans[3] and '0' in _ans[4]:
                    _result = {**_result, **{"result": "Uband OFF / Halogen OFF"}}
                # BOK90 FLATFIELD 123 1 0
                elif '1' in _ans[3] and '0' in _ans[4]:
                    _result = {**_result, **{"result": "Uband ON / Halogen OFF"}}
                # BOK90 FLATFIELD 123 0 1
                elif '0' in _ans[3] and '1' in _ans[4]:
                    _result = {**_result, **{"result": "Uband OFF / Halogen ON"}}
                # BOK90 FLATFIELD 123 1 1
                elif '1' in _ans[3] and '1' in _ans[4]:
                    _result = {**_result, **{"result": "Uband ON / Halogen ON"}}
            else:
                _result = {**_result, **{"error": f"unknown error"}}
                if self.__log:
                    self.__log.error(f"{_result}")
        except Exception as _ie:
                _result = {**_result, **{"error": f"{_ie}"}}
                if self.__log:
                    self.__log.error(f"{_result}")
        if self.__log:
            self.__log.info(f"{_result}")
        return _result


    # +
    # method(s)
    # -
    def halogen_on(self) -> dict:
        return self.__command__(cmd=f"{NG_COMMANDS.get('halogen_on', '')}")
    def halogen_off(self) -> dict:
        return self.__command__(cmd=f"{NG_COMMANDS.get('halogen_off', '')}")
    def uband_on(self) -> dict:
        return self.__command__(cmd=f"{NG_COMMANDS.get('uband_on', '')}")
    def uband_off(self) -> dict:
        return self.__command__(cmd=f"{NG_COMMANDS.get('uband_off', '')}")
    def all_on(self) -> dict:
        return self.__command__(cmd=f"{NG_COMMANDS.get('all_on', '')}")
    def all_off(self) -> dict:
        return self.__command__(cmd=f"{NG_COMMANDS.get('all_off', '')}")
    def status(self) -> dict:
        return self.__request__(cmd=f"{NG_COMMANDS.get('status', '')}")


# +
# initialization
# -
app = Flask(__name__)
ng_client = NgClient(host=NG_SERVER, port=NG_PORT, timeout=NG_TIMEOUT, log=log)
log.debug(f"BFF_APP_HOST = {BFF_APP_HOST}")
log.debug(f"BFF_APP_PORT = {BFF_APP_PORT}")
log.debug(f'ng_client={ng_client}')
log.debug(f"NG_SERVER = {NG_SERVER}")
log.debug(f"NG_PORT = {NG_PORT}")
log.debug(f"NG_COMMANDS = {NG_COMMANDS}")


# +
# route(s)
# -
@app.route('/routes')
def supported():
    return render_template('routes.html', name="Route(s)", routes=['/halogen/on', '/halogen/off', '/uband/on', '/uband/off', '/all/on', '/all/off', '/status', '/routes'])


# +
# route(s)
# -
@app.route('/halogen/on')
def halogen_on():
    return render_template('status.html', name="halogen_on", details=ng_client.commands.get('halogen_on')())

@app.route('/halogen/off')
def halogen_off():
    return render_template('status.html', name="halogen_off", details=ng_client.commands.get('halogen_off')())

@app.route('/uband/on')
def uband_on():
    return render_template('status.html', name="uband_on", details=ng_client.commands.get('uband_on')())

@app.route('/uband/off')
def uband_off():
    return render_template('status.html', name="uband_off", details=ng_client.commands.get('uband_off')())

@app.route('/all/on')
def all_on():
    return render_template('status.html', name="all_on", details=ng_client.commands.get('all_on')())

@app.route('/all/off')
def all_off():
    return render_template('status.html', name="all_off", details=ng_client.commands.get('all_off')())

@app.route('/')
@app.route('/status')
def status():
    return render_template('status.html', name="status", details=ng_client.commands.get('status')())

# +
# main()
# -
if __name__ == '__main__':
    app.run(host=BFF_APP_HOST, port=BFF_APP_PORT, threaded=True, debug=False)
