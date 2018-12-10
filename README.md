# PyZNS - A Python3 Implementation of the ZeroMQ Name Service

This software allows PyZMQ users to access a distributed key/value store.
There are two components, which provide this service:
 * a ZNS Server and 
 * a ZNS Client

The administrator will edit for the server(s) a JSON file, which defines a
"dict" with the required key/value declarations.

The user can request for a known key the corresponing value.

The client/server components use the ZeroMQ "Brokerless Freelance Shotgun" model to
accomplish the task. 

### ZNS Server

When started, a server will read a file named "zns_data.json". The path can be
overruled with the environment variable "ZNS_DATA". After a change of the data
file, the server must be restarted to reflect the change.

For reliability, more servers can be started, each with a unique port
number. If the servers run on different hosts, each needs a copy of the data
file.

Help output of znssrv.py:

     > $ python3 znssrv.py -h
     > usage: znssrv.py [-h] [--debug] port_nr
     >
     > ZNS - ZMQ Name Service
     >
     > positional arguments:
     >  port_nr      port number
     >
     > optional arguments:
     >  -h, --help   show this help message and exit
     >  --debug, -d  generate some debug output


### ZNS Client

The ZNS service can't be used for ZNS itself. Therefor the coordinates of the
servers must be configured somehow. The administrator will edit a JSON file
which defines a "list" of the endpoints (IP:port) of the expected servers.

When started, a client will read a file named "zns_conf.json". The path can be
overruled with the environment variable "ZNS_CONF". After a change of the
config file, the client must be restarted to connect to the correct servers.

Usage example:

     > import zmq
     > import znscli
     >
     > ctx = zmq.Context()
     > cli = znscli.ZNSClient(ctx)
     > val = cli.get("hw_port")
     > ...


Extract from the ZNSClient documentation:

    class ZNSClient(builtins.object)
     |  Setup the freelance client as configured in zns_conf.
     |  
     |  Methods defined here:
     |  
     |  __init__(self, ctx, dbg=False)
     |      Initialize the client.
     |  
     |  close(self)
     |      Free the resources.
     |  
     |  get(self, key)
     |      Get a value only for a valid key.
     |  
     |  lookup(self, key)
     |      Lookup the value for key via the FLClient.
     |      Return an empty string for an unknown key.

Example of "zns_data.json":

     > {
     >     "hw_addr": "192.168.2.133",
     >     "hw_port": "5555",
     >     "wu_addr": "192.168.2.33",
     >     "wu_port": "5556"
     > }

Example of "zns_conf.json":

     > [
     >     "192.168.2.33:4567",
     >     "localhost:4568"
     > ]
