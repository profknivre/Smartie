import os

from conditions import FanStartCond, FanStopCond

FORCEFANSTOP = '/tmp/forcefanstop'
FORCEFANSTART = '/tmp/forcefanstart'


class ForceStartCondition(FanStartCond):
    def handle(self):
        if os.path.exists(FORCEFANSTART):
            os.unlink(FORCEFANSTART)
            self.take_action()
            return True
        return False


class ForceStopCondition(FanStopCond):
    def handle(self):
        if os.path.exists(FORCEFANSTOP):
            os.unlink(FORCEFANSTOP)
            self.take_action()
            return True
        return False
