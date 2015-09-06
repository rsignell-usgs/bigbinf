"""
Reads in .dump files and interprets them
"""
import argparse
from datetime import datetime, timedelta
import json
import os
import sys

from matplotlib import pyplot, dates

from protocols import PROC_ARGS

TIME_FORMAT = "%H:%M:%S.%f"
PLOT_TIME_FORMAT = "%M:%S"

def main():
    """
    Reads the dump files and runs the analysis
    """
    fnames = get_dump_fnames(protocols=args.protocols, n=args.number)
    dumps = []

    for fname in fnames:
        with open("packet_dumps/%s" % fname) as f:
            dumps.append(json.load(f))

    print_len_time(dumps)
    print_speed(dumps)
    plot_length_time(dumps[0])

def plot_length_time(dump):
    """
    Plots time on the x axis vs length on the y axis
    """
    # Convert all the times to an offset from 0
    x = [datetime.strptime(l["time"], TIME_FORMAT) for l in dump["packets"]]
    t0 = min(x)
    dt = timedelta(hours=t0.hour, minutes=t0.minute, seconds=t0.second, microseconds=t0.microsecond)
    x = [t-dt for t in x]

    y = [l["length"] for l in dump["packets"]]

    pyplot.figure()
    pyplot.plot(x, y, ".")
    pyplot.gca().xaxis.set_major_formatter(dates.DateFormatter(PLOT_TIME_FORMAT))
    pyplot.title(dump["protocol"])
    pyplot.xlabel("Time elapsed")
    pyplot.ylabel("Length of payload (bytes)")
    pyplot.show()

def print_speed(dumps):
    """
    Prints the up/down speed, in bytes/s, for each dump
    """
    print "\n{:^61}".format("Speed (bytes/s)")
    print "="*61
    print "{0:<15}{1:<15}{2:<15}{3:<15}".format("Protocol", "Down", "Up", "Total")
    print "="*61

    for dump in dumps:
        print "{protocol:<15}{up:<15.2f}{down:<15.2f}{total:<15.2f}"\
              .format(protocol=dump["protocol"],
                      **calc_speed(dump))
    print

def print_len_time(dumps):
    """
    Prints the total bytes transferred for each dump, as well as total time elapsed
    """
    print "\n{:^90}".format("Bytes transferred")
    print "="*90
    print "{0:<15}{1:<15}{2:<15}{3:<15}{4:<15}{5:<15}".format("Protocol", "Down", "Up",
                                                              "Total", "Filesize", "Time (s)")
    print "="*90

    for dump in dumps:
        print "{protocol:<15}{up:<15}{down:<15}{total:<15}{filesize:<15}{time:<15}"\
              .format(protocol=dump["protocol"],
                      filesize=dump["file_size"],
                      time=get_time_elapsed(dump),
                      **sum_bytes(dump))
    print

def calc_speed(dump):
    """
    Calculates the average (down, up, total) speed of a transfer
    """
    length = sum_bytes(dump)
    time = get_time_elapsed(dump)
    return {"up": length["up"]/time,
            "down": length["down"]/time,
            "total": length["total"]/time}

def sum_bytes(dump):
    """
    Returns the total, incoming and outgoing bytes of the transfer
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

    return {"down": down,
            "up": up,
            "total": total}

def get_time_elapsed(dump):
    """
    Returns the total time elapsed, in seconds
    """
    t_min = datetime.strptime(min(l["time"] for l in dump["packets"]), TIME_FORMAT)
    t_max = datetime.strptime(max(l["time"] for l in dump["packets"]), TIME_FORMAT)
    return (t_max - t_min).total_seconds()

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
    if not n:
        return files
    else:
        acc = []
        for p in PROC_ARGS:
            acc += [d for d in files if d.startswith(p)][:n]
        return acc

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--protocols", metavar="PROTOCOL", nargs="+",
                        default=PROC_ARGS.keys(),
                        help="Can be any combination of %s" % ", ".join(PROC_ARGS.keys()))
    parser.add_argument("-n", "--number", metavar="NUMBER", type=int,
                        help="The number of dumps to evaluate, starting with the \
                              most recent. Defaults to 'all'")
    parser.add_argument("-s", "--test-filesize", metavar="SIZE", type=int,
                        help="The size of the file used for testing, in bytes")
    args = parser.parse_args()

    sys.exit(main())
