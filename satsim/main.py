#!/usr/bin/env python
# coding: utf-8
import sys
from multiprocessing import Pipe
from station import Station
from satellite import Satellite
import argparse
from config import DEFAULT_STATION_PORT, SATELLITES


def start_system(station_port):
    ''' Starts our satellites and our station process '''

    # Create and start our sattelite processes passing newly created Pipes to
    # communicate with station process
    sat_connections = {}
    for sat in SATELLITES:
        station_conn, sat_conn = Pipe()
        sat_proc = Satellite(sat["id"], sat["fail_prob"], sat_conn)
        sat_proc.start()
        sat_connections[sat["id"]] = station_conn

    # Create and start our station process
    station_proc = Station(station_port, sat_connections)
    station_proc.start()
    station_proc.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="station port to listen for "
                        "tasks (default: %s)" % DEFAULT_STATION_PORT,
                        type=int, default=DEFAULT_STATION_PORT)
    args = parser.parse_args()

    try:
        start_system(args.port)
    except KeyboardInterrupt:
        sys.exit(0)
