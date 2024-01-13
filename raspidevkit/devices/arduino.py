from .arduino.arduino_led import ArduinoLed
from raspidevkit.machineutils import dictutils, formatutil
from raspidevkit.constants import SERIAL_TERMINATOR
from typing import Union
from string import Template

import serial
import subprocess
import pkg_resources


class Arduino(serial.Serial):
    def __init__(self, machine, port: str | None = None, baudrate: int = 9600, **kwargs) -> None:
        """
        Initialize Arduino device

        :param machine: Machine instance as this device parent
        :param port: Port the Arduino attach to
        :param baudrate: Baudrate of serial commnication
        :param **kwargs: Other args for serial.Serial object
        """
        super().__init__(port, baudrate, **kwargs)
        self.__commands = [-1]
        self._devices = []
        self._pin_mapping = {}
        self._machine = machine



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



    def read_response(self) -> str:
        """
        Get the response from Arduino Serial COM. \n
        Uses serial.readline()

        :return: Arduino response
        """
        response = self.read_until(SERIAL_TERMINATOR.encode())
        return response.decode()
    


    def send_command(self, command: int):
        """
        Send a command to arduino.

        :param command: Command to set, usually auto-generated when attaching devices
        """
        self.write(f'{command}{SERIAL_TERMINATOR}')
        while True:
            response = self.read_response()
            if response.lower() == 'ok':
                break
        


    def _validate_pin(self, pin: Union[int, list[int]]):
        """
        Check if pin/pins is available

        :param pin: Pin to check
        :raises Exception: If pin is already in use
        """
        if isinstance(pin, int):
            if str(pin) in list(self._pin_mapping.keys()):
                raise Exception(f'Pin {pin} already in use.')
        if isinstance(pin, list):
            for p in pin:
                if str(pin) in list(self._pin_mapping.keys()):
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



    def generate_code(self, output_file: str):
        """
        Generate a code to be uploaded to Arduino
        """
        headers = ''
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

            # Append setup code
            setups += device.code['setup']

            # Create individual method and register to loop
            device_methods = device.code['methods']
            for method, code in device_methods.items():
                method_name = f'{method}_{str(device)}_{index}'
                method_name = formatutil.snake_to_camel(method_name)
                methods += f'void {method_name}() {{\n {code} }}\n'
        
            # Register to loop
            for method, command in device.commands.items():
                method_name = f'{method}_{str(device)}_{index}'
                method_name = formatutil.snake_to_camel(method_name)
                loop += f'else if(currentCommand == {command}){{ {method_name}(); }}\n\n'

        with open(template_path, 'r') as file:
            template_file = file.read()

        template_file = Template(template_file)
        content = template_file.substitute(header=headers,
                                           baudrate=self.baudrate,
                                           terminator = formatutil.escape_whitespace(SERIAL_TERMINATOR),
                                           setup=setups,
                                           loop=loop,
                                           methods=methods)
        
        with open(output_file, 'w') as file:
            file.write(content)

        if self._machine.clang_enabled:
            self.__format_code(output_file)



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
            self._machine.logger.error(f'Error formatting {file}: {e}')
            


    def attach_led(self, pin: int) -> ArduinoLed:
        """
        Attach a LED to this arduino

        :param pin: Arduino pin to attach LED to
        :return: ArduinoLed
        """
        self._validate_pin(pin)
        commands = self.generate_command_list(2)
        methods = ['turn_on', 'turn_off']
        command_map = dictutils.map_key_value(methods, commands)
        led = ArduinoLed(self, pin, command_map)
        self._devices.append(led)
        return led
