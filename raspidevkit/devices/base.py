from ..constants import INPUT, OUTPUT, PULL_UP, PULL_DOWN
from ..utils import stringutil

from typing import Union
import serial
import sys

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO


class GpioDevice:
    def __init__(self, machine, pin_setup: dict, device_type: str) -> None:
        """
        Create a GPIO device. Pin setup can include both input and output.

        :param machine: Machine instance
        :param pin_setup: Pin setup configuration with keys as pins and values as mode
        :param mode: Pin setup mode, can be `INPUT`, `PULL_UP`, `PULL_DOWN`, or `OUTPUT`
        :param device_type: This device device_type `INPUT` or `OUTPUT`

        Example config:
        ```python
        "setup": {
            "14": INPUT,
            "15": PULL_UP,
            "17": PULL_DOWN,
            "24": OUTPUT
        }
        ```
        """
        from raspidevkit import Machine

        self.__machine: Machine = machine
        for pin, setup in pin_setup.items():
            self.__machine.gpio.setup(int(pin), setup)
        
        self.__multi_pin = False
        if len(pin_setup.keys()) > 1:
            self.__multi_pin = True
        
        if self.__multi_pin:
            self.__pins = tuple([int(pin) for pin in pin_setup.keys()])
        else:
            self.__pin = int(list(pin_setup.keys())[0])
        self._device_type = device_type


    
    @property
    def device_type(self) -> str:
        """
        This device type
        """
        return self._device_type



    @property
    def pin(self) -> int:
        """
        Device pin, if single pin
        """
        if self.__multi_pin:
            raise Exception('This is not accessible for multi-pin device. Use pins instead')
        return self.__pin
    


    @property
    def pins(self) -> tuple[int]:
        """
        Device pins, if multi-pin
        """
        if not self.__multi_pin:
            raise Exception('This is not accessible for single-pin device. Use pin instead')
        return self.__pins



    def gpio_setup(self, pin: int,  setup: str):
        """
        Explicitly setup a GPIO pin

        :param pin: Pin to setup
        :param setup: Pin mode (INPUT or OUTPUT)
        """
        if not self.__multi_pin and pin != self.pin:
            raise ValueError('Pin not mapped to device')
        
        if self.__multi_pin and pin not in self.__pins:
            raise ValueError('Pin not mapped to device')
        
        return self.__machine.gpio.setup(pin, setup)



    def gpio_write(self, pin: int, value: bool):
        """
        Perform a GPIO output on pin

        :param pin: The pin to write
        :param value: Can be HIGH or LOW
        :raises ValueError: If pin is not the device pin
        """
        if not self.__multi_pin and pin != self.pin:
            raise ValueError('Pin not mapped to device')
        
        if self.__multi_pin and pin not in self.__pins:
            raise ValueError('Pin not mapped to device')
        
        return self.__machine.gpio.write(pin, value)



    def gpio_read(self, pin: int) -> bool:
        """
        Read the value from a GPIO pin
        
        :param pin: The pin to read
        :return: Value, either True of False
        """
        if not self.__multi_pin and pin != self.pin:
            raise ValueError('Pin not mapped to device')
        
        if self.__multi_pin and pin not in self.__pins:
            raise ValueError('Pin not mapped to device')
        
        return self.__machine.gpio.read(pin)



    def cleanup(self):
        """
        Perform cleanup
        """
        pass



class PwmDevice(GPIO.PWM):
    def __init__(self, machine, pin: int, frequency: float) -> None:
        """
        Create a PWM device

        :param machine: Machine instance
        :param pin: Pin this device is attached to
        :param frequency: Device frequency
        """
        from raspidevkit import Machine

        self.__machine: Machine = machine
        self.__machine.gpio.setup(pin, OUTPUT)
        super().__init__(pin, frequency)
        self.__pin = pin
        self.__frequency = frequency
        self.__duty_cycle = None
        self.__multi_pin = False
        self._device_type = OUTPUT
        self._state = False

    

    @property
    def device_type(self) -> str:
        """
        This device type
        """
        return self._device_type
    

    
    @property
    def pin(self) -> int:
        """
        Device pin, if single pin
        """
        if self.__multi_pin:
            raise Exception('This is not accessible for multi-pin device. Use pins instead')
        return self.__pin
    


    @property
    def frequency(self) -> int:
        """
        Device frequency
        """
        return self.__frequency
    


    @frequency.setter
    def frequency(self, frequency: int):
        self.change_frequency(frequency)



    @property
    def duty_cycle(self) -> float:
        """
        Device duty cycle
        """
        return self.__duty_cycle
    


    @duty_cycle.setter
    def duty_cycle(self, duty_cycle: float):
        self.ChangeDutyCycle(duty_cycle)
        self.__duty_cycle = duty_cycle



    def start(self, duty_cycle: float):
        """
        Start device

        :param duty_cycle: Duty cycle
        """
        if not self._state:
            super().start(duty_cycle)
            self.__duty_cycle = duty_cycle
            self._state = True



    def stop(self):
        """
        Stop device
        """
        if self._state:
            super().stop()
            self.__duty_cycle = None
            self._state = False



    def change_frequency(self, frequency: int):
        """
        Change device frequency

        :param frequency: New frequency
        """
        if self._state:
            self.ChangeFrequency(frequency)
            self.__frequency = frequency


        
    def cleanup(self):
        """
        Perform cleanup
        """
        self.stop()
    


class I2CDevice:
    def __init__(self, machine, address: int) -> None:
        """
        Create an I2C device

        :param machine: Machine instance
        :param address: Device I2C address
        """
        from raspidevkit import Machine
        
        self.__address = address
        self.__machine: Machine = machine


    
    @property
    def address(self) -> int:
        """
        Device I2C address
        """
        return self.__address
    

    
    def read_byte(self, force: bool = False) -> int:
        """
        Read a single byte from an I2C address.

        :param force: Force read flag
        :return: Read byte value
        """
        return self.__machine.i2c.read_byte(self.__address, force)
    


    def read_word_data(self, register: int, force: bool = False) -> int:
        """
        Read a single word (2 bytes) from a given register

        :param register: Register address
        :param force: Force read flag
        :return: 2-byte word
        """
        return self.__machine.i2c.read_word_data(self.__address, register, force)
    


    def read_byte_data(self, register: int, force: bool = False) -> int:
        """
        Read a single byte from a designated register
        
        :param register: Register address
        :param force: Force read flag
        :return: Read byte value
        """
        return self.__machine.i2c.read_byte_data(self.__address, register, force)
    


    def read_block_data(self, register: int, length: int = 32, 
                        force: bool = False) -> list[int]:
        """
        Read a block of data from a given register

        :param register: Register address
        :param length: Block length, default to 32 bytes
        :param force: Force read flag
        :return: List of bytes
        """
        return self.__machine.i2c.read_block_data(self.__address, register, length, force)
    


    def write_byte(self, value: int, force: bool = False):
        """
        Write a single byte to an I2C address

        :param value: Value to write
        :param force: Force write flag
        """
        self.__machine.i2c.write_byte(self.__address, value, force)



    def write_word_data(self, register: int, value:int, force: bool = False):
        """
        Write a single word (2 bytes) to a given register

        :param register: Register address
        :param value: Word value to write
        :param force: Force write flag
        """
        self.__machine.i2c.write_word_data(register, value, force)


        
    def write_byte_data(self, register: int, value: int, force: bool = False):
        """
        Write a byte to a given register

        :param register: Register address
        :param value: Byte value to write
        :param force: Force write flag
        """
        self.__machine.i2c_write_byte_data(self.__address, register, value, force)


    
    def write_block_data(self, register: int, data: list[int], 
                         force: bool = False):
        """
        Write a block of byte data to a given register

        :param register: Register address
        :param data: List of byte values to write
        :param force: Force write flag
        """
        self.__machine.i2c.write_block_data(self.__address, register, data, force)



    def cleanup(self):
        """
        Perform cleanup
        """
        pass



class SerialDevice(serial.Serial):
    def __init__(self, machine, port: Union[str, None] = None, 
                 baudrate: int = 9600, **kwargs) -> None:
        """
        Create a serial device

        :param machine: Machine instancce
        :param port: Serial port to use
        :param baudrate: Serial communication baudrate
        :param **kwargs: Other args for serial.Serial object
        """
        from raspidevkit import Machine

        super().__init__(port, baudrate, **kwargs)
        self.__machine: Machine = machine


    
    def write(self, data: Union[str, bytes], encoding: str = 'utf-8') -> Union[int, None]:
        """
        Output the given byte string over the serial port.
        String data is automatically encoded

        :param data: String data to send
        """
        if isinstance(data, str):
            data = bytes(data, encoding)
        self.__machine.logger.debug(f'[SERIAL][WRITE] Attempting write on {self.port}: {data}')
        output =  super().write(data)
        self.__machine.logger.debug(f'[SERIAL][WRITE] Returned: {output}')
        return output



    def read(self, size: int = 1, 
             encoding: Union[str, None] = None) -> Union[bytes, str]:
        """
        Read size bytes from the serial port. 
        If a timeout is set it may return less characters as requested. 
        With no timeout it will block until the requested number of bytes is read.

        :param size: Byte size to read
        :param encoding: If given, decodes output to given encoding format
        """
        self.__machine.logger.debug(f'[SERIAL][READ] Attempting read on {self.port}:{size}')
        output =  super().read(size)
        if encoding:
            output = output.decode(encoding)
        self.__machine.logger.debug(f'[SERIAL][READ] Returned: {output}')
        return output
    


    def read_until(self, expected: bytes = b"\n", 
                   size: Union[int, None] = None, 
                   encoding: Union[str, None] = None) -> bytes:
        """
        Read until an expected sequence is found (' ' by default), the size
        is exceeded or until timeout occurs.

        :param expected: Sequence to end reading
        :param size: Byte size to read
        :param encoding: If given, decodes output to given encoding format
        """
        self.__machine.logger.debug(f'[SERIAL][READ] Attempting read on {self.port}:{expected}:{size}')
        output =  super().read_until(expected, size)
        if encoding:
            output = output.decode(encoding)
        self.__machine.logger.debug(f'[SERIAL][READ] Returned: {output}')
        return output
    


    def read_all(self, encoding: Union[str, None] = None) -> Union[bytes, None]:
        """
        Read all bytes currently available in the buffer of the OS.

        :param encoding: If given, decodes output to given encoding format
        """
        self.__machine.logger.debug(f'[SERIAL][READ] Attempting read on {self.port}:all')
        output =  super().read_all()
        if encoding:
            output = output.decode(encoding)
        self.__machine.logger.debug(f'[SERIAL][READ] Returned: {output}')
        return output



class ArduinoDevice:
    def __init__(self, arduino, pin_setup: dict, device_type: str, 
                 commands: dict[str, Union[str, int]], uuid: str = '') -> None:
        """
        Create a Arduino device.

        :param arduino: Arduino master
        :param pin_setup: Config dictionary of pin mode, can be `INPUT`,`PULL_UP`, 
            \t`PULL_DOWN`, `OUTPUT` or `custom`. When custom, the setup method 
            \tcan be overriden
        :param device_type: This device device_type `INPUT`or `OUTPUT`
        :param commands: Dictionary of commands with methods as keys.
        :param uuid: Optional UUID, if not given would randomly generate
        Sample command configuration:
        ```python
        commands = {
            "turnOn": 1,
            "turnOff": 2
        }
        ```
        """
        from .serial.arduino import Arduino

        self._arduino: Arduino = arduino
        self._setup_code = ""
        for pin in pin_setup.keys():
            if pin_setup[pin] == INPUT:
                self._setup_code += f'pinMode({pin}, INPUT);\n'
            elif pin_setup[pin] == PULL_UP:
                self._setup_code += f'pinMode({pin}, INPUT_PULLUP);\n'
            elif pin_setup[pin] == PULL_DOWN:
                self._setup_code += f'pinMode({pin}, INPUT_PULLDOWN);\n'
            elif pin_setup[pin] == OUTPUT:
                self._setup_code += f'pinMode({pin}, OUTPUT);\n'
            elif pin_setup[pin] == 'custom':
                pass
            else:
                raise ValueError(f'Invalid value for pin {pin}')
            
        if uuid:
            self.__uuid = uuid
        else:
            self.__uuid = stringutil.generate_string(8)

        self.__multi_pin = False
        if len(pin_setup.keys()) > 1:
            self.__multi_pin = True
        
        if self.__multi_pin:
            self.__pins = tuple([int(pin) for pin in dict.keys()])
        else:
            self.__pin = int(list(pin_setup.keys())[0])

        self._device_type = device_type
        self._methods = list(commands.keys())
        self._commands = commands
        self._code_mapping = {
            'libraries' : [],
            'global': '',
            'setup': self._setup_code,
            'methods': {}
        }



    @property
    def uuid(self) -> str:
        """
        Device UUID
        """
        return self.__uuid
    

    
    @property
    def device_type(self) -> str:
        """
        This device type
        """
        return self._device_type



    @property
    def pin(self) -> int:
        """
        Device pin, if single pin
        """
        if self.__multi_pin:
            raise Exception('This is not accessible for multi-pin device. Use pins instead')
        return self.__pin
    


    @property
    def pins(self) -> tuple[int]:
        """
        Device pins, if multi-pin
        """
        if not self.__multi_pin:
            raise Exception('This is not accessible for single-pin device. Use pin instead')
        return self.__pins



    @property
    def code(self) -> dict:
        """
        Code mapping
        """
        return self._code_mapping
    


    @property
    def commands(self) -> dict[str, int]:
        """
        Commands available to this device
        """
        return self._commands
    


    def validate_commands(self, keys: list):
        """
        Validate the commands parameter pass. All required
        key should be present.
        """
        for key in keys:
            if key not in self._commands.keys():
                raise Exception(f'Key {key} is not present in commands')



    def _map_method_code(self):
        """
        Create method code mapping
        """
        pass



    def cleanup(self):
        """
        Perform cleanup
        """
        pass
