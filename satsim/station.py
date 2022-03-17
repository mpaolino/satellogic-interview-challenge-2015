# coding: utf-8
import select
import zmq
import csv
import time
import traceback
from pulp import LpProblem, LpVariable, LpMaximize, LpInteger, lpSum
from multiprocessing import Process
import threading

from task import Task
from config import RESULTS_CSV_FILE, TASK_DISTRIBUTION_CSV_FILE


class Station(Process):
    '''Earth station process'''

    def __init__(self, port, sat_conns):
        '''
        Station receives a port and a sat_conns pipe dictionary keyed
        with sattelite ids.
        '''
        super(Station, self).__init__()
        self.port = port
        self.sat_conns = sat_conns
        self.fileno_conns = {x.fileno(): x for x in
                             self.sat_conns.itervalues()}
        self.log_prefix = "[Station]"
        self.stop = False  # Used to signal our thread to stop

    def run(self):
        # Start a thread to get replies from satellites
        replies_thre = threading.Thread(target=self.get_replies)
        replies_thre.daemon = True
        replies_thre.start()

        # Start a thread that will listen for requests and process them
        listen_thre = threading.Thread(target=self.listen)
        listen_thre.daemon = True
        listen_thre.start()

        print("%s process started" % self.log_prefix)

        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.stop = True
                if listen_thre.isAlive() or replies_thre.isAlive():
                    # Give them some time then just leave
                    time.sleep(1)

                # Close Pipes
                map(lambda x: x.close(), self.sat_conns.itervalues())
                return
            except Exception as e:
                print("%s Unexpected error: %s" % (self.log_prefix, e))
                print(traceback.format_exc())  # TODO: remove

    def listen(self):
        '''
        Waits and processes requests from ZMQ
        '''
        # Start listening for zmq request
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)

        self.dist_file = open(TASK_DISTRIBUTION_CSV_FILE, 'aw')
        self.dist_writer = csv.writer(self.dist_file, delimiter=',')
        while True:
            if self.stop:
                # bye bye zmq
                context.destroy(linger=0)
                self.dist_file.close()
                return

            # The following will block until a new request arrives
            self.get_requests()

    def get_replies(self):
        '''
        Waits and processes replies from satellites
        '''
        result_file = open(RESULTS_CSV_FILE, 'aw')
        result_writer = csv.writer(result_file, delimiter=',')

        while True:
            if self.stop:
                result_file.close()
                return
            # Block until we get a new reply
            timeout = 1
            rlist, wlist, xlist = select.select(self.fileno_conns.keys(), [],
                                                [], timeout)
            for fileno in rlist:
                reply = self.fileno_conns[fileno].recv()
                # Process reply
                self.process_reply(reply, result_writer)

    def make_tasks(self, tasks_list):
        '''
        This method takes a tasks list as obtained from zmq and returns a list
        of Tasks, it will discard entries with missing keys
        '''
        # Create task objects with the task dictionaries
        tasks = []
        for task in tasks_list:
            try:
                tasks.append(Task(task["name"], task["payoff"],
                                  task["resources"], task["hour"]))
            except KeyError:
                # Discard tasks with missing data
                print("%s Could not create a Task object for entry "
                      "'%s'" % (self.log_prefix, task))
                continue
        return tasks

    def get_requests(self):
        '''
        The actual code that waits for requests and sends them to be
        processed by satellites.
        '''
        tasks_dict = {}
        try:
            tasks_dict = self.socket.recv_json()  # This blocks
        except ValueError:
            print("%s Malformed JSON" % self.log_prefix)
            self.socket.send_string("MALFORMED JSON")
            return

        self.socket.send_string("OK")

        tasks = self.make_tasks(tasks_dict)
        print("%s Received new tasks, assigning to satellites")

        assigned, unassigned = self.assign_tasks(tasks,
                                                 self.sat_conns.keys())

        # Log assigments and unassignments
        self.log_assigned(assigned)
        self.log_unassigned(unassigned)

        # Send tasks to satellites
        for sat_id, assigned_tasks in assigned.iteritems():
            self.sat_conns[sat_id].send(assigned_tasks)

    def log_assigned(self, assigned):
        '''
        Gets a dictionary of assigned tasks to satellites and logs it
        '''
        for to, tasks in assigned.iteritems():
            for task in tasks:
                self.dist_writer.writerow([str(time.time()), task.name,
                                           task.payoff, list(task.resources),
                                           task.hour, to])
        self.dist_file.flush()

    def log_unassigned(self, unassigned):
        ''' Gets a list of assigned tasks to satellites and logs it'''
        for task in unassigned:
            self.dist_writer.writerow([str(time.time()), task.name,
                                       task.payoff, list(task.resources),
                                       task.hour, "unassigned"])
        self.dist_file.flush()

    def process_reply(self, reply, csv_writer):
        '''
        Process a reply from a satellite with all responses for tasks
        '''
        for result in reply:
            outcome = ""
            if result.completed is False:
                print("%s task %s failed on satellite "
                      "%s" % (self.log_prefix, result.name, result.sat_id))
                outcome = "failed"
            if result.completed is True:
                print("%s task %s succeeded on satellite "
                      "%s" % (self.log_prefix, result.name, result.sat_id))
                outcome = "ok"

            csv_writer.writerow([unicode(time.time()), result.name,
                                 result.sat_id, outcome])

    def assign_tasks(self, tasks, sat_ids):
        '''
        assign_tasks will receive a list of tasks and the list of available
        satellites ids, it will return a dictionary of scheduled tasks keyed by
        satellite ids and a list of tasks that could not be assigned.
        This method will try to maximize payoffs while avoiding resource or
        hour conflicts between the tasks. Its just an approximation that uses
        linear programming to obtain a Maximal Weighted Independent Set from
        the tasks.
        Thinking our task set as a graph where 'nodes=tasks with payoff as
        weight' and 'edges=conflicts in resources or hours' we can use LP to
        solve it in a reasonable ammount of time given that we won't have a
        huge ammount of tasks to assign at any given time.
        '''
        tasks.sort(key=lambda x: x.payoff, reverse=True)
        assigments = {}
        for sat_id in sat_ids:
            if not tasks:
                # We run out of tasks to assign
                break

            sat_tasks = self.approximate_MWIS(tasks)
            if sat_tasks:
                assigments[sat_id] = sat_tasks

            # Remove from the pool the tasks that were already assigned O(n)
            map(tasks.remove, sat_tasks)

        return assigments, tasks

    def approximate_MWIS(self, tasks):
        '''
        This methods gives you an approximation to obtaining a MWIS of tasks
        using LP (with pulp library).
        '''
        prob = LpProblem("The Satellite Problem", LpMaximize)
        lp_vars = []

        # A numpy multidimentional array would be much more efficient
        conflict_matrix = [[False for x in xrange(len(tasks))]
                           for x in xrange(len(tasks))]
        # Create the variables first
        for x in xrange(len(tasks)):
            # Create one variable for every node, lets use the index as the
            # name in case we have two equally named tasks, value can be
            # either 1 or 0
            lp_vars.append(LpVariable("%d" % x, 0, 1, LpInteger))

        # We need to specify our objective functions first
        prob += lpSum([lp_vars[i] * tasks[i].payoff]
                      for i in xrange(len(tasks)))

        for x in xrange(len(tasks)):
            for y in xrange(len(tasks)):
                if x == y or conflict_matrix[x][y]:
                    # avoid creating restrictions, either its the same node or
                    # restriction was already accounted for
                    continue
                # Check for conflicts (to create restriction)
                resource_conflict = tasks[x].resources & tasks[y].resources
                hour_conflict = tasks[x].hour == tasks[y].hour
                if len(resource_conflict) or hour_conflict:
                    # Mark conflict in both direction to avoid generating
                    # another equal constrain
                    conflict_matrix[x][y] = True
                    conflict_matrix[y][x] = True
                    # Finally create our restriction for this edge
                    prob += lp_vars[x] + lp_vars[y] <= 1

        # Solve it baby!
        prob.solve()
        # Get the corresponding tasks that where identified as part of the MWIS
        task_mwis = [tasks[int(v.name)]
                     for v in prob.variables() if v.varValue == 1]
        return task_mwis
