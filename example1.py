#!/usr/bin/env python2

#
# Example: Send an GET/POST request over TOR
#

from onion_requests import PICKYONION

tor_proxy_port = 9050
tor_control_port = 9051
tor_control_pass = "password"

with PICKYONION(tor_proxy_port, tor_control_port, tor_control_pass) as picky:
    request = picky.get("https://canihazip.com/s")
    print request.text