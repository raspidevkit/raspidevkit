import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.constants import INPUT
    

class PIRMotionSensor(GpioDevice):
    def __init__(self, machine, pin: int):
        """
        Create a PIR motion sensor object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        pin_setup = {
            str(pin): INPUT
        }
        super().__init__(machine, pin_setup, device_type=INPUT)



    def read(self) -> bool:
        """
        Read the current state of PIR Motion Sensor

        :return: State (on/off)
        """
        return self.gpio_read(self.pin)



    def __repr__(self):
        return f"PIR Motion Sensor <pin={self.pin}, state={self.read()}>"
    