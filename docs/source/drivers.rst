Drivers
=================

Some devices such as motors (DC motors and stepper motors) and etc. can't be directly connected to the Raspberry Pi because of the power constraints and requires the use of specialized drivers to control them

`Raspidevkit` takes the approach of connecting the respective driver objects to the `Machine` class and from that driver object, spawns the respective device

DC Motor Drivers
------------------

Both L293D and L298N behaves the same

.. toctree::
   :maxdepth: 1

   devices/drivers/dc_motor/l293d
   devices/drivers/dc_motor/l298n
