"""
Wrapper classes for transfer protocols
"""
import subprocess
import socket
import fcntl
import struct

PROC_ARGS = {"gridftp": "globus-url-copy -vb sshftp://%s%s %s",
             "scp": "scp %s:%s %s",
             "ftp": "sftp %s:%s %s"}

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

