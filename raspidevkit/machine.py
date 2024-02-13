from .machineutils import dictutils, fileutil
from .__logger import MachineLogger
from .constants import INPUT, PULL_UP, PULL_DOWN, OUTPUT
from typing import Union
from .devices import (
    ActiveBuzzer,
    Arduino,
    Button,
    Led,
    L298NDriver,
    LightSensor,
    PassiveBuzzer,
    PIRMotionSensor,
    Relay,
    RgbLed,
    ServoMotor,
    Sim808,
    UltrasonicSensor
)

import sys
import subprocess
import logging
import time

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO


class Machine:
    def __init__(self, 
                 gpio_mode: str = 'BCM',
                 i2cbus: Union[None, int] = None,
                 enable_logging: bool = False,
                 debug: bool = False,
                 arduino_cli_path: Union[None, str] = None,
                 **kwargs) -> None:
        '''
        Create a machine class which different devices can be created from.

        :param gpio_mode: GPIO mode can be `BCM` or `BOARD` as `GPIO.setmode()`
        :param i2cbus: I2C bus to use, defaults to 1
        :param enable_logging: Enable logging, configuration can be set by passing in a config dictionary
        :param debug: Set debug to true
        :param arduino_cli_path: Path to Arduino CLI
        :param config: Config dictionary which will take priority. See sample config.
        '''
        default_config = {
            'logging': {
                'format': '%(asctime)s [%(levelname)s] - %(message)s.',
                'file': 'machine.log',
                'level': logging.INFO if not debug else logging.DEBUG
            }
        }

        self._config = kwargs.get('config', default_config)
        if gpio_mode.upper() == 'BCM':
            GPIO.setmode(GPIO.BCM)
        elif gpio_mode.upper() == 'BOARD':
            GPIO.setmode(GPIO.BCM)
        else:
            raise ValueError('GPIO mode can only be BCM or BOARD.')
        
        self.__i2c_enabled = False
        if i2cbus is not None:
            import smbus2
            self.__i2cbus = smbus2.SMBus(i2cbus)
            self.__i2c_enabled = True

        self.logger = None
        self.__intialize_logger(enable_logging, debug)
        self.__clang_enabled = self.__is_clang_format_installed()
        self.__arduino_cli_installed = self.__is_arduino_cli_installed(arduino_cli_path)
        self.__arduino_cli_path = arduino_cli_path if self.__arduino_cli_installed else None

        self._devices = []
        self._pin_mapping = []



    @property
    def i2c_enabled(self) -> bool:
        """
        I2C interface enabled
        """
        return self.__i2c_enabled
    


    @property
    def clang_enabled(self) -> bool:
        """
        Clang format installed
        """
        return self.__clang_enabled
    


    @property
    def arduino_cli_installed(self) -> bool:
        """
        Arduino CLI installed
        """
        return self.__arduino_cli_installed
    


    @property
    def arduino_cli_path(self) -> Union[None, str]:
        """
        Arduino CLI path
        """
        return self.__arduino_cli_path
    


    @property
    def devices(self) -> list:
        """
        Attached devices
        """
        return self._devices
    


    def __intialize_logger(self, enabled: bool, debug: bool):
        """
        Initialize logger. `debug` variable will take priority
        """
        default_format = '%(asctime)s [%(levelname)s] - %(message)s.'
        default_file = 'machine.log'
        format = dictutils.get(self._config, 'logging', 'format', default=default_format)
        file = dictutils.get(self._config, 'logging', 'file', default=default_file)
        if not debug:
            level = dictutils.get(self._config, 'logging', 'level', default=logging.INFO)
        else:
            level = logging.DEBUG

        logging_format = logging.Formatter(format)
        main_handler = logging.FileHandler(file)
        main_handler.setFormatter(logging_format)
        self.logger = MachineLogger(__name__, enabled=enabled or debug)
        self.logger.addHandler(main_handler)
        self.logger.setLevel(level)
        self.logger.info('Logger initialized.')
    


    def __is_clang_format_installed(self):
        try:
            subprocess.run(['clang-format', '--version'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True, 
                           shell=True)
            self.logger.info('Clang-format found.')
            return True
        except subprocess.CalledProcessError:
            self.logger.warning('Clang-format not found. Arduino generated code will not be formatted')
            return False
        


    def __is_arduino_cli_installed(self, arduino_cli_path: str):
        try:
            subprocess.run(['arduino-cli', 'version'],
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True,
                           cwd=arduino_cli_path,
                           shell=True)
            self.logger.info('Arduino CLI found.')
            return True
        except subprocess.CalledProcessError:
            self.logger.warning('Arduino CLI not found.')
            return False



    ######################################################
    #                                                    #
    #                   GPIO Interface                   #
    #                                                    #
    ######################################################
        

    def gpio_setup(self, pin: int,  setup: str):
        """
        Explicitly setup a GPIO pin

        :param pin: Pin to setup
        :param setup: Pin mode (INPUT or OUTPUT)
        """
        self.logger.debug(f'[GPIO][SETUP] {pin}:{setup}')
        if setup.upper() == INPUT:
            GPIO.setup(pin, GPIO.IN)
        elif setup.upper() == PULL_UP:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        elif setup.upper() == PULL_DOWN:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        elif setup.upper() == OUTPUT:
            GPIO.setup(pin, GPIO.OUT)
        else:
            raise ValueError('Invalid pin mode')
        


    def gpio_write(self, pin: int, value: bool):
        """
        Perform a GPIO output on a pin

        :param pin: The pin to write
        :param value: Can be HIGH or LOW
        """
        self.logger.debug(f'[GPIO][WRITE] Write on {pin}: {value}')
        if value:
            GPIO.output(pin, GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.LOW)



    def gpio_read(self, pin: int) -> bool:
        """
        Read the value from a GPIO pin
        
        :param pin: The pin to read
        :return: Value, either True of False
        """
        self.logger.debug(f'[GPIO][READ] Read on: {pin}')
        value = GPIO.input(pin)
        self.logger.debug(f'[GPIO][READ] Value from {pin}: {value}')
        return value



    ######################################################
    #                                                    #
    #                   I2C Interface                    #
    #                                                    #
    ######################################################


    def i2c_read_byte(self, address: int, force: bool = False) -> int:
        """
        Read a single byte from an I2C address.

        :param address: Device I2C address
        :param force: Force read flag
        :return: Read byte value
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][READ] Read on {address}')
        value = self.__i2cbus.read_byte(address, force)
        self.logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def i2c_read_word_data(self, address: int, register: int, 
                           force: bool = False) -> int:
        """
        Read a single word (2 bytes) from a given register

        :param address: Device I2C address
        :param register: Register address
        :param force: Force read flag
        :return: 2-byte word
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][READ] Read word data on {address}-{register}')
        value = self.__i2cbus.read_word_data(address, register, force)
        self.logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def i2c_read_byte_data(self, address: int, register: int, 
                           force: bool = False) -> int:
        """
        Read a single byte from a designated register
        
        :param address: Device I2C address
        :param register: Register address
        :param force: Force read flag
        :return: Read byte value
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][READ] Read byte data on {address}-{register}')
        value = self.__i2cbus.read_byte_data(address, register, force)
        self.logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def i2c_read_block_data(self, address: int, register: int, 
                            length: int = 32, force: bool = False) -> list[int]:
        """
        Read a block of data from a given register

        :param address: Device I2C address
        :param register: Register address
        :param length: Block length, default to 32 bytes
        :param force: Force read flag
        :return: List of bytes
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][READ] Read block data ({length}) on {address}-{register}')
        value = self.__i2cbus.read_i2c_block_data(address, register, length, force)
        self.logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def i2c_write_byte(self, address: int, value: int, force: bool = False):
        """
        Write a single byte to an I2C address

        :param address: Device I2C address
        :param value: Value to write
        :param force: Force write flag
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][WRITE] Write on {address}: {value}')
        self.__i2cbus.write_byte(address, value, force)



    def i2c_write_word_data(self, address: int, register: int, 
                            value:int, force: bool = False):
        """
        Write a single word (2 bytes) to a given register

        :param address: Device I2C address
        :param register: Register address
        :param value: Word value to write
        :param force: Force write flag
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][WRITE] Write word data on {address}-{register}: {value}')
        self.__i2cbus.write_word_data(address, register, value, force)


        
    def i2c_write_byte_data(self, address: int, register: int, 
                            value: int, force: bool = False):
        """
        Write a byte to a given register

        :param address: Device I2C address
        :param register: Register address
        :param value: Byte value to write
        :param force: Force write flag
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][WRITE] Write yte data on {address}-{register}: {value}')
        self.__i2cbus.write_byte_data(address, register, value, force)


    
    def i2c_write_block_data(self, address: int, register: int, 
                             data: list[int], force: bool = False):
        """
        Write a block of byte data to a given register

        :param address: Device I2C address
        :param register: Register address
        :param data: List of byte values to write
        :param force: Force write flag
        """
        if not self.__i2c_enabled:
            raise Exception('I2C bus is not enabled.')
        self.logger.debug(f'[I2C][WRITE] Write block data on {address}-{register}: {data}')
        self.__i2cbus.write_block_data(address, register, data, force)



    ######################################################
    #                                                    #
    #               Arduino CLI Interface                #
    #                                                    #
    ######################################################
        

    def get_arduino_boards(self) -> dict:
        """
        Get available Arduino boards
        """
        if not self.__arduino_cli_installed:
            raise Exception('Arduino CLI not found')
        
        result = subprocess.run(['arduino-cli', 'board', 'listall'], 
                                check=True, 
                                cwd=self.__arduino_cli_path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        result_string = result.stdout
        mapping = {}
        lines = result_string.strip().split("\n")
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                board_name = " ".join(parts[:-1])
                fqbn = parts[-1]
                mapping[board_name] = fqbn
        return mapping
    


    def compile_arduino_code(self, file_path: str, fqbn: str):
        """
        Compile arduino code

        :param file_path: Sketch file path (should be a directory)
        :param fqbn: Fully Qualified Board Name
        :raises Exception: If build error occurs
        """
        if not self.__arduino_cli_installed:
            raise Exception('Arduino CLI not found')

        abs_path = fileutil.get_absolute_path(file_path)
        result = subprocess.run(['arduino-cli', 'compile',
                                 '--fqbn', fqbn, abs_path], 
                                cwd=self.__arduino_cli_path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        
        if result.returncode == 1:
            raise Exception(result.stderr)
        


    def upload_arduino_code(self, file_path: str, port: str, 
                            fqbn: str, compile: bool = True):
        """
        Upload a sketch to the arduino

        :param file_path: Sketch file path (should be a directory)
        :param port: Arduino port
        :param fqbn: Fully Qualified Board Name
        :param compile: Try to compile the arduino first before upload
        """
        if not self.__arduino_cli_installed:
            raise Exception('Arduino CLI not found')
        
        self.logger.info('Starting arduino code upload')
        start = time.time()
        abs_path = fileutil.get_absolute_path(file_path)
        self.compile_arduino_code(abs_path, fqbn)
        result = subprocess.run(['arduino-cli', 'upload',
                                 '-p', port, '--fqbn', fqbn, 
                                 abs_path], 
                                cwd=self.__arduino_cli_path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        end = time.time()
        if result.returncode == 1:
            raise Exception(result.stderr)
        self.logger.info(f'Arduino code uploaded in {end - start} seconds')



    ######################################################
    #                                                    #
    #                  Devices Interface                 #
    #                                                    #
    ######################################################
        

    def _validate_pin(self, pin: Union[int, list[int], tuple[int]]):
        """
        Check if pin/pins is available

        :param pin: Pin to check
        :raises Exception: If pin is already in use
        """
        if isinstance(pin, int):
            if pin in self._pin_mapping:
                raise Exception(f'Pin {pin} already in use.')
            self._pin_mapping.append(pin)
        if isinstance(pin, (list, tuple)):
            for p in pin:
                if p in self._pin_mapping:
                    raise Exception(f'Pin {p} already in use.')
                self._pin_mapping.append(p)



    def cleanup(self):
        """
        Perform cleanup for graceful exit
        """
        self.logger.info('Performing cleanup routines.')
        GPIO.cleanup()
        for device in self._devices:
            device.cleanup()
        self.logger.info('Cleanup finished.')



    def attach_button(self, pin: int) -> Button:
        """
        Attach a button to this machine

        :param pin: Pin to attach the button to
        """
        self._validate_pin(pin)
        button = Button(self, pin)
        self._devices.append(button)
        self.logger.info(f'Button attached to pin: {pin}')
        return button
    


    def attach_led(self, pin: int) -> Led:
        """
        Attach a LED to this machine

        :param pin: Pin to attach the LED to
        """
        self._validate_pin(pin)
        led = Led(self, pin)
        self._devices.append(led)
        self.logger.info(f'LED attached to pin: {pin}')
        return led
    


    def attach_rgb_led(self, pins: tuple[int]) -> RgbLed:
        """
        Attach a RGB LED to this machine

        :param pins: Tuple of pins to use, in RGB order (red, green, blue)
        """
        self._validate_pin(pins)
        rgb_led = RgbLed(self, pins)
        self._devices.append(rgb_led)
        self.logger.info(f'RGB LED attached to pins: {pins}')
        return rgb_led
    


    def attach_relay(self, pin: int) -> Relay:
        """
        Attach a relay to this machine

        :param pin: Pin to attach the relay to
        """
        self._validate_pin(pin)
        relay = Relay(self, pin)
        self._devices.append(relay)
        self.logger.info(f'Relay attached to pin: {pin}')
        return relay
    


    def attach_active_buzzer(self, pin: int) -> ActiveBuzzer:
        """
        Attach an active buzzer to this machine

        :param pin: Pin to use
        """
        self._validate_pin(pin)
        active_buzzer = ActiveBuzzer(self, pin)
        self._devices.append(active_buzzer)
        self.logger.info(f'Active buzzer attached to pin: {pin}')
        return active_buzzer
    


    def attach_passive_buzzer(self, pin: int) -> PassiveBuzzer:
        """
        Attach a passive buzzer to this machine

        :param pin: Pin to use
        """
        self._validate_pin(pin)
        passive_buzzer = PassiveBuzzer(self, pin)
        self._devices.append(passive_buzzer)
        self.logger.info(f'Passive buzzer attached to pin: {pin}')
        return passive_buzzer
    


    def attach_light_sensor(self, pin: int) -> LightSensor:
        """
        Attach a light sensor to this machine
        A capacitor is needed in the circuit
        Refer to this [diagram](https://pimylifeup.com/wp-content/uploads/2016/01/Light-Sensor-Circuit.jpg)

        :param pin: Pin to use
        """
        self._validate_pin(pin)
        light_sensor = LightSensor(self, pin)
        self._devices.append(light_sensor)
        self.logger.info(f'Light sensor attached to pin: {pin}')
        return light_sensor
    


    def attach_pir_motion_sensor(self, pin: int) -> PIRMotionSensor:
        """
        Attach a PIR motion sensor to this machine

        :param pin: Pin to use
        """
        self._validate_pin(pin)
        pir_motion_sensor = PIRMotionSensor(self, pin)
        self._devices.append(pir_motion_sensor)
        self.logger.info(f'PIR motion sensor attached to pin: {pin}')
        return pir_motion_sensor
    


    def attach_servo_motor(self, pin: int) -> ServoMotor:
        """
        Attach a servo motor to this machine

        :param pin: Pin to use
        """
        self._validate_pin(pin)
        servo_motor = ServoMotor(self, pin)
        self._devices.append(servo_motor)
        self.logger.info(f'Servo motor attached to pin: {pin}')
        return servo_motor
    


    def attach_ultrasonic_sensor(self, pins: tuple[int, str]) -> ServoMotor:
        """
        Attach a ultrasonic sensor to this machine

        :param pins: Tuple of pins to use, in RGB order (trigger, echo)
        """
        self._validate_pin(pins)
        ultrasonic_sensor = UltrasonicSensor(self, pins)
        self._devices.append(ultrasonic_sensor)
        self.logger.info(f'Ultrasonic sensors attached to pin: {pins}')
        return ultrasonic_sensor
    


    def attach_l298n(self, pins: Union[list, tuple]) -> L298NDriver:
        """
        Attach a L298N Driver to this machine

        :param pins: Pins this device is connected to.
                     Should follow the format 
                     (ena, in1, in2) or (ena, in1, in2, enb, in3, in4)
        """
        self._validate_pin(pins)
        l298n = L298NDriver(self, pins)
        self._devices.append(l298n)
        self.logger.info(f'L298N Driver attached to pins: {pins}')
        return l298n



    def attach_sim808(self, port: str) -> Sim808:
        """
        Attach a SIM808 module to this machine

        :param port: Port to use
        """
        sim808 = Sim808(port)
        self._devices.append(sim808)
        self.logger.info(f'SIM808 attached to port: {port}')
        return sim808
    

    
    def attach_arduino(self, port: str, **kwargs) -> Arduino:
        """
        Attach an Arduino to this machine

        :param port: Port to use
        """
        arduino = Arduino(self, port, **kwargs)
        self._devices.append(arduino)
        self.logger.info(f'Arduino attached to port: {port}')
        return arduino
    