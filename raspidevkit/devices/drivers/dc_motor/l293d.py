from .base import DcMotorDriver, DcMotor
from typing import Union

class L293DDriver(DcMotorDriver):
    def __init__(self, machine, pins: Union[list, tuple]) -> None:
        """
        Create a L293D Driver object. Supports up to two motors.

        :param pins: Pins this device is connected to.
                     Should follow the format 
                     (ena, in1, in2) or (ena, in1, in2, enb, in3, in4)
        """
        if len(pins) != 3 and len(pins) != 6:
            raise ValueError('Incorrect pin format')
        
        self.__motor_pin_setup = {}
        motor_pin_1 = {
            'EN': pins[0],
            'A': pins[1],
            'B': pins[2]
        }
        self.__motor_pin_setup['1'] = motor_pin_1

        motor_pin_2 = None
        if len(pins) == 6:
            motor_pin_2 = {
                'EN': pins[3],
                'A': pins[4],
                'B': pins[5]
            }
            self.__motor_pin_setup['2'] = motor_pin_2

        super().__init__(machine, self.__motor_pin_setup)



    def attach_motor(self, is_pwm: bool = False):
        """
        Attach a motor to this driver

        :param is_pwm: Enable PWM mode, allowing to motor to set speed
        :return: L293DMotor object
        """
        if len(self.motors) >= self._max_motor:
            raise RuntimeError('Driver max capacity reached.')
        
        motor_pins = self.__motor_pin_setup.get(str(len(self.motors) + 1))
        if not motor_pins:
            raise RuntimeError('Missing motor pins.')
        
        motor = L293DMotor(self, motor_pins, is_pwm)
        self._motors.append(motor)
        return motor



    def __repl__(self):
        pins = []
        for motor, pin_setup in self.__motor_pin_setup.items():
            for pin_type, pin in pin_setup.items():
                pins.append(pin)
        return f"L293D DC Driver <pins={pins}, current={len(self._motors)}, max={self._max_motor}>"
    


class L293DMotor(DcMotor):
    def __init__(self, driver, pin_setup: dict[str, str], is_pwm: bool = False) -> None:
        super().__init__(driver, pin_setup, is_pwm)
        self.__pin_setup = pin_setup



    def __repl__(self):
        return f"L293D DC Motor <pin={self.__pin_setup}, pwm_mode={self.is_pwm}, state={self.state}>"
    