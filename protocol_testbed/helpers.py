"""
Common functions used for analysis
"""
import os

from protocols import PROC_ARGS

def get_dump_fnames(protocols, n):
    """
    Returns the first n dumps matching specifics protocols
    """
    if not os.path.exists("packet_dumps"):
        return None

    # Filter on protocols
    matching_files = [f for f in os.listdir("packet_dumps") if f.startswith(tuple(protocols))]
    files = sorted(matching_files)

    # Filter on number
    if n is None:
        return files
    else:
        acc = []
        for p in PROC_ARGS:
            acc += [d for d in files if d.startswith(p)][:n]
        return acc
