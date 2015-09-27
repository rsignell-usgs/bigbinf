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

def plot_packets(dump_batch):
    """
    Plots time on the x axis vs length on the y axis
    """
    # Convert all the times to an offset from 0
    xy = []
    for dump in dump_batch:
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
        axes[i].set_title(dump_batch[i]["protocol"], size=16)
        axes[i].yaxis.set_major_locator(plt.MaxNLocator(max_yticks))

        # Add a line to show where the transfer stopped
        ylim = axes[i].get_ylim()
        end = max(xy[i][0])
        axes[i].plot([end, end], [ylim[0], ylim[1]], "g--", linewidth=1, label="final packet")

    fig.text(0.5, 0.04, "Time elapsed", ha='center', va='center', size=16)
    fig.text(0.04, 0.5, "Length of payload (bytes)", ha='center', va='center',
             rotation='vertical', size=16)
    fig.suptitle("Individual Packets", size=18)
    axes[3].legend(bbox_to_anchor=(1, -0.1))
    fig.show()

def plot_speed_efficiency(df, filesize):
    """
    Given a pandas Dataframe, plots each protocol's speed
    vs it's data efficiency
    """
    fs = filesize
    rows = df.loc[df["File Size (bytes)"] == fs]
    x = rows["Bytes Total"]
    y = rows["Speed (bytes/s)"]
    plt.plot(x, y, "o")

    # Add a line to represent filesize
    ylim = plt.ylim()
    plt.plot([fs, fs], [ylim[0], ylim[1]], "r--", linewidth=3, label="filesize")

    plt.title("Speed vs Data Efficiency for %s Byte File" % fs, size=18)
    plt.ylabel("Speed (bytes/s)", size=16)
    plt.xlabel("Total Bytes Transferred", size=16)
    plt.legend()
    plt.show()

def get_dumps(protocols, n):
    """
    Returns dumps in json
    """
    fnames = get_dump_fnames(protocols, n)
    dumps = []

    for fname in fnames:
        with open("packet_dumps/%s" % fname) as f:
            dumps.append(json.load(f))

    return dumps

def display_dumps(dumps):
    """
    Organizes a set of dumps into a pandas DataFrame
    """
    # Set up DataFrame with correct columns
    df = pd.DataFrame(dumps)
    df.drop(["host_from", "host_to", "packets"], axis=1, inplace=True)

    # Calculate new columns and round
    df["time"] = np.round(df["time"], 2)
    df["speed"] = np.round(df["bytes_down"]/df["time"], 2)
    df["ratio"] = np.round(df["bytes_total"]/df["file_size"]*100, 2)

    # Remove milliseconds from start time
    t = pd.to_datetime(df["utc_start_time"])
    t = [d.strftime("%Y-%m-%d %H:%M:%S") for d in t]
    df["utc_start_time"] = t

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
