import os

from conditions import FanStartCondition, FanStopCondition

FORCEFANSTOP = '/tmp/forcefanstop'
FORCEFANSTART = '/tmp/forcefanstart'


class ForceStartCondition(FanStartCondition):
    def handle(self):
        if os.path.exists(FORCEFANSTART):
            os.unlink(FORCEFANSTART)
            self.take_action()
            return True
        return False


class ForceStopCondition(FanStopCondition):
    def handle(self):
        if os.path.exists(FORCEFANSTOP):
            os.unlink(FORCEFANSTOP)
            self.take_action()
            return True
        return False
