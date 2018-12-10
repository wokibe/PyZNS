#! /usr/bin/env python

# zns_srv.py

"""Freelance "Shotgun" server for ZNS - ZMQ Name Service."""

import os
import json
import argparse
import zmq


def zns_srv(port):
    """Start the server loop with the 'port' number'."""
    # the server needs to read the preedited zns_data file
    # the default file name is zns_data.json
    # this path may be overruled by the environment variable ZNS_DATA
    try:
        fn = os.environ['ZNS_DATA']
    except Exception:
        fn = 'zns_data.json'

    with open(fn) as f:
        data = f.read()

    # convert the json string into a dict
    keyval = json.loads(data)
    if not type(keyval) == dict:
        raise Exception('ZNS Exception: Invalid zns_data format')

    # prepare the REP socket
    ctx = zmq.Context()
    srv = ctx.socket(zmq.REP)

    # construct the endpoint address
    addr = "tcp://*:%d" % port
    srv.bind(addr)

    if args.debug:
        print('zns_srv runs with port %d' % port)

    # server loop
    while True:
        # wait for a request
        req = srv.recv_multipart()
        if not req:
            break       # interrupted

        if args.debug:
            print("request: %s" % req)

        # fail if not the expected multipart
        assert len(req) == 2

        # extract the required key
        key = req[1].decode()

        # find the correspondig value
        if key in keyval:
            val = keyval[key]
        # or return an empty sring
        else:
            val = ''

        # prepare as bytes
        val = val.encode()

        # compose the multipart

        adr = req[0]
        rep = [adr, val]
        srv.send_multipart(rep)

    srv.setsockopt(zmq.LINGER, 0)


# ------------ main ---------------
parser = argparse.ArgumentParser(description='ZNS - ZMQ Name Service')
parser.add_argument('--debug', '-d', help='generate some debug output',
                    action='store_true', dest='debug')
parser.add_argument('port_nr', type=int, help='port number')
args = parser.parse_args()
zns_srv(args.port_nr)
