import sys
import time
from ..constants import INPUT, OUTPUT, PULL_UP, PULL_DOWN, \
    RED, BLUE, GREEN, YELLOW, MAGENTA, CYAN, WHITE
from typing import Callable, Union

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO


class GpioDevice:
    def __init__(self, pin_setup: dict, device_type: str) -> None:
        """
        Create a GPIO device. Pin setup can include both input and output.

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
        for pin in pin_setup.keys():
            if pin_setup[pin] == INPUT:
                GPIO.setup(pin, GPIO.IN)
            elif pin_setup[pin] == PULL_UP:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            elif pin_setup[pin] == PULL_DOWN:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            elif pin_setup[pin] == OUTPUT:
                GPIO.setup(int(pin), GPIO.OUT)
            else:
                raise ValueError(f"Pin setup for {pin} is not valid")
        
        self.__multi_pin = False
        if len(pin_setup.keys()) > 1:
            self.__multi_pin = True
        
        if self.__multi_pin:
            self.__pins = tuple([int(pin) for pin in dict.keys()])
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



    def cleanup(self):
        """
        Perform cleanup
        """
        pass



class PwmDevice(GPIO.PWM):
    def __init__(self, pin: int, frequency: float) -> None:
        """
        Create a PWM device

        :param pin: Pin this device is attached to
        :param frequency: Device frequency
        """
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
    


class ArduinoDevice:
    def __init__(self, pin_setup: dict, device_type: str, commands: dict[str, Union[str, int]]) -> None:
        """
        Create a Arduino device.

        :param pin_setup: Config dictionary of pin mode, can be `INPUT`,`PULL_UP`, 
            \t`PULL_DOWN`, `OUTPUT` or `custom`. When custom, the setup method 
            \tcan be overriden
        :param device_type: This device device_type `INPUT`or `OUTPUT`
        :param commands: Dictionary of commands with methods as keys.
        Sample command configuration:
        ```python
        commands = {
            "turnOn": 1,
            "turnOff": 2
        }
        ```
        """
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
            else:
                raise ValueError(f'Invalid value for pin {pin}')
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
            'setup': self._setup_code,
            'methods': {}
        }



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