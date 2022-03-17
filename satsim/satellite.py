# coding: utf-8
import random
import traceback
from multiprocessing import Process
from result import Result


class Satellite(Process):
    '''
    Satellite process class, receives tasks and determines if they fail or not
    '''
    def __init__(self, sat_id, fail_prob, conn):
        super(Satellite, self).__init__()
        self.sat_id = sat_id
        self.fail_prob = float(fail_prob)
        self.conn = conn
        self.log_prefix = "[Satellite %s]" % self.sat_id

    def run(self):
        '''One satellite process'''
        print("%s process started" % self.log_prefix)

        while True:
            try:
                tasks = self.conn.recv()
                # print("%s Received tasks: %s" % (self.log_prefix, tasks))
                results = []
                for task in tasks:
                    if self.should_task_fail():
                        results.append(Result(self.sat_id, task.name, False))
                    else:
                        results.append(Result(self.sat_id, task.name, True))
                self.conn.send(results)
            except KeyboardInterrupt:
                self.conn.close()
                return
            except Exception, e:
                print("%s Unexpected error: %s" % (self.log_prefix, e))
                print(traceback.format_exc())  # TODO: remove

    def should_task_fail(self):
        '''
        Used to simulate the task failure probability.
        '''
        return random.choices((True, False), weights=[self.fail_prob, 1-self.fail_prob], k=1).pop()
