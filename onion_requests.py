#!/usr/bin/env python2

# Blackhats.Today - PICKYONION
#

import requests
import stem
import os
from stem.util import term
from stem.process import launch_tor_with_config
from stem.control import Controller

class PICKYONION(object):

    def __init__(self, tor_socks_port=9050, tor_ctrl_port=9051, tor_ctrl_pass=None):
        self.tor_socks_port = tor_socks_port
        self.tor_ctrl_port = tor_ctrl_port
        self.tor_ctrl_pass = tor_ctrl_pass
        self.tor_controller = None
        self.tor_process = None
        self.tor_hidden_dir = None
        self.tor_hidden_address = None

        if not self._is_running():
            self.tor_process = self._start_tor()

        self.tor_controller = Controller.from_port(port=self.tor_ctrl_port)
        self.tor_controller.authenticate(self.tor_ctrl_pass)
        self.tor_hidden_dir = self.tor_controller.get_conf('DataDirectory')
        self.tor_session = requests.Session()
        self.tor_session.proxies.update({
            'http': 'socks5://localhost:%d' % (self.tor_socks_port),
            'https': 'socks5://localhost:%d' % (self.tor_socks_port),
        })

    def _start_tor(self):
        return launch_tor_with_config(
            config={
                'SocksPort': str(self.tor_socks_port),
                'ControlPort': str(self.tor_ctrl_port)
            },
            take_ownership=True,
            init_msg_handler=self.tor_bootstrap_messages,)

    def tor_bootstrap_messages(self, line):
        if 'Bootstrapped' in line:
            print(term.format(line, term.Color.GREEN))

    def _is_running(self):
        try:
            c = Controller.from_port(port=self.tor_ctrl_port)
            c.close()
            return True
        except: return False

    def start_hidden_service(self, tor_port=8080, local_port=8000, name='generated_name_here'):
        self.tor_hidden_dir = os.path.join(self.tor_controller.get_conf('DataDirectory', '/tmp'), name)
        r = self.tor_controller.create_ephemeral_hidden_service({tor_port: local_port}, await_publication=True)
        if r.service_id:
            self.tor_hidden_address = r.service_id
            return r.service_id
        else: return None

    def close(self):
        try:
            self.tor_session.close()
            self.tor_controller.close()
        except: pass
        if self.tor_process: self.tor_process.terminate()

    def reset_identity(self):
        self.tor_controller.signal(stem.Signal.NEWNYM)
        time.sleep(self.tor_controller.get_newnym_wait())

    def get_bytes_read(self):
        if self.tor_controller.get_info("traffic/read"):
            return self.tor_controller.get_info("traffic/read")

    def get_bytes_written(self):
        if self.tor_controller.get_info("traffic/written"):
            return self.tor_controller.get_info("traffic/written")

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

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()