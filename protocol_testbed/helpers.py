"""
Common helper functions used for analysis
"""
import json
import numpy as np
import os
import pandas as pd
from datetime import datetime

from protocols import PROC_ARGS

TIME_FORMAT = "%H:%M:%S.%f"

def calc_speed_ratios(df):
    """
    Takes a dataframe grouped by filesize
    and then protocol. Returns their individual ratios
    """
    sizes = df.index.levels[0]
    protocols = df.index.levels[1]
    ans = pd.DataFrame(index=protocols)

    for size in sizes:
        sel = df.loc[size]
        smallest = float(min(sel["Speed (bytes/s)"]))
        biggest = float(max(sel["Speed (bytes/s)"]))
        ans[str(size)] = (sel["Speed (bytes/s)"]-smallest)/(biggest-smallest)

    return ans.transpose()

def calc_data_per_filesize(df):
    """
    Takes a dataframe grouped by filesize and then protocol,
    returns a dataframe with their respective ratios
    """
    sizes = df.index.levels[0]
    protocols = df.index.levels[1]
    ans = pd.DataFrame(index=protocols)

    for size in sizes:
        ans[str(size)] = df.loc[size]["Ratio (%)"]

    return ans.transpose()

def get_dumps(fnames):
    """
    Returns dumps in json
    """
    dumps = []

    for fname in fnames:
        # size = os.stat("packet_dumps/%s" % fname).st_size
        # print "Reading in %s (%s)" % (fname, sizeof_fmt(size))
        with open("packet_dumps/%s" % fname) as f:
            raw_dump = json.load(f)
            if raw_dump["stored_packets"]:
                del raw_dump["packets"]
            dumps.append(raw_dump)

    return dumps

def organize_dumps(dumps):
    """
    Organizes a set of dumps into a pandas DataFrame
    """
    # Set up DataFrame with correct columns
    df = pd.DataFrame(dumps)
    df.drop(["host_from", "host_to"], axis=1, inplace=True)

    # Make sure that there's a stored_packets column
    # This is for backwards compatability with dumps
    # that were collected before the value existed
    if not "stored_packets" in df.columns:
        df["stored_packets"] = True

    # Calculate new columns and round
    df["time"] = np.round(df["time"], 2)
    df["speed"] = np.round(df["bytes_down"]/df["time"], 2)
    df["ratio"] = np.round(df["bytes_total"]/df["file_size"]*100, 2)

    # Remove milliseconds from start time
    t = pd.to_datetime(df["utc_start_time"])
    t = [d.strftime("%Y-%m-%d %H:%M:%S") for d in t]
    df["utc_start_time"] = pd.to_datetime(t)

    # Group batches by batch_id
    ids = enumerate(set(df["batch_id"]))
    ids = {x[1]: x[0] for x in ids}
    df["batch_id"] = [ids[x] for x in df["batch_id"]]

    # Reorder and rename
    df = df[["protocol", "batch_id", "stored_packets", "utc_start_time", "file_size", "bytes_down",
             "bytes_up", "bytes_total", "ratio", "time", "speed"]]
    df.columns = ["Protocol", "Batch ID", "Stored Packets", "Start Time",
                  "File Size (bytes)", "Bytes Down", "Bytes Up", "Bytes Total",
                  "Ratio (%)", "Time (s)", "Speed (bytes/s)"]

    return df, ids

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

def get_fnames_by_id(batch_id):
    """
    Fetches the filenames for a specific batch_id
    """
    names = []

    for fname in os.listdir("packet_dumps"):
        dump = get_dumps([fname])[0]
        if dump["batch_id"] == batch_id:
            names.append(fname)

    return names

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
    length = sum_bytes(dump["packets"])
    time = get_time_elapsed(dump["packets"])
    return (length[0]/time,
            length[1]/time,
            length[2]/time)

def sum_bytes(packets):
    """
    Returns the (down, up, total) bytes of the transfer
    """
    down = 0
    up = 0
    total = 0

    for p in packets:
        if p["direction"] == "up":
            up += int(p["length"])
        else:
            down += int(p["length"])
        total += int(p["length"])

    return (down, up, total)

def get_time_elapsed(packets):
    """
    Returns the total time elapsed, in seconds
    """
    t_min = datetime.strptime(min(p["time"] for p in packets), TIME_FORMAT)
    t_max = datetime.strptime(max(p["time"] for p in packets), TIME_FORMAT)
    return (t_max - t_min).total_seconds()


def sizeof_fmt(num, use_kibibyte=True):
    """
    Converts 2540610608 -> 2.4 GiB
    """
    base, suffix = [(1000., 'B'), (1024., 'iB')][use_kibibyte]
    for x in ['B'] + [i+suffix for i in "kMGTP"]:
        if -base < num < base:
            return "%3.1f %s" % (num, x)
        num /= base
    return "%3.1f %s" % (num, x)

