"""
tcpdump interface to be used for analysis
"""
import subprocess

class TcpDump(object):
    """
    Captures tcpdump output for traffic between two hosts
    """

    def __init__(self, if_name, host_1=None, host_2=None):
        """
        Takes either 0 or 2 hosts
        """
        self.if_name = if_name
        self.host_1 = host_1
        self.host_2 = host_2
        self.handle = None
        self.output = ""

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
        self.output = self.handle.stdout.read().split("\n")
