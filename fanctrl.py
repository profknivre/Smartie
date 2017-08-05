from conditions import HighHumidityAndHighSlopeCondtion, LowHumiditySmallSlopeCondition, LongRunningTimeCondition
from fan import Fan
from measurements import Measurements


class FanController:
    def __init__(self, fan: Fan, measurements: Measurements):
        self.fan = fan
        self.measurements = measurements

        self.startconds = [HighHumidityAndHighSlopeCondtion(self.fan, self.measurements)]
        self.stopconds = [LowHumiditySmallSlopeCondition(self.fan, self.measurements),
                          LongRunningTimeCondition(self.fan, self.measurements)]

    # def get_slope(self, current_val, update=True):
    #     dq = self.db.get('hum_hist', deque(maxlen=10))
    #     dq3 = self.db.get('hum_hist3', deque(maxlen=3))
    #
    #     if update:
    #         dq.append(current_val)
    #         self.db['hum_hist'] = dq
    #         dq3.append(current_val)
    #         self.db['hum_hist3'] = dq3
    #
    #     a = get_slope(dq)
    #
    #     return a

    def do_stuff(self):

        if any(self.startconds):
            print('Fan started')

        if any(self.stopconds):
            print('Fan stopped')
