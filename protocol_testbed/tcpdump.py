"""
tcpdump interface to be used for analysis
"""
from datetime import datetime
import os
import subprocess

BUFFER_FILE = "buffer"

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
        self.buff = open(BUFFER_FILE, "w+")

    def start(self):
        """
        Starts the subprocess
        """
        packet_filter = ""
        if self.host_1 and self.host_2:
            packet_filter = "host %s and host %s" % (self.host_1, self.host_2)

        self.handle = subprocess.Popen(["tcpdump", "-i", self.if_name, packet_filter],
                                       stdout=self.buff,
                                       stderr=None)

    def stop(self):
        """
        Stops the subprocess
        """
        # self.buff.flush()
        # self.handle.stdout.flush()
        self.handle.terminate()
        self.buff.close()
        with open(BUFFER_FILE) as f:
            stdout = f.read().split("\n")
        print "captured packets: %s" % len(stdout)
        os.remove("buffer")

        # get rid of blank lines
        stdout = [line for line in stdout if line]
        packets = [get_packet_transfer_dict(line, self.host_1) for line in stdout]

        self.output = {"protocol": self.protocol,
                       "file_size": os.path.getsize(self.filename),
                       "utc_start_time": self.utc_start_time,
                       "host_from": self.host_1,
                       "host_to": self.host_2,
                       "packets": [p for p in packets if p]}

def get_packet_transfer_dict(line, host_1):
    """
    Represents a single line of tcpdump output
    """
    elements = line.split(" ")

    # Sometimes tcpdump spits out lines like
    # 19:10:04.114431 IP 128.199.53.7], length 0
    # This happens because the process is killed abruptly.
    if len(elements) > 5:
        direction = "up" if elements[2].startswith(host_1) else "down"
        return {"direction": direction,
                "time": elements[0],
                "length": elements[-1]}
    else:
        return None

