from .__logger import MachineLogger
from .__interface import (
    ArduinoCliInterface,
    GpioInterface,
    I2cInterface
)
from typing import Union
from .utils import dictutils
from .devices import (
    ActiveBuzzer,
    Arduino,
    Button,
    Led,
    L293DDriver,
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
import logging


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
        :param i2cbus: I2C bus to use
        :param enable_logging: Enable logging, configuration can be set by passing in a config dictionary
        :param debug: Set debug to true
        :param arduino_cli_path: Path to Arduino CLI
        :param config: Config dictionary which will take priority. See sample config.

        ```python
        default_config = {
            'logging': {
                'format': '%(asctime)s [%(levelname)s] - %(message)s.',
                'file': 'machine.log',
                'level': logging.INFO if not debug else logging.DEBUG
            }
        }
        ```
        '''
        custom_config = kwargs.get('config', {})
        self.logger = None
        self.__intialize_logger(enable_logging, debug, custom_config)

        self.__gpio = GpioInterface(gpio_mode, self.logger)
        self.__i2c = I2cInterface(i2cbus, self.logger)
        self.__arduino_cli = ArduinoCliInterface(arduino_cli_path, self.logger)

        self._devices = []
        self._pin_mapping = []



    @property
    def gpio(self):
        """
        GPIO interface
        """
        return self.__gpio
    

    
    @property
    def i2c(self):
        """
        I2C interface
        """
        return self.__i2c



    @property
    def arduino_cli(self):
        """
        Arduino CLI interface
        """
        return self.__arduino_cli
    


    @property
    def devices(self) -> list:
        """
        Attached devices
        """
        return self._devices
    


    def __intialize_logger(self, enabled: bool, debug: bool, config: dict):
        """
        Initialize logger. `debug` variable will take priority
        """
        default_format = '%(asctime)s [%(levelname)s] - %(message)s.'
        default_file = 'machine.log'
        format = dictutils.get(config, 'logging', 'format', default=default_format)
        file = dictutils.get(config, 'logging', 'file', default=default_file)
        if not debug:
            level = dictutils.get(config, 'logging', 'level', default=logging.INFO)
        else:
            level = logging.DEBUG

        logging_format = logging.Formatter(format)
        main_handler = logging.FileHandler(file)
        main_handler.setFormatter(logging_format)
        self.logger = MachineLogger(__name__, enabled=enabled or debug)
        self.logger.addHandler(main_handler)
        self.logger.setLevel(level)
        self.logger.info('Logger initialized.')



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
        self.gpio.cleanup()
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
    


    def attach_ultrasonic_sensor(self, pins: tuple[int]) -> UltrasonicSensor:
        """
        Attach a ultrasonic sensor to this machine

        :param pins: Tuple of pins to use, in order (trigger, echo)
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



    def attach_l293d(self, pins: Union[list, tuple]) -> L293DDriver:
        """
        Attach a L293D Driver to this machine

        :param pins: Pins this device is connected to.
                     Should follow the format 
                     (ena, in1, in2) or (ena, in1, in2, enb, in3, in4)
        """
        self._validate_pin(pins)
        l293d = L293DDriver(self, pins)
        self._devices.append(l293d)
        self.logger.info(f'L293D Driver attached to pins: {pins}')
        return l293d
    


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
