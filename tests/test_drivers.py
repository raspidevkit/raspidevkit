import sys
sys.path.append('./')

from raspidevkit import Machine
from raspidevkit import COUNTER_CLOCKWISE, CLOCKWISE
import pytest
import time


@pytest.fixture()
def machine():
    machine = Machine()
    yield machine
    machine.cleanup()


class TestDcMotorDriver:
    def test_l293d_single_motor(self, machine: Machine):
        pins = (14, 15, 18)
        l239d = machine.attach_l293d(pins)
        motor = l239d.attach_motor()
        with pytest.raises(Exception):
            motor.set_speed(50)
        motor.run()
        time.sleep(1)
        motor.set_direction(COUNTER_CLOCKWISE)
        time.sleep(1)
        motor.set_direction(CLOCKWISE)
        time.sleep(1)
        motor.stop()


    def test_l293d_single_pwm_motor(self, machine: Machine):
        pins = (14, 15, 18)
        l239d = machine.attach_l293d(pins)
        motor = l239d.attach_motor(is_pwm=True)
        motor.set_speed(50)
        motor.run()
        time.sleep(1)
        motor.set_direction(COUNTER_CLOCKWISE)
        time.sleep(1)
        motor.set_direction(CLOCKWISE)
        time.sleep(1)
        motor.stop()


    def test_l293d_single_setup_multi_motor(self, machine: Machine):
        pins = (14, 15, 18)
        l239d = machine.attach_l293d(pins)
        l239d.attach_motor()
        with pytest.raises(Exception):
            l239d.attach_motor()


    def test_l293d_dual_setup_multi_motor(self, machine: Machine):
        pins = (14, 15, 18, 25, 24, 23)
        l239d = machine.attach_l293d(pins)
        l239d.attach_motor()
        l239d.attach_motor()
        with pytest.raises(Exception):
            l239d.attach_motor()


    def test_l298n_single_motor(self, machine: Machine):
        pins = (14, 15, 18)
        l298n = machine.attach_l298n(pins)
        motor = l298n.attach_motor()
        with pytest.raises(Exception):
            motor.set_speed(50)
        motor.run()
        time.sleep(1)
        motor.set_direction(COUNTER_CLOCKWISE)
        time.sleep(1)
        motor.set_direction(CLOCKWISE)
        time.sleep(1)
        motor.stop()


    def test_l298n_single_pwm_motor(self, machine: Machine):
        pins = (14, 15, 18)
        l298n = machine.attach_l298n(pins)
        motor = l298n.attach_motor(is_pwm=True)
        motor.set_speed(50)
        motor.run()
        time.sleep(1)
        motor.set_direction(COUNTER_CLOCKWISE)
        time.sleep(1)
        motor.set_direction(CLOCKWISE)
        time.sleep(1)
        motor.stop()


    def test_l298n_single_setup_multi_motor(self, machine: Machine):
        pins = (14, 15, 18)
        l298n = machine.attach_l298n(pins)
        l298n.attach_motor()
        with pytest.raises(Exception):
            l298n.attach_motor()


    def test_l298n_dual_setup_multi_motor(self, machine: Machine):
        pins = (14, 15, 18, 25, 24, 23)
        l298n = machine.attach_l298n(pins)
        l298n.attach_motor()
        l298n.attach_motor()
        with pytest.raises(Exception):
            l298n.attach_motor()
