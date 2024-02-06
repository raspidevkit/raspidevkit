import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.constants import OUTPUT


class Relay(GpioDevice):
    def __init__(self, machine, pin: int):
        """
        Create a Relay object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        pin_setup = {
            str(pin): OUTPUT
        }
        super().__init__(machine, pin_setup, device_type=OUTPUT)
        self._state = False



    @property
    def state(self):
        """
        Device current state
        """
        return self._state
    

    
    def turn_on(self):
        """
        Turn on relay. Has no effect if already turn on.
        """
        if not self._state:
            self.gpio_write(self.pin, True)
            self._state = True



    def turn_off(self):
        """
        Turn off relay. Has no effect if already turn off.
        """
        if self._state:
            self.gpio_write(self.pin, False)
            self._state = False



    def set_state(self, state: bool):
        """
        Turn relay on/off.

        :param state: State to switch to
        """
        if state:
            self.turn_on()
        else:
            self.turn_off()



    def cleanup(self):
        """
        Perform cleanup
        """
        self.turn_off()


        
    def __repr__(self):
        return f"Relay <pin={self.pin}, state={self._state}>"

