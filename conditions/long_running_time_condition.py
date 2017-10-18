from conditions import FanStopCondition


class LongRunningTimeCondition(FanStopCondition):
    """
    if self.fan.on_time() > self.max_on_time():
    """

    def handle(self):
        if self.fan.on_time() > self.max_on_time():
            self.take_action()
            return True
        return False
