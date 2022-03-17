#!/usr/bin/env python
# coding: utf-8
import sys
import argparse
import zmq

DEFAULT_STATION_HOST = "localhost"
DEFAULT_STATION_PORT = 5556
DEFAULT_TASKS_FILE = "tasks.json"


def main(rfile, host, port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%s" % (host, port))
    tasks = open("tasks.json")
    sys.stdout.write("Connecting to Station and sending requests... ")
    sys.stdout.flush()
    socket.send(tasks.read())
    try:
        reply = socket.recv_string()
    except KeyboardInterrupt:
        return
    sys.stdout.write("DONE\n")
    print ("Station replied: %s" % reply)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="request JSON file"
                        " (default: %s)" % DEFAULT_TASKS_FILE,
                        type=str, default=DEFAULT_TASKS_FILE)
    parser.add_argument("--host", help="station host"
                        " (default: %s)" % DEFAULT_STATION_HOST,
                        type=str, default=DEFAULT_STATION_HOST)
    parser.add_argument("--port", help="station port"
                        " (default: %s)" % DEFAULT_STATION_PORT,
                        type=int, default=DEFAULT_STATION_PORT)
    args = parser.parse_args()
    try:
        main(args.file, args.host, args.port)
    except KeyboardInterrupt:
        sys.exit(0)
