import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.constants import OUTPUT, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO


class RgbLed(GpioDevice):
    def __init__(self, machine, pins: tuple[int, str]) -> None:
        """
        Create a RGB LED device that can change color light

        :param machine: Machine instance as this device parent
        :param pins: Tuple of pins to use, in RGB order (red, green, blue)
        """
        if len(pins) != 3:
            raise ValueError("Pins should have 3 values.")
        
        pin_setup = {
            str(tuple[0]): OUTPUT,
            str(tuple[1]): OUTPUT,
            str(tuple[2]): OUTPUT,
        }
        super().__init__(pin_setup, device_type=OUTPUT)
        self._color = None
        self._state = False
        self._machine = machine



    @property
    def state(self):
        """
        Fevice current state
        """
        return self._state
    


    @property
    def color(self):
        """
        Device current color
        """
        return self._color
    


    def turn_on(self):
        """
        Turn RGB LED on (white). Has no effect if already turned on.
        """
        if not self._state:
            for pin in self.pins:
                self._machine.gpio_write(pin, True)
            self._state = True
            self._color = WHITE



    def turn_off(self):
        """
        Turn RGB LED off. Has no effect if already turned off.
        """
        if self._state:
            for pin in self.pins:
                self._machine.gpio_write(pin, False)
            self._state = False
            self._color = None
            


    def set_color(self, color: str):
        """
        Change RGB LED color

        :param color: Color to set this RGB LED to
        Available colors:
        * RED
        * GREEN
        * BLUE
        * YELLOW
        * MAGENTA
        * CYAN
        * WHITE
        """
        color = color.upper()
        supported_colors = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE]
        if color not in supported_colors:
            raise NotImplementedError(f'Color {color} is not supported.')

        self._state = True
        if color == RED:
            self._machine.gpio_write(self.pins[0], True)
            self._machine.gpio_write(self.pins[1], False)
            self._machine.gpio_write(self.pins[2], False)
        if color == GREEN:
            self._machine.gpio_write(self.pins[0], False)
            self._machine.gpio_write(self.pins[1], True)
            self._machine.gpio_write(self.pins[2], False)
        if color == BLUE:
            self._machine.gpio_write(self.pins[0], False)
            self._machine.gpio_write(self.pins[1], False)
            self._machine.gpio_write(self.pins[2], True)
        if color == YELLOW:
            self._machine.gpio_write(self.pins[0], True)
            self._machine.gpio_write(self.pins[1], True)
            self._machine.gpio_write(self.pins[2], False)
        if color == MAGENTA:
            self._machine.gpio_write(self.pins[0], True)
            self._machine.gpio_write(self.pins[1], False)
            self._machine.gpio_write(self.pins[2], True)
        if color == CYAN:
            self._machine.gpio_write(self.pins[0], False)
            self._machine.gpio_write(self.pins[1], True)
            self._machine.gpio_write(self.pins[2], True)
        if color == WHITE:
            self._machine.gpio_write(self.pins[0], True)
            self._machine.gpio_write(self.pins[1], True)
            self._machine.gpio_write(self.pins[2], True) 



    def cleanup(self):
        """
        Perform cleanup
        """
        self.turn_off()
        


    def __repr__(self):
        return f"RGB LED <pins={self.pins}, state={self._state}>"
    