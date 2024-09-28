from ..base import SerialDevice, ArduinoDevice
from ..arduino.hall_effect_sensor import HallEffectSensor
from ..arduino.led import Led
from ..arduino.relay import Relay
from ..arduino.servo_motor import ServoMotor
from ..arduino.dht import DHT11, DHT22
from raspidevkit.utils import dictutils, stringutil, fileutil
from typing import Union
from string import Template

import subprocess
import tempfile
import pkg_resources


class Arduino(SerialDevice):
    def __init__(self, 
                 machine, 
                 port: Union[str,None] = None, 
                 baudrate: int = 9600,
                 board: str = 'Arduino Uno',
                 **kwargs) -> None:
        """
        Initialize Arduino device

        :param machine: Machine instance as this device parent
        :param port: Port the Arduino attach to
        :param baudrate: Baudrate of serial commnication
        :param **kwargs: Other args for serial.Serial object
        """
        from raspidevkit import Machine

        super().__init__(machine, port, baudrate, **kwargs)
        self.board = board
        self._cmd_terminator = '\n'
        self._data_terminator = '\r\n'
        self._whitespace_sub = '||'
        self.__commands = [-1]
        self._devices = []
        self._pin_used = []
        self.__machine: Machine = machine



    @property
    def devices(self) -> list:
        """
        Attached devices
        """
        return self._devices
    


    def cleanup(self):
        """
        Perform cleanup
        """
        self.reset_input_buffer()
        self.reset_output_buffer()
        self.close()



    def read_response(self, origin: str) -> str:
        """
        Get the response from Arduino Serial COM. \n
        Uses serial.readline()

        :param origin: Response origin can be (`cmd` or `data`)
        :return: Arduino response
        """
        if origin == 'cmd':
            terminator = self._cmd_terminator
        elif origin == 'data':
            terminator = self._data_terminator
        else:
            raise ValueError('Unknown arduino response origin')
        
        response = self.read_until(terminator.encode(), encoding='utf-8')
        return response.strip()
    


    def send_command(self, command: int):
        """
        Send a command to arduino.

        :param command: Command to set, usually auto-generated when attaching devices
        """
        while True:
            self.write(str(command) + self._cmd_terminator)
            response = self.read_response(origin='cmd')
            if 'ok' in response.lower():
                break
        


    def send_data(self, data: str):
        """
        Send a data to arduino

        :param data: Data to send
        """
        raw_data = f'{data}{self._data_terminator}'.replace(' ', self._whitespace_sub)
        while True:
            self.write(raw_data)
            response = self.read_response(origin='data')
            if 'ok' in response.lower():
                break

        

    def _validate_pin(self, pin: Union[int, list[int]]):
        """
        Check if pin/pins is available

        :param pin: Pin to check
        :raises Exception: If pin is already in use
        """
        if isinstance(pin, int):
            if pin in self._pin_used:
                raise Exception(f'Pin {pin} already in use.')
        if isinstance(pin, list):
            for p in pin:
                if p in self._pin_used:
                    raise Exception(f'Pin {pin} already in use.')
        


    def generate_command_list(self, length: int) -> list:
        """
        Generate a list of available command to use

        :param length: Command count to generate
        :return: Available command list
        """
        last_command = max(self.__commands)
        commands = list(range(last_command + 1, last_command + length + 1))
        self.__commands.extend(commands)
        return commands



    def get_attached_device_type(self, _class: ArduinoDevice) -> int:
        """
        Get the number of instances a device type is attached to this arduino

        :param _class: Arduino Device Class
        :return: Number of instance of device type
        """
        count = 0
        for device in self._devices:
            if device.__class__ == _class:
                count += 1
        return count



    def generate_code(self, output_file: str):
        """
        Generate a code to be uploaded to Arduino
        """
        headers = ''
        global_vars = ''
        setups = ''
        methods = ''
        loop = ''
        template_path = pkg_resources.resource_filename('raspidevkit', 
                                                        'templates/arduino_template.ino')
        for index, device in enumerate(self._devices):
            # Add libraries if any
            libraries = device.code['libraries']
            if libraries:
                for library in libraries:
                    headers += f'#include <{library}>\n'

            # Add global variables
            global_vars += device.code['global']

            # Append setup code
            setups += device.code['setup']

            # Create individual method and register to loop
            device_methods = device.code['methods']
            for method, code in device_methods.items():
                method_name = f'{method}_{str(device)}_{index}'
                method_name = stringutil.snake_to_camel(method_name)
                methods += f'void {method_name}() {{\n {code} }}\n'
        
            # Register to loop
            for method, command in device.commands.items():
                method_name = f'{method}_{str(device)}_{index}'
                method_name = stringutil.snake_to_camel(method_name)
                loop += f'else if(currentCommand == {command}){{ {method_name}(); currentCommand = -1;}}\n\n'

        with open(template_path, 'r') as file:
            template_file = file.read()

        template_file = Template(template_file)
        content = template_file.substitute(header=headers,
                                           global_vars = global_vars,
                                           baudrate=self.baudrate,
                                           cmd_terminator = stringutil.escape_whitespace(self._cmd_terminator),
                                           data_terminator = stringutil.escape_whitespace(self._data_terminator),
                                           whitespace_sub = stringutil.escape_whitespace(self._whitespace_sub),
                                           setup=setups,
                                           loop=loop,
                                           methods=methods)
        
        with open(output_file, 'w') as file:
            file.write(content)

        if self.__machine.arduino_cli.formatting:
            self.__format_code(output_file)



    def compile(self, fresh: bool = False):
        """
        Generates, compile and upload code to the arduino
          NOTE: Devices that are only attached up to this point
                are in included in the sketch.

        :param fresh: Bypass hash checking, will always compile sketch
        """
        name = 'raspidevkit.ino'
        raspidevkit_folder = 'raspidevkit'
        temp_dir = tempfile.gettempdir()
        sketch_path = fr'{temp_dir}/{raspidevkit_folder}'
        if not fileutil.does_path_exists(sketch_path):
            fileutil.create_directory(sketch_path)
        file_name = fr'{sketch_path}/{name}'
        previous_hash = ''
        if fileutil.does_file_exists(file_name):
            previous_hash = fileutil.get_file_hash(file_name)
        self.generate_code(file_name)
        current_hash = fileutil.get_file_hash(file_name)

        if previous_hash == current_hash and not fresh:
            self.__machine.logger.info('Generated code matched with previously generated code. Skipping upload')
            return
        fbqn = self.__machine.arduino_cli.get_boards()[self.board]
        self.close()
        self.__machine.arduino_cli.upload_code(sketch_path, self.port, fbqn)
        self.open()



    def __format_code(self, file):
        """
        Format file to C++ formatting with Clang-format
        """
        format_file = pkg_resources.resource_filename('raspidevkit', 'templates/.clang-format')

        try:
            subprocess.run(['clang-format', '-i', file, 
                            f'-style=file:{format_file}'], 
                           check=True, 
                           shell=True)
        except subprocess.CalledProcessError as e:
            self.__machine.logger.error(f'Error formatting {file}: {e}')
            


    def attach_hall_effect_sensor(self, pin: int) -> HallEffectSensor:
        """
        Attach a hall effect sensor to this arduino
        :param pin: Arduino pin to attach hall effect sensor to
        :return: ArduinoHallEffectSensor
        """
        self._validate_pin(pin)
        self._pin_used.append(pin)
        commands = self.generate_command_list(1)
        methods = ['read']
        command_map = dictutils.map_key_value(methods, commands)
        hall_effect_sensor = HallEffectSensor(self, pin, command_map)
        self._devices.append(hall_effect_sensor)
        return hall_effect_sensor
    


    def attach_led(self, pin: int) -> Led:
        """
        Attach a LED to this arduino

        :param pin: Arduino pin to attach LED to
        :return: ArduinoLed
        """
        self._validate_pin(pin)
        self._pin_used.append(pin)
        commands = self.generate_command_list(2)
        methods = ['turn_on', 'turn_off']
        command_map = dictutils.map_key_value(methods, commands)
        led = Led(self, pin, command_map)
        self._devices.append(led)
        return led



    def attach_relay(self, pin: int) -> Relay:
        """
        Attach a relay to this arduino

        :param pin: Arduino pin to attach relay to
        :return: ArduinoRelay
        """
        self._validate_pin(pin)
        self._pin_used.append(pin)
        commands = self.generate_command_list(2)
        methods = ['turn_on', 'turn_off']
        command_map = dictutils.map_key_value(methods, commands)
        relay = Relay(self, pin, command_map)
        self._devices.append(relay)
        return relay
    


    def attach_servo_motor(self, pin: int) -> ServoMotor:
        """
        Attach a servo motor to this arduino

        :param pin: Arduino pin to attach servo motor to
        :return: ServoMotor
        """
        self._validate_pin(pin)
        self._pin_used.append(pin)
        commands = self.generate_command_list(1)
        methods = ['rotate']
        uuid = self.get_attached_device_type(ServoMotor) + 1
        command_map = dictutils.map_key_value(methods, commands)
        servo_motor = ServoMotor(self, pin, command_map, uuid=uuid)
        self._devices.append(servo_motor)
        return servo_motor
    


    def attach_dht11(self, pin: int) -> DHT11:
        """
        Attach a DHT11 sensor to this arduino

        :param pin: Arduino pin to attach DHT11 sensor to
        :return: DHT11
        """
        self._validate_pin(pin)
        self._pin_used.append(pin)
        commands = self.generate_command_list(3)
        methods = ['get_data', 'get_temperature', 'get_humidity']
        uuid = self.get_attached_device_type(DHT11) + 1
        command_map = dictutils.map_key_value(methods, commands)
        dht11 = DHT11(self, pin, command_map, uuid=uuid)
        self._devices.append(dht11)
        return dht11



    def attach_dht22(self, pin: int) -> DHT22:
        """
        Attach a DHT22 sensor to this arduino

        :param pin: Arduino pin to attach DHT22 sensor to
        :return: DHT22
        """
        self._validate_pin(pin)
        self._pin_used.append(pin)
        commands = self.generate_command_list(3)
        methods = ['get_data', 'get_temperature', 'get_humidity']
        uuid = self.get_attached_device_type(DHT22) + 1
        command_map = dictutils.map_key_value(methods, commands)
        dht22 = DHT22(self, pin, command_map, uuid=uuid)
        self._devices.append(dht22)
        return dht22
