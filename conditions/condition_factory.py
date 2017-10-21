import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from conditions import get_condition_list


class ConditionFactory:
    def __init__(self, fan, measurements):
        self.fan = fan
        self.measurements = measurements

    def build(self, sth):
        return (type(sth) is str) and self.build_by_name(sth) or self.build_by_cls(sth)

    def build_by_cls(self, cls):
        retval = cls(self.fan, self.measurements)
        return retval

    def build_by_name(self, name):
        cls = eval('conditions.{:s}'.format(name))  # XXX: fixme, check for smarter one....
        retval = cls(self.fan, self.measurements)
        return retval

    def build_all(self):
        return map(lambda x: self.build(x), get_condition_list())
