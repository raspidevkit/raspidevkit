from .machineutils import dictutils
from .__logger import MachineLogger
from .__devices import Button, Led, RgbLed, ActiveBuzzer, LightSensor, PIRMotionSensor, \
    PassiveBuzzer, Sim808, Arduino
from .constants import INPUT, OUTPUT
from typing import Union

import sys
import subprocess
import logging

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
                 enable_logging: bool = False,
                 **kwargs) -> None:
        '''
        Create a machine class which different devices can be created from.

        :param gpio_mode: GPIO mode can be `BCM` or `BOARD` as `GPIO.setmode()`
        :param enable_logging: Enable logging, configuration can be set by passing in a config dictionary
        :param config: Config dictionary which will take priority. See sample config.
        '''
        default_config = {
            'logging': {
                'format': '%(asctime)s [%(levelname)s] - %(message)s.',
                'file': 'machine.log'
            }
        }

        self._config = kwargs.get('config', default_config)
        if gpio_mode.upper() == 'BCM':
            GPIO.setmode(GPIO.BCM)
        elif gpio_mode.upper() == 'BOARD':
            GPIO.setmode(GPIO.BCM)
        else:
            raise ValueError('GPIO mode can only be BCM or BOARD.')
        self.__intialize_logger(enable_logging)
        self.__clang_enabled = self.__is_clang_format_installed()
        self._devices = []
        self._pin_mapping = {}



    @property
    def clang_enabled(self) -> bool:
        """
        Clang format installed
        """
        return self.__clang_enabled
    


    @property
    def devices(self) -> list:
        """
        Attached devices
        """
        return self._devices
    


    def __intialize_logger(self, enabled: bool):
        default_format = '%(asctime)s [%(levelname)s] - %(message)s.'
        default_file = 'machine.log'
        format = dictutils.get(self._config, 'logging', 'format', default=default_format)
        file = dictutils.get(self._config, 'logging', 'file', default=default_file)

        logging_format = logging.Formatter(format)
        main_handler = logging.FileHandler(file)
        main_handler.setFormatter(logging_format)
        self.logger = MachineLogger(__name__, enabled=enabled)
        self.logger.addHandler(main_handler)
        self.logger.setLevel(logging.INFO)
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
    


    def gpio_setup(self, pin: int,  setup: str):
        """
        Explicitly setup a GPIO pin

        :param pin: Pin to setup
        :param setup: Pin mode (INPUT or OUTPUT)
        """
        if setup.upper() == INPUT:
            GPIO.setup(pin, GPIO.IN)
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
        value = GPIO.input(pin)
        return value



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
    


    def attach_sim808(self, port: str) -> Sim808:
        """
        Attach a SIM808 module to this machine

        :param port: Port to use
        """
        sim808 = Sim808(port)
        self._devices.append(sim808)
        self.logger.info(f'SIM808 attached to port: {port}')
        return sim808
    

    
    def attach_arduino(self, port: str) -> Arduino:
        """
        Attach an Arduino to this machine

        :param port: Port to use
        """
        arduino = Arduino(self, port)
        self._devices.append(arduino)
        self.logger.info(f'Arduino attached to port: {port}')
        return arduino
    