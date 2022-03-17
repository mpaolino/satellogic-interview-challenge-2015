# coding: utf-8
import unittest

from satsim.task import Task


class TestTask(unittest.TestCase):

    def test_equals(self):
        task1 = Task(name='task1', payoff=10, resources=[1], hour=8)
        task2 = Task(name='task1', payoff=10, resources=[1], hour=8)
        self.assertTrue(task1 == task2)

    def test_notequals(self):
        task1 = Task(name='task1', payoff=10, resources=[1], hour=8)
        task2 = Task(name='task2', payoff=10, resources=[1], hour=8)
        self.assertTrue(task1 != task2)

        task1 = Task(name='task1', payoff=10, resources=[1], hour=8)
        task2 = Task(name='task1', payoff=20, resources=[1], hour=8)
        self.assertTrue(task1 != task2)

        task1 = Task(name='task1', payoff=10, resources=[1], hour=8)
        task2 = Task(name='task1', payoff=10, resources=[2], hour=8)
        self.assertTrue(task1 != task2)

        task1 = Task(name='task1', payoff=10, resources=[1], hour=8)
        task2 = Task(name='task1', payoff=10, resources=[1], hour=7)
        self.assertTrue(task1 != task2)
