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
        super().__init__(pin_setup, device_type=INPUT)
        self._machine = machine



    def read(self) -> bool:
        """
        Read the current state of button

        :return: State (on/off)
        """
        return self._machine.gpio_read(self.pin)



    def __repr__(self):
        return f"Button <pin={self.pin}, state={self.read()}>"
    