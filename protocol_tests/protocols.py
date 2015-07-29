"""
Wrapper classes for transfer protocols
"""
import subprocess

class GridFtp(object):
    """
    Wrapper for globus gridftp
    """
    def __init__(self, remote_host, remote_path, local_path):
        self.remote_host = remote_host
        self.remote_path = remote_path
        self.local_path = local_path

    def run(self):
        """
        Run globus-url-copy
        """
        subprocess.call(["globus-url-copy",
                         "-vb",
                         "sshftp://%s%s" % (self.remote_host, self.remote_path),
                         self.local_path])

