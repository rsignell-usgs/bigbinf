"""
Reads in .dump files and interprets them
"""
import argparse
import json
import sys

from protocols import PROC_ARGS
from helpers import aggregate,\
                    calc_speed,\
                    get_dump_fnames,\
                    sum_bytes
from plot import plot_packets, plot_aggregate

def main():
    """
    Reads the dump files and runs the analysis
    """
    fnames = get_dump_fnames(protocols=args.protocols, n=args.number)
    dumps = []

    for fname in fnames:
        with open("packet_dumps/%s" % fname) as f:
            dumps.append(json.load(f))

    if not args.graph:
        print_stats(dumps)
    else:
        if "packets" in args.graph:
            plot_packets(dumps)
        if "aggregate" in args.graph:
            plot_aggregate(dumps)

def print_stats(dumps):
    """
    Prints statistics in table form to stdout
    """
    header_main = "{:<12} | {:^60} | {:^36}"\
                  .format("", "Bytes Transferred", "Speed")

    header_sub = "{:<12} | {:<12}{:<12}{:<12}{:<12}{:<12} | {:<12}{:<12}{:<12}"\
                  .format("Protocol", "Down", "Up", "Total", "Filesize", "Ratio (%)",\
                          "Down", "Up", "Total")
    div = "="*len(header_sub)

    print
    print div
    print header_main
    print div
    print header_sub
    print div

    if args.aggregate:
        for p in args.protocols:
            t_d, t_u, t_t = aggregate([sum_bytes(d) for d in dumps if d["protocol"] == p])
            s_d, s_u, s_t = aggregate([calc_speed(d) for d in dumps if d["protocol"] == p])
            filesize = sum(int(d["file_size"]) for d in dumps)/len(dumps)
            r = (1-float(t_t)/float(filesize))*100
            ratio = "+{:.2f}".format(r) if r > 0 else "{:.2f}".format(r)
            print "{:<12} | {:<12}{:<12}{:<12}{:<12}{:<12} | {:<12.2f}{:<12.2f}{:<12.2f}"\
                  .format(p, t_d, t_u, t_t, filesize, ratio, s_d, s_u, s_t)

    else:
        for dump in dumps:
            t_d, t_u, t_t = sum_bytes(dump)
            s_d, s_u, s_t = calc_speed(dump)
            filesize = dump["file_size"]
            r = (1-float(t_t)/float(filesize))*100
            ratio = "+{:.2f}".format(r) if r > 0 else "{:.2f}".format(r)

            print "{:<12} | {:<12}{:<12}{:<12}{:<12}{:<12} | {:<12.2f}{:<12.2f}{:<12.2f}"\
                  .format(dump["protocol"], t_d, t_u, t_t, filesize, ratio, s_d, s_u, s_t)
    print

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--protocols", metavar="PROTOCOL", nargs="+",
                        default=PROC_ARGS.keys(),
                        help="Can be any combination of %s" % ", ".join(PROC_ARGS.keys()))
    parser.add_argument("-n", "--number", metavar="NUMBER", type=int, default=None,
                        help="The number of dumps to evaluate, starting with the \
                              most recent. Defaults to 'all'")
    parser.add_argument("-s", "--test-filesize", metavar="SIZE", type=int,
                        help="The size of the file used for testing, in bytes")
    parser.add_argument("-a", "--aggregate", action="store_true",
                        help="Aggregate dumps of the same type")
    parser.add_argument("-g", "--graph", nargs="+", default=None,
                        choices=["aggregate", "packets"], help="Which graphs to plot")
    parser.add_argument("-i", "--individual", action="store_true",
                        help="Aggregate dumps of the same type")
    args = parser.parse_args()

    if args.graph:
        args.number = 1

    sys.exit(main())
