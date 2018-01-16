#!/usr/bin/env python2

#
# Example3: TOR Hidden Service to Custom Service
#

from pickyonion import PICKYONION

tor_proxy_port = 9050
tor_control_port = 9051
tor_control_pass = "password"

with PICKYONION(tor_proxy_port, tor_control_port, tor_control_pass) as picky:

    picky.set_hidden_service_port(8080)
    picky.set_local_service_port(1337)

    addr = picky.start_hidden_service(picky.get_hidden_service_port(), picky.get_local_service_port(), "random_name", False)
    
    if(addr):
        print "Hidden Service running at %s.onion:%d, redirecting to localhost:%d" % (addr, int(picky.get_hidden_service_port()), int(picky.get_local_service_port()))
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print "Exiting with keyboard interrupt.."
            picky.close()
