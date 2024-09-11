import sys
sys.path.append('../')

from ..base import GpioDevice
from raspidevkit.utils import mathutil
from raspidevkit.constants import INPUT, OUTPUT, PULL_DOWN
from typing import Tuple, Optional
import time
    

class DHTSensor(GpioDevice):
    def __init__(self, machine, pin: int):
        """
        Create a dht sensor object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        pin_setup = {
            str(pin): PULL_DOWN
        }
        super().__init__(machine, pin_setup, device_type=INPUT)



    def get_data(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get temperature and humidity from the sensor

        :return: temperature, humidity
        """
        data = []
        tmp = 0

        self.__send_start_signal()
        while not self.gpio_read():
            continue
        while self.gpio_read():
            continue

        while tmp < 40:
            counter = 0
            while not self.gpio_read():
                continue
            while self.gpio_read():
                counter += 1
                if counter > 100:
                    break
            if counter < 8:
                data.append(0)
            else:
                data.append(1)
            tmp += 1

        humidity_bit = data[0:8]
        humidity_point_bit = data[8:16]
        temperature_bit = data[16:24]
        temperature_point_bit = data[24:32]
        checksum_bit = data[32:40]

        humidity = mathutil.bits_to_int(humidity_bit, 2)
        humidity_point = mathutil.bits_to_int(humidity_point_bit, 2)
        temperature = mathutil.bits_to_int(temperature_bit, 2)
        temperature_point = mathutil.bits_to_int(temperature_point_bit, 2)
        checksum = mathutil.bits_to_int(checksum_bit, 2)

        valid = self.__verify_checksum(checksum, humidity, humidity_point, 
                                       temperature, temperature_point)
        
        if valid:
            return float(temperature), float(humidity)
        
        return None, None
    


    def get_temperature(self) -> float:
        """
        Get temperature from the sensor

        :return: Temperature
        """
        temperature, _ = self.get_data()
        return temperature
    


    def get_humidity(self) -> float:
        """
        Get humidity from the sensor

        :return: Humidity
        """
        _, humidity = self.get_data()
        return humidity



    def __send_start_signal(self):
        """
        Send start signal to the sensor
        """
        self.gpio_setup(self.pin, OUTPUT)
        self.gpio_write(self.pin, True)
        time.sleep(0.025)
        self.gpio_write(self.pin, False)
        time.sleep(0.02)
        self.gpio_setup(self.pin, INPUT)



    def __verify_checksum(self, *args) -> bool:
        """
        Verify checksum from data
        """
        checksum = args[0]
        total = sum(args) - checksum
        return checksum == (total & 0xFF)



    def __repr__(self):
        return f"DHT Sensor <pin={self.pin}>"
    


class DHT11(DHTSensor):
    def __init__(self, machine, pin: int):
        """
        Create a DHT11 object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        super().__init__(machine, pin)



    def __repr__(self):
        return f"DHT11 <pin={self.pin}>"



class DHT22(DHTSensor):
    def __init__(self, machine, pin: int):
        """
        Create a DHT22 object

        :param machine: Machine instance as this device parent
        :param pin: Pin this device is attached to
        """
        super().__init__(machine, pin)



    def __repr__(self):
        return f"DHT22 <pin={self.pin}>"
    