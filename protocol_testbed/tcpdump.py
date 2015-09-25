"""
tcpdump interface to be used for analysis
"""
from datetime import datetime
import fcntl
import os
import socket
import struct
import subprocess
import time

from helpers import sum_bytes, get_time_elapsed

BUFFER_FILE = "buffer"

class TcpDump(object):
    """
    Captures tcpdump output for traffic between a remote host and local host
    """

    def __init__(self, protocol, filename, if_name, remote_hostname, local_ip):
        """
        Takes either 0 or 2 hosts
        """
        self.protocol = protocol
        self.filename = filename
        self.if_name = if_name
        self.remote_hostname = remote_hostname
        self.remote_ip = socket.gethostbyname(remote_hostname)
        self.local_ip = local_ip
        self.handle = None
        self.output = ""
        self.utc_start_time = str(datetime.utcnow())
        self.buff = open(BUFFER_FILE, "w+")

    def start(self):
        """
        Starts the subprocess
        """
        packet_filter = ""
        packet_filter = "host %s and host %s" % (self.remote_ip, self.local_ip)

        print "Filtering tcpdump with: %s" % packet_filter
        self.handle = subprocess.Popen(["tcpdump", "-i", self.if_name, packet_filter],
                                       stdout=self.buff,
                                       stderr=None)
        time.sleep(1)

    def stop(self):
        """
        Stops the subprocess
        """
        time.sleep(1)
        self.handle.terminate()
        self.buff.close()
        with open(BUFFER_FILE) as f:
            stdout = f.read().split("\n")
        os.remove("buffer")

        print
        print "Saving dump file..."
        print

        # get rid of blank lines
        stdout = [line for line in stdout if line]
        packets = [get_dict(line, self.remote_hostname, self.remote_ip) for line in stdout]
        packets = [p for p in packets if p]

        total_bytes = sum_bytes(packets)

        self.output = {"protocol": self.protocol,
                       "file_size": os.path.getsize(self.filename),
                       "utc_start_time": self.utc_start_time,
                       "host_from": self.remote_hostname,
                       "host_to": self.local_ip,
                       "bytes_down": total_bytes[0],
                       "bytes_up": total_bytes[1],
                       "bytes_total": total_bytes[2],
                       "time": get_time_elapsed(packets),
                       "packets": packets}

def get_dict(line, remote_hostname, remote_ip):
    """
    Represents a single line of tcpdump output
    """
    elements = line.split(" ")

    # Sometimes tcpdump spits out lines like
    # 19:10:04.114431 IP 128.199.53.7], length 0
    # This happens because the process is killed abruptly.
    if len(elements) > 5:
        # elements[2] is the host the packet was sent from
        direction = "down" if elements[2].startswith((remote_hostname, remote_ip)) else "up"
        return {"direction": direction,
                "time": elements[0],
                "length": int(elements[-1])}
    else:
        return None

def get_ip_address(ifname):
    """
    Gets the outward-facing, local ip address of the interface
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

