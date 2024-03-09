from raspidevkit.constants import OUTPUT, CLOCKWISE, COUNTER_CLOCKWISE
from raspidevkit.utils import dictutils
from ...base import GpioDevice, PwmDevice
from abc import abstractmethod


class DcMotorDriver:
    def __init__(self, machine, motor_pin_setup: dict[str, dict[str, str]]) -> None:
        """
        Base class for DcMotorDrivers object.

        :param motor_pin_setup: Pin connection of GPIO pin and physical driver pin.
                          Pins are only initialized when calling `attach_motors()`.
                          Has currently support only on 3 pin per motor drivers (en, a, b)

        Example config:
        ```python
        motor_pin_setup = {
            "1": {
                "EN": "14",
                "A": "15",
                "B": "16"
            },
            "2": {
                "EN": "17",
                "A": "18",
                "B": "19"
            }
        }
        ```
        """
        from  raspidevkit import Machine

        self.__machine: Machine = machine
        self.__gpio = self.__machine.gpio
        self._max_motor = len(motor_pin_setup.keys())
        self._motors = []



    @property
    def gpio(self):
        """
        GPIO interface
        """
        return self.__gpio


    
    @property
    def motors(self):
        """
        Currently attached motors to this driver
        """
        return self._motors
    


    @abstractmethod
    def attach_motor(self):
        """
        Attach a motor to this driver
        """
        raise NotImplementedError('Must be overriden by derived class')



    def gpio_write(self, pin: int, value: bool):
        """
        Perform a GPIO output on a pin

        :param pin: The pin to write
        :param value: Can be HIGH or LOW
        """
        self.__machine.gpio.write(pin, value)



    def gpio_setup(self, pin: int,  setup: str):
        """
        Explicitly setup a GPIO pin

        :param pin: Pin to setup
        :param setup: Pin mode (INPUT or OUTPUT)
        """
        self.__machine.gpio.setup(pin, setup)



    def cleanup(self):
        """
        Perform cleanup for graceful exit
        """
        for motor in self.motors:
            motor.cleanup()
        


class DcMotor(GpioDevice, PwmDevice):
    def __init__(self, driver: DcMotorDriver, pin_setup: dict[str, str], is_pwm: bool = False) -> None:
        """
        Base class for DcMotors object. Must be spawned by a DcMotorDriver class.

        :param pin_setup: Pin connection of driver pin and GPIO pin.
                          Has currently support only on 3 pin per motor drivers (en, a, b).
        :param is_pwm: Enable PWM mode, allowing to motor to set speed

        Example config:
        ```python
        pin_setup = {
            "EN": "14",
            "A": "15",
            "B": "16"
        }
        ```
        """
        self.__driver = driver
        self.__is_pwm = is_pwm
        self._state = False
        required_keys = ['EN', 'A', 'B']

        if not dictutils.does_keys_exists(pin_setup, required_keys):
            raise ValueError('Incorrect pin setup. Missing keys')
        
        self.__pin_en = pin_setup.get('EN')
        self.__pin_a = pin_setup.get('A')
        self.__pin_b = pin_setup.get('B')

        gpio_pins = {}
        for _, pin in pin_setup.items():
            gpio_pins[pin] = OUTPUT

        super().__init__(machine=self.__driver, pin_setup=gpio_pins, device_type=OUTPUT)

        if is_pwm:
            super(PwmDevice, self).__init__(pin_setup.pop('EN'), frequency=1000)
            self.__is_pwm = True
            
        self.__driver.gpio_write(self.__pin_a, True)
        self.__driver.gpio_write(self.__pin_b, False)

        self.__direction = CLOCKWISE
        self.__speed = 100



    @property
    def is_pwm(self):
        """
        PWM is enabled
        """
        return self.__is_pwm
    


    @property
    def state(self):
        """
        Motor state
        """
        return self._state
    


    @property
    def speed(self):
        """
        Motor speed. 100 is highest, 0 is lowest.
        """
        return self.__speed
    


    @speed.setter
    def speed(self, speed: int):
        self.set_speed(speed)



    @property
    def direction(self):
        """
        Current spinning direction
        """
        return self.__direction
    


    @direction.setter
    def direction(self, direction: str):
        self.set_direction(direction)



    def cleanup(self):
        """
        Perform cleanup for graceful exit
        """
        self.stop()



    def run(self):
        """
        Start the motor
        """
        if self._state:
            return
        
        if self.__is_pwm:
            self.start(self.__speed)
        else:
            self.__driver.gpio_write(self.__pin_en, True)
        self._state = True



    def stop(self):
        """
        Stop the motor
        """
        if not self._state:
            return
        
        if self.__is_pwm:
            super().stop()
        else:
            self.__driver.gpio_write(self.__pin_en, False)
        self._state = False


    
    def set_speed(self, speed: int):
        """
        Set motor speed. Only available if `is_pwm`

        :param speed: New speed
        """
        if not self.is_pwm:
            raise RuntimeError('Only available if in pwm mode')
        
        self.duty_cycle = speed
        self.__speed = speed



    def set_direction(self, direction: str):
        """
        Set current spinning direction

        :param direction: New direction to set to. Can be (CLOCKWISE or COUNTER_CLOCKWISE). Use raspidev.constants
        """
        if self.direction == direction:
            return
        
        if direction != CLOCKWISE and direction != COUNTER_CLOCKWISE:
            raise ValueError('Incorrect direction value. Use raspidev.CLOCKWISE or raspidev.COUNTER_CLOCKWISE')

        if direction == CLOCKWISE:
            self.__driver.gpio_write(self.__pin_a, True)
            self.__driver.gpio_write(self.__pin_b, False)
        
        if direction == COUNTER_CLOCKWISE:
            self.__driver.gpio_write(self.__pin_a, False)
            self.__driver.gpio_write(self.__pin_b, True)
