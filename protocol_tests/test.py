"""
Gets information on packets transferred during a globus-url-copy
"""
import argparse
from datetime import datetime
import socket
import sys

from tcpdump import TcpDump
from protocols import Protocol, get_ip_address

def main():
    """
    Do a transfer and log the packet data
    """
    gridftp = Protocol(args.host, args.remote_path, args.local_path, "gridftp")
    scp = Protocol(args.host, args.remote_path, args.local_path, "scp")
    test(gridftp)
    test(scp)



def test(protocol_obj):
    """
    Takes a Protocol object and runs a test for it
    Outputs the dump to a file
    """
    remote_hostname = args.host
    if "@" in remote_hostname:
        remote_hostname = remote_hostname[remote_hostname.find("@")+1:]

    remote_ip = socket.gethostbyname(remote_hostname)
    local_ip = get_ip_address(args.interface)
    dump = TcpDump(args.interface, remote_ip, local_ip)

    dump.start()
    protocol_obj.run()
    dump.stop()

    datestring = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    protocol_name = protocol_obj.protocol
    with open("packet_dumps/%s_%s.dump" % (protocol_name, datestring), "w") as f:
        f.writelines(line+"\n" for line in dump.output)


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

