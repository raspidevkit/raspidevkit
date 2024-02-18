from ..base import ArduinoDevice
from raspidevkit.constants import OUTPUT
from raspidevkit.machineutils import stringutil
from typing import Union
import time


class ServoMotor(ArduinoDevice):
    def __init__(self, arduino, pin: int, 
                 commands: dict[str, Union[str, int]], uuid: str = '') -> None:
        """
        Create a Servo Motor object attached to Arduino

        :param arduino: Arduino master
        :param pin: Pin to attach Servo Motor in Arduino
        :param commands: Dictionary of commands with methods as keys.
        :param uuid: Optional UUID, if not given would randomly generate
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
            str(pin): 'custom'
        }
        super().__init__(pin_setup=pin_setup, 
                         device_type=OUTPUT, 
                         commands=commands,
                         uuid=uuid)
        all_methods = [
            'rotate'
        ]

        self.validate_commands(all_methods)
        self._method_code = self._map_method_code()
        self.__arduino = arduino

        self._state = False
        self._code_mapping['libraries'] = ['Servo.h']
        self._code_mapping['global'] = f'Servo servo{self.uuid};'
        self._code_mapping['setup'] = f'servo{self.uuid}.attach({pin});servo{self.uuid}.write(0);'
        self._code_mapping['methods'] = self._method_code
    


    def _map_method_code(self):
        """
        Create method code mapping
        """
        rotate_code = f'''String data = recieveData();
        int angle = data.toInt();
        servo{self.uuid}.write(angle);
        '''
        method_code = {
            'rotate': rotate_code,
        }
        return method_code
    


    def rotate(self, angle: int):
        """
        Rotate servo motor to angle

        :param angle: Angle to turn
        """
        if not isinstance(angle, int):
            raise ValueError('Angle should be int')

        command = self._commands.get('turn_on')
        self.__arduino.send_command(command)
        self.__arduino.send_data(str(angle))



    def cleanup(self):
        """
        Perform cleanup
        """
        self.turn_off()



    def __str__(self):
        """
        Device name
        """
        return "servo_motor"
    


    def __repr__(self):
        return f"Arduino Servo Motor <pin={self.pin}, state={self._state}>"
    