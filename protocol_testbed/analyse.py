"""
Reads in .dump files and interprets them
"""
import argparse
import json
import sys

from datetime import datetime

from protocols import PROC_ARGS
from helpers import get_dump_fnames, TIME_FORMAT, PLOT_TIME_FORMAT

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

def aggregate(l):
    """
    Aggregates lists of tuples
    e.g. [(1,1,1), (3,3,3)] returns (2,2,2)
    """
    return tuple(sum(x)/len(x) for x in zip(*l))

def print_speed(dumps):
    """
    Prints the up/down speed, in bytes/s, for each dump
    """
    print "\n{:^61}".format("Speed (bytes/s)")
    print "="*61
    print "{0:<15}{1:<15}{2:<15}{3:<15}".format("Protocol", "Down", "Up", "Total")
    print "="*61

    if args.aggregate:
        for p in args.protocols:
            agg = aggregate([calc_speed(d) for d in dumps if d["protocol"] == p])
            print "{0:<15}{1:<15.2f}{2:<15.2f}{3:<15.2f}".format(p, *agg)

    else:
        for dump in dumps:
            print "{0:<15}{1:<15.2f}{2:<15.2f}{3:<15.2f}"\
                   .format(dump["protocol"], *calc_speed(dump))
    print

def print_len_time(dumps):
    """
    Prints the total bytes transferred for each dump, overhead, and total time elapsed
    """
    print "\n{:^105}".format("Bytes transferred")
    print "="*105
    print "{0:<15}{1:<15}{2:<15}{3:<15}{4:<15}{5:<15}{6:<15}".format("Protocol", "Down", "Up",
                                                                     "Total", "Filesize",
                                                                     "Overhead (%)", "Time (s)")
    print "="*105

    if args.aggregate:
        for p in args.protocols:
            agg_len = aggregate([sum_bytes(d) for d in dumps if d["protocol"] == p])
            agg_time = sum(get_time_elapsed(d) for d in dumps)/len(dumps)
            agg_filesize = sum(int(d["file_size"]) for d in dumps)/len(dumps)
            print "{0:<15}{4:<15}{5:<15}{6:<15}{1:<15}{2:<15.4f}{3:<15}"\
                  .format(p, agg_filesize, (1-float(agg_len[2])/float(agg_filesize))*100,
                          agg_time, *agg_len)

    else:
        for dump in dumps:
            num_bytes = sum_bytes(dump)
            filesize = dump["file_size"]
            print "{0:<15}{4:<15}{5:<15}{6:<15}{1:<15}{2:<15.4f}{3:<15}"\
                  .format(dump["protocol"], filesize,
                          (1-float(num_bytes[2])/float(filesize))*100,
                          get_time_elapsed(dump), *num_bytes)
    print

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
    parser.add_argument("-a", "--aggregate", action="store_true",
                        help="Aggregate dumps of the same type")
    args = parser.parse_args()

    sys.exit(main())
