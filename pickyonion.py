#!/usr/bin/env python2

import SimpleHTTPServer
import SocketServer
import threading
import requests
import logging
import stem
import os
from time import sleep
from stem.util import term
from stem.control import Controller
from stem.process import launch_tor_with_config

# Setup Class
class PICKYONION(object):

    # Class Constructor
    def __init__(self, tor_socks_port=9050, tor_ctrl_port=9051, tor_ctrl_pass=None):

        self.tor_socks_port = tor_socks_port
        self.tor_ctrl_port = tor_ctrl_port
        self.tor_ctrl_pass = tor_ctrl_pass
        self.tor_process = None
        self.tor_session = None
        self.tor_data_dir = None
        self.tor_controller = None
        self.tor_hidden_dir = None
        self.tor_hidden_address = None

        # Web server variables
        self.tor_webserver_port = None

        # Setup custom logging handler
        self.logger = logging.getLogger(__name__)
        self.logger = logging.basicConfig(filename='debug.log', level=logging.DEBUG)

        if not self._is_running():
            self.tor_process = self._start_tor()

        self.tor_controller = Controller.from_port(port=self.tor_ctrl_port)
        self.logger.debug("Attempting to authenticate with TOR Controller")
        self.tor_controller.authenticate(self.tor_ctrl_pass)
        self.tor_data_dir = self.tor_controller.get_conf('DataDirectory')
        self.tor_session = requests.Session()
        self.tor_session.proxies.update({
            'http': 'socks5://localhost:%d' % (self.tor_socks_port),
            'https': 'socks5://localhost:%d' % (self.tor_socks_port),
        })

    def close(self):
        try:
            self.tor_session.close()
            self.tor_controller.close()
        except: pass
        if self.tor_process: self.tor_process.terminate()

    def tor_messages(self, line):
        pass

    def get_bytes_read(self):
        if self.tor_controller.get_info("traffic/read"):
            return self.tor_controller.get_info("traffic/read")

    def get_bytes_written(self):
        if self.tor_controller.get_info("traffic/written"):
            return self.tor_controller.get_info("traffic/written")

    def get_tor_socks_port(self):
        self.logger.debug("get_tor_socks_port function called!")
        if self.tor_socks_port:
            return self.tor_socks_port

    def set_tor_socks_port(self, port):
        self.logger.debug("set_tor_socks_port function called!")
        if port:
            self.tor_socks_port = int(port)

    def get_tor_ctrl_port(self):
        self.logger.debug("get_tor_ctrl_port function called!")
        if self.tor_ctrl_port:
            return self.tor_ctrl_port

    def set_tor_ctrl_port(self, port):
        self.logger.debug("set_tor_ctrl_port function called!")
        if port:
            self.tor_ctrl_port = int(port)

    def get_tor_ctrl_pass(self):
        self.logger.debug("get_tor_ctrl_pass function called!")
        if self.tor_ctrl_pass:
            return self.tor_ctrl_pass

    def set_tor_ctrl_pass(self, password):
        self.logger.debug("set_tor_ctrl_pass function called!")
        if password:
            self.tor_ctrl_pass = str(password)

    def get_webserver_port(self):
        self.logger.debug("get_webserver_port function called!")
        if self.tor_webserver_port:
            return self.tor_webserver_port

    def set_webserver_port(self, port=8080):
        self.logger.debug("set_tor_webserver_port function called!")
        if port:
            self.tor_webserver_port = int(port)

    def reset_identity(self):
        self.logger.debug("Attempting to reset the tor circuit/identity.")
        self.tor_controller.signal(stem.Signal.NEWNYM)
        sleep(self.tor_controller.get_newnym_wait())

    def _start_tor(self):
        self.logger.debug("Attempting to start the TOR instance.")
        return launch_tor_with_config(
            config={
                'SocksPort': str(self.tor_socks_port),
                'ControlPort': str(self.tor_ctrl_port)
            },
            take_ownership=True,
            init_msg_handler=self.tor_messages, )

    def _start_webserver(self, path):
        try:
            if path:
                os.chdir(path)
        except OSError:
            os.getcwd()

        self.logger.debug("Attempting to start webserver on port %d" % int(self.get_webserver_port()))
        httpd = SocketServer.TCPServer(("localhost", self.get_webserver_port()), SimpleHTTPServer.SimpleHTTPRequestHandler)
        th = threading.Thread(target=httpd.serve_forever)
        th.daemon = True
        th.start()

    def start_hidden_service(self, listener_port=8080, local_port=1337, name="TODO_generate_me", ws = True):
        self.tor_hidden_dir = os.path.join(self.tor_controller.get_conf('DataDirectory', '/tmp'), name)
        if ws:
            local_port = self.get_webserver_port()
            self._start_webserver(local_port)

        r = self.tor_controller.create_ephemeral_hidden_service({listener_port: local_port}, await_publication=True)
        if r.service_id:
            self.tor_hidden_address = r.service_id
            return r.service_id
        else:
            return None

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

    def delete(self, *args, **kwargs):
        return self.tor_session.delete(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

