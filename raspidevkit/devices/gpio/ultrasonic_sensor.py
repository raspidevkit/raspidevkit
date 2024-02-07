import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.constants import INPUT, OUTPUT
from raspidevkit.machineutils import mathutil
import time


class UltrasonicSensor(GpioDevice):
    def __init__(self, machine, pins: tuple[int, str]) -> None:
        """
        Create am ultrasonic sensor device

        :param machine: Machine instance as this device parent
        :param pins: Tuple of pins to use, in RGB order (trigger, echo)
        """
        if len(pins) != 2:
            raise ValueError("Pins should have 2 values.")
        
        pin_setup = {
            str(pins[0]): OUTPUT,
            str(pins[1]): INPUT,
        }
        super().__init__(machine, pin_setup, device_type=INPUT)
        self.__trigger_pin = pins[0]
        self.__echo_pin = pins[1]


    
    def get_distance(self, measure: str = 'cm') -> float:
        """
        Get the distance of an object from the sensor

        :param measure: Unit of measurement (`cm`, `inch`, `ft`, `m`)
        :return: Distance of object
        """
        self.gpio_write(self.__trigger_pin, True)
        time.sleep(0.00001)
        self.gpio_write(self.__trigger_pin, False)

        start = time.time()
        end = time.time()

        while not self.gpio_read(self.__echo_pin):
            start = time.time()

        while self.gpio_read(self.__echo_pin):
            end = time.time()
        
        elapsed = end - start
        distance = (elapsed * 34300) / 2
        converted_distance = mathutil.convert_distance(distance, 'cm', measure)
        return converted_distance
    


    def __repr__(self) -> str:
        return f"Ultrasonic Sensor <pins={self.pins}"
    