import sys
sys.path.append('./')

from raspidevkit import Machine
import pytest


@pytest.fixture()
def machine():
    machine = Machine()
    yield machine
    # No cleanup
    # machine.cleanup()


class TestArduino:
    def test_arduino(self, machine: Machine):
        arduino = machine.attach_arduino(port=None)
