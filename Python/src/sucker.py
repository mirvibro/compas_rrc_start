from compas_rrc import PulseDigital, SetDigital

class Sucker:
    _io_name = 'ABB_Scalable_IO_0_DO1'

    def __init__(self, name):
        self._name = name

    def grab(self):
        return SetDigital(self._io_name, 1)

    def release(self):
        return SetDigital(self._io_name, 0)