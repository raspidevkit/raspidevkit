from ..base import ArduinoDevice
from raspidevkit.constants import INPUT
from typing import Tuple, Optional, Union
import time


class DHTSensor(ArduinoDevice):
    def __init__(self, arduino, pin: int, dtype: str, commands: dict[str, Union[str, int]]) -> None:
        """
        Create a LED object attached to Arduino

        :param arduino: Arduino master
        :param pin: Pin to attach DHT sensor in Arduino
        :param dtype: DHT sensor type
        :param commands: Dictionary of commands with methods as keys.
        Required command configuration:
        ```python
        commands = {
            "get_data": 1,
            "get_temperature": 2,
            "get_humidity": 3
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
            'get_data',
            'get_temperature',
            'get_humidity'
        ]
        self.__var_name = f'dht{self.uuid}'
        self.validate_commands(all_methods)
        self._method_code = self._map_method_code()

        self.__type = dtype
        self._state = False
        self._code_mapping['libraries'] = ['DHT.h']
        self._code_mapping['global'] = f'DHT {self.__var_name} = DHT({pin},{dtype});'
        self._code_mapping['setup'] = f'{self.__var_name}.begin();'
        self._code_mapping['methods'] = self._method_code

    
    def _map_method_code(self):
        """
        Create method code mapping
        """
        get_data_code = f'sendResponse(String({self.__var_name}.readTemperature()) + " " + String({self.__var_name}.readHumidity()));'
        get_temperature_code = f'sendResponse(String({self.__var_name}.readTemperature()));'
        get_humidity_code = f'sendResponse(String({self.__var_name}.readHumidity()));'

        method_code = {
            'get_data': get_data_code,
            'get_temperature': get_temperature_code,
            'get_humidity': get_humidity_code
        }
        return method_code



    def get_data(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get temperature and humidity from the sensor
        :return: temperature, humidity
        """
        command = self._commands.get('get_data')
        self._arduino.send_command(command)
        response = self._arduino.read_response(origin='cmd')
        data = response.split()
        try:
            temperature = float(data[0])
            humidity = float(data[1])
            return temperature, humidity
        except:
            raise Exception('Sensor read fail')



    def get_temperature(self) -> float:
        """
        Get temperature from the sensor
        :return: Temperature
        """
        command = self._commands.get('get_temperature')
        self._arduino.send_command(command)
        response = self._arduino.read_response(origin='cmd')
        try:
            temperature = float(response)
            return temperature
        except:
            raise Exception('Sensor read fail')
        


    def get_humidity(self) -> float:
        """
        Get humidity from the sensor
        :return: Humidity
        """
        command = self._commands.get('get_humidity')
        self._arduino.send_command(command)
        response = self._arduino.read_response(origin='cmd')
        try:
            humidity = float(response)
            return humidity
        except:
            raise Exception('Sensor read fail')
        


    def __str__(self):
        """
        Device name
        """
        return "dht_sensor"
    


    def __repr__(self):
        return f"Arduino DHT Sensor <pin={self.pin}, type={self.__type}>"



class DHT11(DHTSensor):
    def __init__(self, arduino, pin: int, 
                 commands: dict[str, Union[str, int]], uuid: str = ''):
        """
        Create a DHT11 object
        :param arduino: Arduino instance as this device parent
        :param pin: Pin this device is attached to
        :param commands: Dictionary of commands with methods as keys.
        """
        super().__init__(arduino=arduino,
                         pin=pin,
                         dtype='DHT11',
                         commands=commands)




    def __repr__(self):
        return f"DHT11 <pin={self.pin}>"
    


class DHT22(DHTSensor):
    def __init__(self, arduino, pin: int, 
                 commands: dict[str, Union[str, int]], uuid: str = ''):
        """
        Create a DHT22 object
        :param arduino: Arduino instance as this device parent
        :param pin: Pin this device is attached to
        :param commands: Dictionary of commands with methods as keys.
        """
        super().__init__(arduino=arduino,
                         pin=pin,
                         dtype='DHT22',
                         commands=commands)




    def __repr__(self):
        return f"DHT22 <pin={self.pin}>"