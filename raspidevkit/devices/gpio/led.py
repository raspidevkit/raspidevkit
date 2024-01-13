import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.constants import OUTPUT
import time


class Led(GpioDevice):
    def __init__(self, machine, pin: int):
        """
        Create a LED object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        pin_setup = {
            str(pin): OUTPUT
        }
        super().__init__(pin_setup, device_type=OUTPUT)
        self._state = False
        self._machine = machine



    @property
    def state(self):
        """
        Device current state
        """
        return self._state
    

    
    def turn_on(self):
        """
        Turn on LED. Has no effect if already turn on.
        """
        if not self._state:
            self._machine.gpio_write(self.pin, True)
            self._state = True



    def turn_off(self):
        """
        Turn off LED. Has no effect if already turn off.
        """
        if self._state:
            self._machine.gpio_write(self.pin, False)
            self._state = False



    def set_state(self, state: bool):
        """
        Turn LED on/off.

        :param state: State to switch to
        """
        if state:
            self.turn_on()
        else:
            self.turn_off()



    def blink(self, delay: float):
        """
        Switch state after some delay and go back to current state

        :param delay: Delay before switching state
        """
        if self._state:
            self.turn_off()
            time.sleep(delay)
            self.turn_on()
        else:
            self.turn_on()
            time.sleep(delay)
            self.turn_off()



    def cleanup(self):
        """
        Perform cleanup
        """
        self.turn_off()


        
    def __repr__(self):
        return f"LED <pin={self.pin}, state={self._state}>"

