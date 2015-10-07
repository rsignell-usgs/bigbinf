"""
Common functions used for analysis
"""
from datetime import datetime, timedelta
import json
import numpy as np
import os
import pandas as pd

from matplotlib import pyplot as plt, dates
from protocols import PROC_ARGS

TIME_FORMAT = "%H:%M:%S.%f"

PLOT_TIME_FORMAT = "%M:%S"

def plot_packets(batch_id):
    """
    Plots time on the x axis vs length on the y axis
    """
    dump_batch_names = get_fnames_by_id(batch_id)
    dump_protocols = []
    filesize = 0

    # Convert all the times to an offset from 0
    xy = []
    for name in dump_batch_names:
        with open("packet_dumps/%s" % name) as f:
            dump = json.load(f)

        dump_protocols.append(dump["protocol"])
        filesize = sizeof_fmt(dump["file_size"])
        x = [datetime.strptime(l["time"], TIME_FORMAT) for l in dump["packets"]]
        t0 = min(x)
        dt = timedelta(hours=t0.hour, minutes=t0.minute, seconds=t0.second,
                       microseconds=t0.microsecond)
        x = [t-dt for t in x]
        y = [l["length"] for l in dump["packets"]]
        xy.append((x, y))

    fig, axes = plt.subplots(4, sharex="col")
    max_yticks = 4

    for i in range(4):
        axes[i].plot(xy[i][0], xy[i][1], ".")
        axes[i].xaxis.set_major_formatter(dates.DateFormatter(PLOT_TIME_FORMAT))
        axes[i].set_title(dump_protocols[i], size=16)
        axes[i].yaxis.set_major_locator(plt.MaxNLocator(max_yticks))

        # Add a line to show where the transfer stopped
        ylim = axes[i].get_ylim()
        end = max(xy[i][0])
        axes[i].plot([end, end], [ylim[0], ylim[1]], "g--", linewidth=1, label="final packet")

    fig.text(0.5, 0.04, "Time elapsed", ha='center', va='center', size=16)
    fig.text(0.04, 0.5, "Length of payload (bytes)", ha='center', va='center',
             rotation='vertical', size=16)
    fig.suptitle("Individual Packets for %s Transfer" % filesize, size=18)
    axes[3].legend(bbox_to_anchor=(1, -0.1))
    fig.show()

def plot_speed_efficiency(df, filesize):
    """
    Given a pandas Dataframe, plots each protocol's speed
    vs it's data efficiency
    """
    rows = df.loc[int(filesize)]

    x = rows["Bytes Total"]
    y = rows["Speed (bytes/s)"]
    marker = ["o", "o", "*", "*"]
    colors = ["k", "m", "m", "k"]

    for i in range(4):
        pname = rows.index[i]
        plt.scatter(x[i], y[i], marker=marker[i], color=colors[i], s=150, label=pname)

    # Add a line to represent filesize
    ylim = plt.ylim()
    plt.plot([filesize, filesize], [ylim[0], ylim[1]], "r--", linewidth=3, label="filesize")

    plt.title("Speed vs Data Efficiency for %s File" % sizeof_fmt(filesize), size=18)
    plt.ylabel("Speed (bytes/s)", size=16)
    plt.xlabel("Total Bytes Transferred", size=16)
    plt.legend(bbox_to_anchor=(1.18, 1), scatterpoints=1)
    plt.ylim(ylim)
    plt.show()

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
    df = df[["protocol", "batch_id", "utc_start_time", "file_size", "bytes_down",
             "bytes_up", "bytes_total", "ratio", "time", "speed"]]
    df.columns = ["Protocol", "Batch ID", "Start Time", "File Size (bytes)", "Bytes Down",
                  "Bytes Up", "Bytes Total", "Ratio (%)", "Time (s)", "Speed (bytes/s)"]

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

