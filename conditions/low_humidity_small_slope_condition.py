from conditions import FanStopCondition


class LowHumiditySmallSlopeCondition(FanStopCondition):
    """
    if humidity < 80 and slope > -0.25 and self.fan.on_time() > self.min_on_time()
    """

    def handle(self):
        humidity, slope = self.measurements.bathroom_humidity, self.measurements.bathroom_humidity_slope
        if humidity < 80 and slope > -0.25 and self.fan.on_time() > self.min_on_time():
            self.take_action()
            return True
        return False
