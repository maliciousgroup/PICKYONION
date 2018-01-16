# Project: PICKY ONION

**PICKY ONION** is a private red team python library focused on leveraging [TOR](https://www.torproject.org/) to establish secure communication and on-demand hidden service hosting.

    from Picky_Onion import picky_onion
	
	tor_proxy_port = 9050
	tor_control_port = 9051
	tor_control_pass = "password"

	with picky_onion(tor_proxy_port, tor_control_port, tor_control_pass) as picky:
    request = picky.get("https://canihazip.com/s")
    print request.text



# Dependencies
This library relies on the [TOR](https://www.torproject.org/) project to run, so you need to make sure the **tor** package is installed on your operating system. Depending on your distribution here are some examples:

**Debian/Ubuntu**

    $ sudo apt install tor


**Arch Linux**

    $ sudo pacman -S tor

 
**Fedora/CentOS/Redhat**

    $ sudo yum install tor

**OSX**

    $ brew install tor




# Installation
To install the library you will need to clone the git repository with authorization from the blackhatstodays security team.

    $ git clone https://github.com/blackhatstoday/pickyonion
    $ cd pickyonion
    $ sudo setup.py install
