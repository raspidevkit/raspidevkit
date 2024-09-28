from ..base import ArduinoDevice
from raspidevkit.constants import PULL_UP
from typing import Tuple, Optional, Union


class Button(ArduinoDevice):
    def __init__(self, arduino, pin: int, commands: dict[str, Union[str, int]]) -> None:
        """
        Create a button object attached to Arduino

        :param arduino: Arduino master
        :param pin: Pin to attachbutton in Arduino
        :param commands: Dictionary of commands with methods as keys.
        Required command configuration:
        ```python
        commands = {
            "read": 1,
        }
        ```
        """
        pin_setup = {
            str(pin): PULL_UP
        }
        super().__init__(arduino=arduino,
                         pin_setup=pin_setup, 
                         device_type=PULL_UP, 
                         commands=commands)
        all_methods = [
            'read',
        ]
        self.validate_commands(all_methods)
        self._method_code = self._map_method_code()

        self._state = False
        self._code_mapping['setup'] = f'pinMode({pin}, INPUT_PULLUP);'
        self._code_mapping['methods'] = self._method_code

    
    def _map_method_code(self):
        """
        Create method code mapping
        """
        read = f'sendResponse(String(digitalRead({self.pin})));'

        method_code = {
            'read': read
        }
        return method_code



    def read(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get button state
        :return: pressed state
        """
        command = self._commands.get('read')
        self._arduino.send_command(command)
        response = self._arduino.read_response(origin='cmd')
        try:
            if response == "1":
                return True
            return False
        except:
            raise Exception('Button read fail')
        


    def __str__(self):
        """
        Device name
        """
        return "button"
    


    def __repr__(self):
        return f"Arduino Button <pin={self.pin}"
