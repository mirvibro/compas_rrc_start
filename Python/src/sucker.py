from compas_rrc import PulseDigital

# This is just a dummy implementation for now, update if we know more details about the suction tool
class Sucker:
    _io_name_grab = 'ABB_Scalable_IO_0_DO1'
    _io_name_release = 'ABB_Scalable_IO_0_DO2'

    def __init__(self, name, pulse_time = 0.2):
        self._name = name
        self.pulse_time = pulse_time

    def grab(self):
        return PulseDigital(self._io_name_grab, self.pulse_time)

    def release(self):
        return PulseDigital(self._io_name_release, self.pulse_time)