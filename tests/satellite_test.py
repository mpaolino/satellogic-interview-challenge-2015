# coding: utf-8
import unittest
from multiprocessing import Pipe

from satsim.task import Task
from satsim.satellite import Satellite


class TestSatellite(unittest.TestCase):

    def test_processtask(self):
        test_conn, sat_conn = Pipe()
        sat = Satellite(sat_id=1, fail_prob=0, conn=sat_conn)
        task = Task(name='task', payoff=10, resources=[1], hour=18)

        sat.start()
        test_conn.send([task])
        reply = test_conn.recv()
        # Stop everything now as asserts may avoid it
        test_conn.close()
        sat.terminate()
        self.assertEquals(len(reply), 1)
        result = reply.pop()
        self.assertEquals(result.sat_id, 1)
        self.assertEquals(result.name, 'task')
        self.assertTrue(result.completed)
        test_conn.close()
        sat.terminate()

    def test_failtask(self):
        test_conn, sat_conn = Pipe()
        sat = Satellite(sat_id=1, fail_prob=1, conn=sat_conn)
        task = Task(name='task', payoff=10, resources=[1], hour=18)

        sat.start()
        test_conn.send([task])
        reply = test_conn.recv()
        # Stop everything now as asserts may avoid it
        test_conn.close()
        sat.terminate()
        self.assertEquals(len(reply), 1)
        result = reply.pop()
        self.assertEquals(result.sat_id, 1)
        self.assertEquals(result.name, 'task')
        self.assertFalse(result.completed)
