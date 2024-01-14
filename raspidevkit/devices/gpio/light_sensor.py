import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.constants import INPUT, OUTPUT
import time
    

class LightSensor(GpioDevice):
    def __init__(self, machine, pin: int):
        """
        Create a light sensor object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        pin_setup = {
            str(pin): INPUT
        }
        super().__init__(pin_setup, device_type=INPUT)
        self._machine = machine



    def read(self) -> int:
        """
        Read the current state of button

        :return: Value
        """
        value = 0
        self._machine.gpio_setup(self.pin, OUTPUT)
        self._machine.gpio_write(self.pin, False)
        time.sleep(0.1)
        self._machine.gpio_setup(self.pin, INPUT)
        while not self._machine.gpio_read(self.pin):
            value += 1
        return value



    def __repr__(self):
        return f"Light Sensor <pin={self.pin}, value={self.read()}>"
    