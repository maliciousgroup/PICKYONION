#!/usr/bin/env python2

#
# Blackhats.Today - PICKY ONION
#

import requests
import time
import stem
from stem.util import term
from stem.process import launch_tor_with_config
from stem.control import Controller

class Picky_Onion(object):

    def __init__(self, tor_socks_port=9050, tor_ctrl_port=9051, tor_ctrl_pass=None):
        self.tor_socks_port = tor_socks_port
        self.tor_ctrl_port = tor_ctrl_port
        self.tor_ctrl_pass = tor_ctrl_pass
        self.tor_controller = None
        self.tor_process = None

        if not self._is_running():
            self.tor_process = self._start_tor()

        self.tor_controller = Controller.from_port(port=self.tor_ctrl_port)
        self.tor_controller.authenticate(self.tor_ctrl_pass)
        self.tor_session = requests.Session()
        self.tor_session.proxies.update({
            'http'  : 'socks5://localhost:%d' % (self.tor_socks_port),
            'https' : 'socks5://localhost:%d' % (self.tor_socks_port),
        })

    def _start_tor(self):
        return launch_tor_with_config(
            config={
                'SocksPort': str(self.tor_socks_port),
                'ControlPort': str(self.tor_ctrl_port)
            },
            take_ownership=True, init_msg_handler=self._print_bootstrap_lines,)

    def close(self):
        try:
            self.tor_session.close()
            self.tor_controller.close()
        except: pass

        if self.tor_process:
            self.tor_process.terminate()

    def reset_identity(self):
        self.tor_controller.signal(stem.Signal.NEWNYM)
        time.sleep(self.tor_controller.get_newnym_wait())

    def _print_bootstrap_lines(self, line):
        if 'Bootstrapped' in line:
            print(term.format(line, term.Color.GREEN))

    def _is_running(self):
        try:
            c = Controller.from_port(port=self.tor_ctrl_port)
            c.close()
            return True
        except:
            return False

    def get(self, *args, **kwargs):
        return self.tor_session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.tor_session.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.tor_session.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.tor_session.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.tor_session.delete(*args, **kwargs)
