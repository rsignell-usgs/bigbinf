"""
tcpdump interface to be used for analysis
"""
from datetime import datetime
import os
import subprocess

class TcpDump(object):
    """
    Captures tcpdump output for traffic between two hosts
    """

    def __init__(self, protocol, filename, if_name, host_1=None, host_2=None):
        """
        Takes either 0 or 2 hosts
        """
        self.protocol = protocol
        self.filename = filename
        self.if_name = if_name
        self.host_1 = host_1
        self.host_2 = host_2
        self.handle = None
        self.output = ""
        self.utc_start_time = str(datetime.utcnow())

    def start(self):
        """
        Starts the subprocess
        """
        packet_filter = ""
        if self.host_1 and self.host_2:
            packet_filter = "(host %s and host %s)" % (self.host_1, self.host_2)

        self.handle = subprocess.Popen(["tcpdump", "-i", self.if_name, packet_filter],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)

    def stop(self):
        """
        Stops the subprocess
        """
        self.handle.terminate()
        stdout = self.handle.stdout.read().split("\n")
        # get rid of blank lines
        stdout = [line for line in stdout if line]
        self.output = {"protocol": self.protocol,
                       "file_size": os.path.getsize(self.filename),
                       "uct_start_time": self.utc_start_time,
                       "packets": [get_packet_transfer_dict(line, self.host_1)
                                   for line in stdout]}

def get_packet_transfer_dict(line, host_1):
    """
    Represents a single line of tcpdump output
    """
    elements = line.split(" ")

    direction = "incoming" if elements[2].startswith(host_1) else "outgoing"

    return {"direction": direction,
            "time": elements[0],
            "from_ip": elements[2],
            "to_ip": elements[5],
            "length": elements[-1]}

