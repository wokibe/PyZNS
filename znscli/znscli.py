# zns-cli.py

"""Freelance Shotgun Client for ZNS - ZMQ Name Service."""

import os
import sys
import time
import json
import zmq

TIMEOUT = 1000  # ms


class FLClient(object):
    """This is the 'Freelance Shotgun' client from ZGuide.py."""

    def __init__(self, ctx, debug=False):
        """Initialize the client."""
        self.servers = 0
        self.sequence = 0
        self.context = ctx
        self.debug = debug
        self.socket = self.context.socket(zmq.DEALER)

    def destroy(self):
        """Release th resources."""
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()

    def connect(self, addr):
        """Connect to the server."""
        self.socket.connect(addr)
        self.servers += 1
        if self.debug:
            print("connect to %s" % addr)

    def request(self, *request):
        """Send the request to the server."""
        # prefix request with sequence number and empty envelope
        self.sequence += 1

        # prepare the multiopart
        msg = ['', str(self.sequence)] + list(request)

        #  encode the whole multipart
        msgb = []
        for s in msg:
            msgb.append(s.encode())

        # the dealer will distribute the request to all connected servers
        for server in range(self.servers):
            self.socket.send_multipart(msgb)

        # wait for a matching reply to arrive from anywhere
        poll = zmq.Poller()
        poll.register(self.socket, zmq.POLLIN)

        reply = None

        # calculate the maximum timeout
        endtime = time.time() + TIMEOUT / 1000
        while time.time() < endtime:
            socks = dict(poll.poll((endtime - time.time()) * 1000))
            if socks.get(self.socket) == zmq.POLLIN:
                replyb = self.socket.recv_multipart()
                assert len(replyb) == 3     # expected multipart length

                # decode the whole multipart
                reply = []
                for s in replyb:
                    reply.append(s.decode())

                sequence = int(reply[1])
                if sequence == self.sequence:
                    break   # got the expected sequence number

        if time.time() >= endtime:
            # raise Exception('ZNS Exception: No ZNS server available!')
            self.__fatal__('No ZNS server available!')
        return reply

    def __fatal__(self, txt):
        """Terminate after a fatal exception."""
        print("ZNS Exception: ", txt)
        os._exit(1)


class ZNSClient(object):
    """Setup the freelance client as configured in zns_conf."""

    def __init__(self, ctx, dbg=False):
        """Initialize the client."""
        # the client will connect to the preedited servers
        # the default file name is zns_conf.json
        # this path may be overruled by the environment variable ZNS_CONF
        try:
            fn = os.environ['ZNS_CONF']
        except Exception:
            fn = 'zns_conf.json'

        with open(fn) as f:
            conf = f.read()

        cfg = json.loads(conf)
        if dbg:
            print(cfg)

        if not type(cfg) == list:
            # raise Exception('ZNS Exception: Invalid data in zns_conf')
            self.__fatal__('Invalid data in zns_conf')
        self.flc = FLClient(ctx, dbg)
        for srv in cfg:
            addr = 'tcp://%s' % srv
            self.flc.connect(addr)

    def lookup(self, key):
        """Lookup the value for key via the FLClient."""
        reply = self.flc.request(key)

        # return only the requested value
        return reply[2]

    def get(self, key):
        """Get a value only for a valid key."""
        reply = self.lookup(key)
        if not reply:
            # raise Exception('ZNS Exception: Invalid key')
            self.__fatal__('Invalid key')
        return reply

    def close(self):
        """Free the resources."""
        self.flc.destroy()

    def __fatal__(self, txt):
        """Terminate after a fatal exception."""
        print("ZNS Exception: ", txt)
        os._exit(1)


if __name__ == '__main__':
    ctx = zmq.Context()
    cli = ZNSClient(ctx, True)

    key = 'wu_addr'
    val = cli.lookup(key)
    if val:
        print('%s: %s' % (key, val))
    else:
        print('invalid key: %s' % key)

    key = 'wu_port'
    val = cli.lookup(key)
    if val:
        print('%s: %s' % (key, val))
    else:
        print('invalid key: %s' % key)

    key = 'xyzzy'
    val = cli.lookup(key)
    if val:
        print('%s: %s' % (key, val))
    else:
        print('invalid key: %s' % key)

    val = cli.get(key)
    print('%s: %s' % (key, val))

    cli.close()
