"""
Gets information on packets transferred during a globus-url-copy
"""
import argparse
import socket
import sys

from tcpdump import TcpDump
from protocols import GridFtp

def main():
    """
    Do a transfer and log the packet data
    """
    remote_ip = socket.gethostbyname(args.host)
    local_ip = socket.gethostbyname(socket.gethostname())
    dump = TcpDump(args.interface, remote_ip, local_ip)
    gridftp = GridFtp(args.host, args.remote_path, args.local_path)

    # Run the test
    dump.start()
    gridftp.run()
    dump.stop()

    print dump.output



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", metavar="INTERFACE", required=True,
                        help="The interface to capture packets on")
    parser.add_argument("-H", "--host", metavar="HOST", required=True,
                        help="The host which has the file to be copied")
    parser.add_argument("-r", "--remote-path", metavar="PATH", required=True,
                        help="The path of the file to be copied")
    parser.add_argument("-l", "--local-path", metavar="PATH", required=True,
                        help="The path where the file shold be copied to")
    args = parser.parse_args()

    sys.exit(main())

