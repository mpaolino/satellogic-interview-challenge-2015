# coding: utf-8


class Task():

    def __init__(self, name, payoff, resources, hour):
        self.name = name
        self.payoff = float(payoff)
        self.resources = set(resources)
        hour = int(hour)
        if hour < 0 or hour > 24:
            raise ValueError("hour must be > 0 and < 24")
        self.hour = hour

    def __eq__(self, task1):
        if self.name != task1.name:
            return False
        if self.payoff != task1.payoff:
            return False
        if self.resources != task1.resources:
            return False
        return True

    def __repr__(self):
        return "(Name: %s, payoff: %s, resources: %s, " \
               "hour: %s)" % (self.name, self.payoff,
                              self.resources, self.hour)

    def __unicode__(self):
        return unicode(self.__repr__())

    def __str__(self):
        return self.__repr__()
