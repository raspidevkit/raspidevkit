from ..base import ArduinoDevice
from raspidevkit.constants import INPUT
from typing import Tuple, Optional, Union


class HallEffectSensor(ArduinoDevice):
    def __init__(self, arduino, pin: int, commands: dict[str, Union[str, int]]) -> None:
        """
        Create a hall effect sensor object attached to Arduino
        :param arduino: Arduino master
        :param pin: Pin to attach hall effect sensor in Arduino
        :param commands: Dictionary of commands with methods as keys.
        Required command configuration:
        ```python
        commands = {
            "read": 1,
        }
        ```
        """
        pin_setup = {
            str(pin): INPUT
        }
        super().__init__(arduino=arduino,
                         pin_setup=pin_setup, 
                         device_type=INPUT, 
                         commands=commands)
        all_methods = [
            'read',
        ]
        self.validate_commands(all_methods)
        self._method_code = self._map_method_code()

        self._state = False
        self._code_mapping['setup'] = f'pinMode({pin}, INPUT);'
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
        Get hall effect sensor state
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
            raise Exception('Hall effect sensor read fail')



    def __str__(self):
        """
        Device name
        """
        return "hall_effect_sensor"



    def __repr__(self):
        return f"Arduino Hall Effect Sensor <pin={self.pin}"
