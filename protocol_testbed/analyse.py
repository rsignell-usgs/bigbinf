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

    print
    print "{0:<10}{1}".format("Protocol", "Speed (bytes/s)")
    print "="*25
    for fname in fnames:
        pname = fname[:fname.find("_")]
        with open("packet_dumps/%s" % fname) as f:
            dump = json.load(f)
        print "{0:<10}{1:.2f}".format(pname+":", calc_speed(dump))

def calc_speed(dump):
    """
    Calculates the average speed of a transfer
    """
    length = sum_bytes(dump)[0]
    time = get_time_elapsed(dump)
    return length/time


def plot_length_time(dump, fname):
    """
    Plots time on the x axis vs length on the y axis
    """
    # Convert all the times to an offset from 0
    x = [datetime.strptime(l["time"], TIME_FORMAT) for l in dump]
    t0 = min(x)
    dt = timedelta(hours=t0.hour, minutes=t0.minute, seconds=t0.second, microseconds=t0.microsecond)
    x = [t-dt for t in x]

    y = [l["length"] for l in dump]

    # Tidy up the filename to be used as a title
    title = fname[:-5]
    title = title.replace("_", " ").upper()

    pyplot.figure()
    pyplot.plot(x, y, "o")
    pyplot.gca().xaxis.set_major_formatter(dates.DateFormatter(PLOT_TIME_FORMAT))
    pyplot.title(title)
    pyplot.xlabel("Time elapsed (min:second)")
    pyplot.ylabel("Length of payload (bytes)")
    pyplot.show()

def sum_bytes(dump):
    """
    Returns the total, incoming and outgoing bytes of the transfer
    """
    outgoing = 0
    incoming = 0
    total = 0

    for l in dump:
        if l["direction"] == "outgoing":
            outgoing += int(l["length"])
        else:
            incoming += int(l["length"])
        total += int(l["length"])

    return total, outgoing, incoming

def get_time_elapsed(dump):
    """
    Returns the total time elapsed, in seconds
    """
    t_min = datetime.strptime(min(l["time"] for l in dump), TIME_FORMAT)
    t_max = datetime.strptime(max(l["time"] for l in dump), TIME_FORMAT)
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
