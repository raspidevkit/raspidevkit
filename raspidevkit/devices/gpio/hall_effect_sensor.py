import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.constants import INPUT, PULL_UP
    

class HallEffectSensor(GpioDevice):
    def __init__(self, machine, pin: int):
        """
        Create a hall effect sensor object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        pin_setup = {
            str(pin): PULL_UP
        }
        super().__init__(machine, pin_setup, device_type=INPUT)



    def read(self) -> bool:
        """
        Read the current state of hall effect sensor

        :return: State (on/off)
        """
        return self.gpio_read(self.pin)



    def __repr__(self):
        return f"Hall effect sensor <pin={self.pin}, state={self.read()}>"
    