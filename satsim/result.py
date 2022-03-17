# coding: utf-8


class Result():

    def __init__(self, sat_id, name, completed):
        self.sat_id = sat_id
        self.name = name
        self.completed = completed

    def __repr__(self):
        return "(sat_id: %s, name: %s, result: %s)" % (self.sat_id,
                                                       self.name,
                                                       self.completed)

    def __unicode__(self):
        return unicode(self.__repr__())

    def __str__(self):
        return self.__repr__()
