"""
Common functions used for analysis
"""
import os
from datetime import datetime

from protocols import PROC_ARGS

TIME_FORMAT = "%H:%M:%S.%f"

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

def aggregate(l):
    """
    Aggregates lists of tuples
    e.g. [(1,1,1), (3,3,3)] returns (2,2,2)
    """
    return tuple(sum(x)/len(x) for x in zip(*l))

def calc_speed(dump):
    """
    Calculates the average (down, up, total) speed of a transfer
    """
    length = sum_bytes(dump)
    time = get_time_elapsed(dump)
    return (length[0]/time,
            length[1]/time,
            length[2]/time)

def sum_bytes(dump):
    """
    Returns the (down, up, total) bytes of the transfer
    """
    down = 0
    up = 0
    total = 0

    for l in dump["packets"]:
        if l["direction"] == "up":
            up += int(l["length"])
        else:
            down += int(l["length"])
        total += int(l["length"])

    return (down, up, total)

def get_time_elapsed(dump):
    """
    Returns the total time elapsed, in seconds
    """
    t_min = datetime.strptime(min(l["time"] for l in dump["packets"]), TIME_FORMAT)
    t_max = datetime.strptime(max(l["time"] for l in dump["packets"]), TIME_FORMAT)
    return (t_max - t_min).total_seconds()