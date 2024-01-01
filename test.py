from raspidevkit import Machine
from raspidevkit.machineutils import formatutil

machine = Machine()

arduino = machine.attach_led(10)
