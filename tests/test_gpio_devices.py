import sys
sys.path.append('./')

from raspidevkit import Machine
from raspidevkit import (
    RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE
)
import pytest
import time


@pytest.fixture()
def machine():
    machine = Machine()
    yield machine
    machine.cleanup()


class TestGpioDevice:
    def test_button(self, machine: Machine):
        button = machine.attach_button(18)
        button.read()

    
    def test_buzzer_active(self, machine: Machine):
        active_buzzer = machine.attach_active_buzzer(18)
        active_buzzer.turn_on()
        time.sleep(1)
        active_buzzer.turn_off()


    def test_buzzer_passive(self, machine: Machine):
        passive_buzzer = machine.attach_passive_buzzer(18)
        passive_buzzer.buzz(515)
        time.sleep(1)
        passive_buzzer.play_note('E2')

    
    def test_led(self, machine: Machine):
        led = machine.attach_led(18)
        led.turn_on()
        time.sleep(1)
        led.turn_off()


    def test_light_sensor(self, machine: Machine):
        light_sensor = machine.attach_light_sensor(18)
        light_sensor.read()


    def test_pir_motion_sensor(self, machine: Machine):
        pir_motor_sensor = machine.attach_pir_motion_sensor(18)
        pir_motor_sensor.read()


    def test_relay(self, machine: Machine):
        relay = machine.attach_relay(18)
        relay.turn_on()
        time.sleep(1)
        relay.turn_off()


    def test_rgb_led(self, machine: Machine):
        rgb_pins = (14, 15, 18)
        colors = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE]
        rgb_led = machine.attach_rgb_led(rgb_pins)
        rgb_led.turn_on()
        time.sleep(1)
        for color in colors:
            rgb_led.set_color(color)
            time.sleep(1)
        rgb_led.turn_off()


    def test_servo_motor(self, machine: Machine):
        servo_motor = machine.attach_servo_motor(18)
        servo_motor.rotate(90)
        time.sleep(1)
        servo_motor.rotate(0)


    def test_ultrasonic_sensor(self, machine: Machine):
        echo_pin = 15
        trigger_pin = 18
        ultrasonic_sensor = machine.attach_ultrasonic_sensor((echo_pin, trigger_pin))
        ultrasonic_sensor.get_distance()
        ultrasonic_sensor.get_distance(measure='inch')
        ultrasonic_sensor.get_distance(measure='ft')
        ultrasonic_sensor.get_distance(measure='m')
        with pytest.raises(Exception):
            ultrasonic_sensor.get_distance(measure='km')
        