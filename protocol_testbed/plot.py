"""
Functions to produce matplotilb figures
"""
from datetime import datetime, timedelta
import json
import numpy as np
from matplotlib import pyplot as plt, dates

from helpers import get_fnames_by_id, sizeof_fmt,\
                    calc_speed_ratios, TIME_FORMAT


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
    marker = ["o", "o", "o", "*", "*"]
    colors = ["k", "m", "r", "m", "k"]

    for i in range(5):
        pname = rows.index[i]
        plt.scatter(x[i], y[i], marker=marker[i], color=colors[i], s=150, label=pname)

    # Add a line to represent filesize
    ylim = plt.ylim()
    plt.plot([filesize, filesize], [ylim[0], ylim[1]], "r--", linewidth=3, label="filesize")

    # Add surrounding information
    plt.title("Speed vs Data Efficiency for %s File" % sizeof_fmt(filesize), size=22, y=1.1)
    plt.ylabel("Speed (bytes/s)", size=20)
    plt.xlabel("Total Bytes Transferred", size=20)
    plt.legend(bbox_to_anchor=(1.3, 1), scatterpoints=1, prop={"size":"14"})

    # Make sure the limits are correct and consistent
    plt.axes().yaxis.set_major_locator(plt.MaxNLocator(4))
    plt.axes().xaxis.set_major_locator(plt.MaxNLocator(4))
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.ylim(ylim)

    plt.show()

def plot_speed_per_filesize(df, ratio=False):
    """
    Takes an aggregated dataframe and plots
    speed as a function of filesize
    """
    agg = df.groupby(["File Size (bytes)", "Protocol"]).aggregate(np.mean)
    agg_inverse = df.groupby(["Protocol", "File Size (bytes)"]).aggregate(np.mean)

    sizes = agg.index.levels[0]
    protocols = agg.index.levels[1]

    markers = ["o", "o", "o", "*", "*"]
    colors = ["k", "m", "r", "m", "k"]

    if ratio:
        ylabel = "Speed Ratio"
        ratios = calc_speed_ratios(agg)
        for i, p in enumerate(protocols):
            plt.plot(ratios.index, ratios[p], marker=markers[i], color=colors[i], label=p)
    else:
        ylabel = "Speed (bytes/s)"
        for i, p in enumerate(protocols):
            sel = agg_inverse.loc[p]
            plt.plot(sizes, sel["Speed (bytes/s)"], marker=markers[i], color=colors[i], label=p)

    plt.title("Speed vs Filesize", size=22)
    plt.xlabel("Filesize (bytes)", size=20)
    plt.ylabel(ylabel, size=20)
    plt.legend(bbox_to_anchor=(1.2, 1), prop={"size":"16"})
    plt.show()
