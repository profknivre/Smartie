from conditions import FanStartCondition


class HighHumidityAndHighSlopeCondition(FanStartCondition):
    """
    if humidity >= 80 and slope >= 1:
    """

    def handle(self):
        humidity, slope = self.measurements.bathroom_humidity, self.measurements.bathroom_humidity_slope
        if humidity >= 80 and slope >= 1:
            self.take_action()
            return True
        return False
