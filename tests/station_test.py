# coding: utf-8
import unittest
import zmq
from multiprocessing import Pipe

from satsim.station import Station
from satsim.task import Task
from satsim.config import DEFAULT_STATION_PORT


class TestStation(unittest.TestCase):

    def test_make_tasks(self):
        station = Station(DEFAULT_STATION_PORT, {})
        tasks = [{"name": 'task1',
                  "payoff": 1,
                  "resources": [1, 2],
                  "hour": 5},
                 {"name": 'task2',
                  "payoff": 2,
                  "resources": [2, 3],
                  "hour": 2}]
        converted = station.make_tasks(tasks)
        converted.sort(key=lambda x: x.name, reverse=True)
        self.assertEquals(len(converted), 2)
        task1 = converted.pop()
        task2 = converted.pop()
        self.assertTrue(isinstance(task1, Task))
        self.assertTrue(isinstance(task2, Task))
        self.assertEquals(task1.name, "task1")
        self.assertEquals(task2.name, "task2")
        self.assertEquals(task1.payoff, 1)
        self.assertEquals(task2.payoff, 2)
        self.assertEquals(task1.resources, set([1, 2]))
        self.assertEquals(task2.resources, set([2, 3]))
        self.assertEquals(task1.hour, 5)
        self.assertEquals(task2.hour, 2)

    def test_assign_tasks_resource_conflicts(self):
        station = Station(DEFAULT_STATION_PORT, {})
        task1 = Task(name="photo", payoff=10, resources=[1, 5],
                     hour=1)
        task2 = Task(name="maintenance", payoff=1, resources=[1, 2],
                     hour=2)
        task3 = Task(name="test", payoff=1, resources=[5, 6],
                     hour=3)
        task4 = Task(name="fsck", payoff=0.1, resources=[1, 6],
                     hour=4)
        (assigned, unassigned) = station.assign_tasks(tasks=[task1, task2,
                                                             task3, task4],
                                                      sat_ids=range(2))
        # Should have assigned to satellite 0 and 1
        self.assertEquals(len(assigned), 2)
        self.assertIn(0, assigned)
        self.assertIn(1, assigned)

        # task1 for satellite 0
        self.assertEquals(len(assigned[0]), 1)
        self.assertIn(task1, assigned[0])

        # task2 and task3 for satellite 1
        self.assertEquals(len(assigned[1]), 2)
        self.assertIn(task2, assigned[1])
        self.assertIn(task3, assigned[1])

        # task4 could not be assigned
        self.assertEquals(len(unassigned), 1)
        self.assertEquals(unassigned.pop(), task4)

    def test_assign_tasks_hour_conflicts(self):
        station = Station(DEFAULT_STATION_PORT, {})
        task1 = Task(name="photo", payoff=10, resources=[1, 2],
                     hour=1)
        task2 = Task(name="maintenance", payoff=1, resources=[3, 4],
                     hour=1)
        (assigned, unassigned) = station.assign_tasks(tasks=[task1, task2],
                                                      sat_ids=range(2))
        # One task for each satellite
        self.assertEquals(len(assigned), 2)
        self.assertIn(0, assigned)
        self.assertIn(1, assigned)

        self.assertEqual(assigned[0].pop(), task1)
        self.assertEqual(assigned[1].pop(), task2)

        self.assertEquals(len(unassigned), 0)

    def test_assign_tasks_no_conflicts(self):
        test_conn, sat_conn = Pipe()
        station = Station(DEFAULT_STATION_PORT, {})
        task1 = Task(name="photo", payoff=10, resources=[1, 2],
                     hour=1)
        task2 = Task(name="maintenance", payoff=1, resources=[3, 4],
                     hour=2)
        (assigned, unassigned) = station.assign_tasks(tasks=[task1, task2],
                                                      sat_ids=range(2))

        # No conflicts in tasks, all should be assigned to satellite 0
        self.assertEquals(len(assigned), 1)
        self.assertIn(0, assigned)

        self.assertEquals(len(assigned[0]), 2)
        self.assertIn(task1, assigned[0])
        self.assertIn(task2, assigned[0])

        self.assertEquals(len(unassigned), 0)

    def test_process_request(self):
        '''
        Send a JSON to the Station, see if it sends data to satellites
        '''
        json_tasks = '''
           [
            {
                "name": "photos",
                "payoff": 10,
                "resources": [
                    1,
                    2
                ],
                "hour": 10
            },
            {
                "name": "maintenance",
                "payoff": 1,
                "resources": [
                    3,
                    4
                ],
                "hour": 2
            }]'''

        task1 = Task(name="photos", payoff=10, resources=[1, 2],
                     hour=1)
        task2 = Task(name="maintenance", payoff=1, resources=[3, 4],
                     hour=2)

        test_conn, sat_conn = Pipe()
        station = Station(DEFAULT_STATION_PORT, {1: sat_conn})
        station.daemon = True
        station.start()

        # Lets connect and send the JSON
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % DEFAULT_STATION_PORT)
        socket.send_string(json_tasks)
        self.assertEquals(socket.recv_string(), "OK")
        context.destroy(linger=0)

        # Get the tasks for our satellite from the station
        sat_tasks = test_conn.recv()
        # Terminate our station process
        station.terminate()
        # Check that there are 2 tasks
        self.assertEquals(len(sat_tasks), 2)
        self.assertIn(task1, sat_tasks)
        self.assertIn(task2, sat_tasks)

    def test_malformed_json(self):
        '''
        Send a malformet JSON to the Station, see if it sends error back
        '''
        malformed_json = "[wrong"

        station = Station(DEFAULT_STATION_PORT, {})
        station.daemon = True
        station.start()

        # Lets connect and send the JSON
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % DEFAULT_STATION_PORT)
        socket.send_string(malformed_json)
        self.assertEquals(socket.recv_string(), "MALFORMED JSON")

        # Terminate our station process
        station.terminate()

        context.destroy(linger=0)
