"""
Wrapper classes for transfer protocols
"""
import json
import socket
import subprocess

with open("args.json") as f:
    PROC_ARGS = json.load(f)

class Protocol(object):
    """
    Wrapper for transfer protocols
    """
    def __init__(self, remote_host, remote_path, local_path, protocol):
        self.remote_host = remote_host
        self.remote_path = remote_path
        self.local_path = local_path
        self.protocol = protocol
        self.proc_args = PROC_ARGS[protocol] % (remote_host, remote_path, local_path)

    def run(self):
        """
        Copy the file using proc_args
        """
        print "\nCalling: %s\n" % self.proc_args
        subprocess.call(self.proc_args.split(" "))

