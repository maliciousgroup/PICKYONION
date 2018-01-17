# Project: PICKY ONION

**PICKY ONION** is a private red team python library focused on leveraging [TOR](https://www.torproject.org/) to establish secure communication and on-demand hidden service hosting.

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
To install the library you will need to clone the git repository with **authorization** from the blackhatstodays security team.

    $ git clone https://github.com/blackhatstoday/pickyonion
	Cloning into 'pickyonion'...
	Username for 'https://github.com': <your_id>
	Password for 'https://blackhatstoday@github.com': <your_id_pass> 
	Unpacking objects: 100% (74/74), done.
	 
	$ cd pickyonion
	$ sudo ./setup.py install





# Examples

**Example 1**:  (Making a GET request via TOR socket)

    from pickyonion import PICKYONION
	
	tor_proxy_port = 9050
	tor_control_port = 9051
	tor_control_pass = "password"

	with picky_onion(tor_proxy_port, tor_control_port, tor_control_pass) as picky:
	    request = picky.get("https://canihazip.com/s")
	    print request.text


----------


**Example 2**: (Generating a hidden service address and redirecting traffic to built-in web server)

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


----------


**Example 3**: (Generating a hidden service address to redirect to a local port or service of choosing)

    from pickyonion import PICKYONION

	tor_proxy_port = 9050
	tor_control_port = 9051
	tor_control_pass = "password"

	hidden_port = 8080
	local_port = 1337

	with PICKYONION(tor_proxy_port, tor_control_port, tor_control_pass) as picky:
	    picky.set_hidden_service_port(hidden_port)
	    picky.set_local_service_port(local_port)
	    addr = picky.start_hidden_service(picky.get_hidden_service_port(), picky.get_local_service_port(), "random_name", False)
    
	    if(addr):
	        print "Hidden Service running at %s.onion:%d, redirecting to localhost:%d" % (addr, int(picky.get_hidden_service_port()), int(picky.get_local_service_port()))
	        try:
	            while True:
	                pass
	        except KeyboardInterrupt:
	            print "Exiting with keyboard interrupt.."
	            picky.close()


