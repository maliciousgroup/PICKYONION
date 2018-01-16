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
        self.tor_hidden_port = None
        self.tor_hidden_address = None

        # Internal Service (to redirect traffic to)
        self.local_service_port = None

        # Web server variables
        self.tor_webserver_port = None
        self.tor_webserver_dir = None

        # Attempt a logging functionality
        self.logger = logging.getLogger('PICKYONION')
        log_handler = logging.FileHandler('debug.log')
        formatter = logging.Formatter('%(name)s %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)
        self.logger.setLevel(logging.DEBUG)

        if not self._is_running():
            self.tor_process = self._start_tor()

        self.logger.debug("Attempting to start Controller")
        self.tor_controller = Controller.from_port(port=self.tor_ctrl_port)
        self.logger.debug("Attempting to authenticate with Controller")
        try:
            self.tor_controller.authenticate(self.tor_ctrl_pass)
        except:
            self.logger.exception("Authentication Failed")
            self.close()

        self.tor_data_dir = self.tor_controller.get_conf('DataDirectory')
        self.logger.debug("Attempting to start TOR Session")
        self.tor_session = requests.Session()
        self.tor_session.proxies.update({
            'http': 'socks5://localhost:%d' % (self.tor_socks_port),
            'https': 'socks5://localhost:%d' % (self.tor_socks_port),
        })

    def close(self):
        self.logger.debug("function close() was called")
        try:
            self.tor_session.close()
            self.tor_controller.close()
        except: pass
        if self.tor_process: self.tor_process.terminate()

    def tor_messages(self, line):
        pass

    def get_bytes_read(self):
        self.logger.debug("function get_bytes_read() was called")
        if self.tor_controller.get_info("traffic/read"):
            return self.tor_controller.get_info("traffic/read")

    def get_bytes_written(self):
        self.logger.debug("function was called")
        if self.tor_controller.get_info("traffic/written"):
            return self.tor_controller.get_info("traffic/written")

    def get_tor_socks_port(self):
        self.logger.debug("function get_tor_socks_port was called")
        if self.tor_socks_port:
            return self.tor_socks_port

    def set_tor_socks_port(self, port):
        self.logger.debug("function set_tor_socks_port was called")
        if port:
            self.tor_socks_port = int(port)

    def get_tor_ctrl_port(self):
        self.logger.debug("function get_tor_ctrl_port was called")
        if self.tor_ctrl_port:
            return self.tor_ctrl_port

    def set_tor_ctrl_port(self, port):
        self.logger.debug("function set_tor_ctrl_port was called")
        if port:
            self.tor_ctrl_port = int(port)

    def get_hidden_service_port(self):
        self.logger.debug("function get_hidden_service_port was called")
        if self.tor_hidden_port:
            return self.tor_hidden_port

    def set_hidden_service_port(self, port):
        self.logger.debug("function set_hidden_service_port was called")
        if port:
            self.tor_hidden_port = int(port)

    def get_tor_ctrl_pass(self):
        self.logger.debug("function get_tor_ctrl_pass was called")
        if self.tor_ctrl_pass:
            return self.tor_ctrl_pass

    def set_tor_ctrl_pass(self, password):
        self.logger.debug("function set_tor_ctrl_pass was called")
        if password:
            self.tor_ctrl_pass = str(password)

    def get_local_service_port(self):
        self.logger.debug("function get_local_service_port was called")
        if self.local_service_port:
            return self.local_service_port

    def set_local_service_port(self, port):
        self.logger.debug("function set_local_service_port was called")
        if port:
            self.local_service_port = int(port)

    def get_webserver_port(self):
        self.logger.debug("function get_webserver_port was called")
        if self.tor_webserver_port:
            return self.tor_webserver_port

    def set_webserver_port(self, port=8080):
        self.logger.debug("function set_webserver_port was called")
        if port:
            self.tor_webserver_port = int(port)

    def get_webserver_dir(self):
        self.logger.debug("function get_webserver_dir was called")
        if self.tor_webserver_dir:
            return(self.tor_webserver_dir)

    def set_webserver_dir(self, path=None):
        self.logger.debug("function set_webserver_dir called")
        if path:
            self.tor_webserver_dir = path

    def reset_identity(self):
        self.logger.debug("function reset_identity was called")
        self.tor_controller.signal(stem.Signal.NEWNYM)
        sleep(self.tor_controller.get_newnym_wait())

    def _start_tor(self):
        self.logger.debug("function was called")
        return launch_tor_with_config(
            config={
                'SocksPort': str(self.tor_socks_port),
                'ControlPort': str(self.tor_ctrl_port)
            },
            take_ownership=True,
            init_msg_handler=self.tor_messages, )

    def _start_webserver(self):
        self.logger.debug("function was called")
        try:
            if self.tor_webserver_dir:
                os.chdir(self.tor_webserver_dir)
        except OSError:
            os.getcwd()
        except:
            os.chdir("/tmp")

        self.logger.debug("function was called")
        httpd = SocketServer.TCPServer(("localhost", self.get_webserver_port()), SimpleHTTPServer.SimpleHTTPRequestHandler)
        th = threading.Thread(target=httpd.serve_forever)
        th.daemon = True
        th.start()

    def start_hidden_service(self, listener_port=8080, local_port=1337, name="TODO_generate_me", ws=True):
        self.logger.debug("Attempting to start hidden service")
        self.tor_hidden_dir = os.path.join(self.tor_controller.get_conf('DataDirectory', '/tmp'), name)
        if ws:
            local_port = self.get_webserver_port()
            self._start_webserver()

        if self.tor_hidden_port:
            listener_port = int(self.tor_hidden_port)

        if self.local_service_port:
            local_port = int(self.local_service_port)

        r = self.tor_controller.create_ephemeral_hidden_service({listener_port: local_port}, await_publication=True)
        if r.service_id:
            self.logger.debug("Success, %s.onion was created" % (r.service_id))
            self.tor_hidden_address = r.service_id
            return r.service_id
        else:
            self.logger.debug("Failed. Hidden Service failed to create")
            return None

    def _is_running(self):
        try:
            c = Controller.from_port(port=self.tor_ctrl_port)
            c.close()
            return True
        except:
            return False

    def get(self, *args, **kwargs):
        self.logger.debug("function get was called")
        return self.tor_session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.logger.debug("function post was called")
        return self.tor_session.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        self.logger.debug("function put was called")
        return self.tor_session.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.logger.debug("function delete was called")
        return self.tor_session.delete(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
