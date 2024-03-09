import sys
sys.path.append('../')

from ..base import PwmDevice
import time


class ServoMotor(PwmDevice):
    def __init__(self, machine, pin: int, frequency: int = 50) -> None:
        """
        Create a RGB LED device that can change color light

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        :param frequency: Device frequency
        """
        super().__init__(machine, pin, frequency)
        self.duty_cycle = 0
        self.__min_angle_duty_cycle = (-180, 2.5)
        self.__max_angle_duty_cycle = (180, 12.5)
        self._machine = machine
        self.__angle = 0



    @property
    def angle(self):
        """
        Current angle
        """
        return self.__angle
    


    def set_angle_duty_cycle(self, min: tuple, max: tuple):
        """
        Set the minimum and maximum angle by duty cycle. \n
        Input should be a tuple in the form of (`angle`, `duty_cycle`)

        :param min: The minimum angle by duty cycle
        :param max: The maximum angle by duty cycle
        """
        self.__min_angle_duty_cycle = min
        self.__max_angle_duty_cycle = max



    def rotate(self, angle: int, wait: float = 1):
        """
        Rotate servo at a given angle

        :param angle: Angle to turn servo to
        :param wait: Seconds to wait for rotation to complete
        """
        min_angle = self.__min_angle_duty_cycle[0]
        min_duty_cycle = self.__min_angle_duty_cycle[1]
        max_angle = self.__max_angle_duty_cycle[0]
        max_duty_cycle = self.__max_angle_duty_cycle[1]

        if angle < min_angle:
            raise ValueError('Angle is lower than allowed minimum angle')
        
        if angle > max_angle:
            raise ValueError('Angle is higher than the allowed maximum angle')

        duty_cycle = self.__map_angle_to_duty_cycle(angle, min_duty_cycle, 
                                                   max_duty_cycle, min_angle, max_angle)
        self.start(duty_cycle)
        time.sleep(wait)
        self.stop()



    def __map_angle_to_duty_cycle(self, angle, min_duty, max_duty, min_angle, max_angle):
        angle = max(min_angle, min(max_angle, angle))
        mapped_duty_cycle = ((angle - min_angle) / (max_angle - min_angle)) * (max_duty - min_duty) + min_duty
        return mapped_duty_cycle
    


    def cleanup(self):
        """
        Perform cleanup
        """
        self.rotate(0)
        


    def __repr__(self):
        min_angle = self.__min_angle_duty_cycle[0]
        max_angle = self.__max_angle_duty_cycle[0]
        return f"Servo Motor <pin={self.pin}, angle={self.__angle}, min={min_angle}, max={max_angle}>"
    