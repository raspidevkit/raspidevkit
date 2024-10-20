from ..base import ArduinoDevice
from raspidevkit.constants import OUTPUT
from typing import Union
import time


class Relay(ArduinoDevice):
    def __init__(self, arduino, pin: int, commands: dict[str, Union[str, int]]) -> None:
        """
        Create a LED object attached to Arduino

        :param arduino: Arduino master
        :param pin: Pin to attach LED in Arduino
        :param commands: Dictionary of commands with methods as keys.
        Required command configuration:
        ```python
        commands = {
            "turn_on": 1,
            "turn_off": 2,
            "blink": 3
        }
        ```
        """
        pin_setup = {
            str(pin): OUTPUT
        }
        super().__init__(arduino=arduino,
                         pin_setup=pin_setup, 
                         device_type=OUTPUT, 
                         commands=commands)
        all_methods = [
            'turn_on',
            'turn_off'
        ]
        self.validate_commands(all_methods)
        self._method_code = self._map_method_code()
        self._state = False
        self._code_mapping['methods'] = {
            'turn_on': f'digitalWrite({pin}, HIGH);',
            'turn_off': f'digitalWrite({pin}, LOW);'
        }
    


    @property
    def state(self):
        """
        Device state
        """
        return self._state
    


    def turn_on(self):
        """
        Turn on LED. Has no effect if already turned on.
        """
        if not self._state:
            command = self._commands.get('turn_on')
            self._arduino.send_command(command)
            self._state = True



    def turn_off(self):
        """
        Turn off LED. Has no effect if already turned off.
        """
        if self._state:
            command = self._commands.get('turn_off')
            self._arduino.send_command(command)
            self._state = False
        
    

    def _map_method_code(self):
        """
        Create method code mapping
        """
        method_code = {
            'turn_on': f'digitalWrite({self.pin}, HIGH);',
            'turn_off': f'digitalWrite({self.pin}, LOW);',
        }
        return method_code
    


    def cleanup(self):
        """
        Perform cleanup
        """
        self.turn_off()



    def __str__(self):
        """
        Device name
        """
        return "arduino_led"
    


    def __repr__(self):
        return f"Arduino LED <pin={self.pin}, state={self._state}>"
    