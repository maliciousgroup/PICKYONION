#!/usr/bin/env python2

#
# Example2: TOR Hidden Service to Local Webserver
#

from pickyonion import PICKYONION

tor_proxy_port = 9050
tor_control_port = 9051
tor_control_pass = "password"

with PICKYONION(tor_proxy_port, tor_control_port, tor_control_pass) as picky:
    picky.set_webserver_port(65500)
    picky.set_webserver_dir("/tmp")
    addr = picky.start_hidden_service(8080, picky.get_webserver_port(), "random_name")
    if(addr):
        print "Local WebServer running on port 8080 at %s.onion" % (addr)
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print "Exiting with keyboard interrupt.."
            picky.close()
