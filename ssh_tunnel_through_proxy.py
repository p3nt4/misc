#!/usr/bin/env python

import getpass
import os
import socket
import select
import sys
import threading
from optparse import OptionParser
import http.client
import urllib.parse

import paramiko

SSH_PORT = 443
DEFAULT_PORT = 4000

g_verbose = True


def http_proxy_tunnel_connect(proxy, target,timeout=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(proxy)
        print("connected")
        cmd_connect = "CONNECT %s:%d HTTP/1.1\r\n\r\n"%target
        print(("--> %s"%repr(cmd_connect)))
        sock.sendall(cmd_connect.encode())
        response = bytes([])
        sock.settimeout(2) # quick hack - replace this with something better performing.
        try: 
            # in worst case this loop will take 2 seconds if not response was received (sock.timeout)
            while True:
                chunk = sock.recv(1024)
                if not chunk: # if something goes wrong
                    break
                response +=bytes(chunk)
                if "\r\n\r\n" in chunk.decode(): # we do not want to read too far ;)
                    break
        except socket.error as se:
            if "timed out" not in se:
                response=[se]
        responsestr = response.decode()
        print(("<-- %s"%repr(responsestr)))
        if not "200 connection established" in responsestr.lower():
            raise Exception("Unable to establish HTTP-Tunnel: %s"%repr(responsestr))
        return sock


def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        verbose("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    verbose(
        "Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    verbose("Tunnel closed from %r" % (chan.origin_addr,))


def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()


def verbose(s):
    if g_verbose:
        print(s)


HELP = """\
Set up a reverse forwarding tunnel across an SSH server, using paramiko. A
port on the SSH server (given with -p) is forwarded across an SSH session
back to the local machine, and out to a remote site reachable from this
network. This is similar to the openssh -R option.
"""


def get_host_port(spec, default_port):
    "parse 'hostname:22' into a host and port, with the port optional"
    args = (spec.split(":", 1) + [default_port])[:2]
    args[1] = int(args[1])
    return args[0], args[1]


def parse_options():
    global g_verbose

    parser = OptionParser(
        usage="usage: %prog [options] <ssh-server>[:<server-port>]",
        version="%prog 1.0",
        description=HELP,
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="squelch all informational output",
    )
    parser.add_option(
        "-p",
        "--remote-port",
        action="store",
        type="int",
        dest="port",
        default=DEFAULT_PORT,
        help="port on server to forward (default: %d)" % DEFAULT_PORT,
    )
    parser.add_option(
        "-u",
        "--user",
        action="store",
        type="string",
        dest="user",
        default=getpass.getuser(),
        help="username for SSH authentication (default: %s)"
        % getpass.getuser(),
    )
    parser.add_option(
        "-K",
        "--key",
        action="store",
        type="string",
        dest="keyfile",
        default=None,
        help="private key file to use for SSH authentication",
    )
    parser.add_option(
        "",
        "--no-key",
        action="store_false",
        dest="look_for_keys",
        default=True,
        help="don't look for or use a private key file",
    )
    parser.add_option(
        "-P",
        "--password",
        action="store_true",
        dest="readpass",
        default=False,
        help="read password (for key or password auth) from stdin",
    )
    parser.add_option(
        "-r",
        "--remote",
        action="store",
        type="string",
        dest="remote",
        default=None,
        metavar="host:port",
        help="remote host and port to forward to",
    )
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("Incorrect number of arguments.")
    if options.remote is None:
        parser.error("Remote address required (-r).")

    g_verbose = options.verbose
    server_host, server_port = get_host_port(args[0], SSH_PORT)
    remote_host, remote_port = get_host_port(options.remote, SSH_PORT)
    return options, (server_host, server_port), (remote_host, remote_port)


def main():
    options, server, remote = parse_options()
    password = ""
    if options.readpass:
        password = getpass.getpass("Enter SSH password: ")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    verbose("Connecting to ssh host %s:%d ..." % (server[0], server[1]))
    try:
        proxy_uri = ""
        url = urllib.parse.urlparse(proxy_uri)
        http_con = http.client.HTTPConnection(url.hostname, url.port)

        headers = {}
        if url.username and url.password:
            auth = '%s:%s' % (url.username, url.password)
            headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(auth)
        http_con.set_tunnel(server[0], server[1],headers)
        http_con.connect()
        sock = http_con.sock
        #sock = http_proxy_tunnel_connect(proxy=("",),target=(server[0],server[1]),timeout=500)
        data = sock.recv(5)
        print(data.decode())
        sock.send("HELLO BACK".encode())
        #sock.send("\nClient: HELLO BACK".encode())
        #print(data.decode())
        client.connect(
          hostname=server[0],
          port=server[1],
          sock=sock,
          username=options.user,
          password=password,
          banner_timeout=4
        )
    except Exception as e:
        print(("*** Failed to connect to %s:%d: %r" % (server[0], server[1], e)))
        raise e
        sys.exit(1)

    verbose(
        "Now forwarding remote port %d to %s:%d ..."
        % (options.port, remote[0], remote[1])
    )

    try:
        reverse_forward_tunnel(
            options.port, remote[0], remote[1], client.get_transport()
        )
    except KeyboardInterrupt:
        print("C-c: Port forwarding stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
