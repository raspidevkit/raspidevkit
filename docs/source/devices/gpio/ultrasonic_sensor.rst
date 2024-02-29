Ultrasonic Sensor (HC-SR04)
-------------------------------

The connection diagram for servo motor is shown below:


.. image:: ../../_static/gpio/ultrasonic_sensor.png
   :alt: Servo motor connection
   :align: center


+----------+--------------+
| HC-SR04  | Raspberry Pi |
+==========+==============+
| VCC      | 5V           |
+----------+--------------+
| GND      | GND          |
+----------+--------------+
| Trig     | GPIO14       |
+----------+--------------+
| Echo     | GPIO15       |
+----------+--------------+

Reading distance
^^^^^^^^^^^^^^^^^^^^^^

The default distance unit is ``cm``, however you can also use different unit of measure. The available units are:
- cm
- inch
- ft
- m

.. code-block:: python

   import raspidevkit
   import time

   machine = raspidevkit.Machine()
   trig = 14
   echo = 15
   ultrasonic_sensor = machine.attach_ultrasonic_sensor((trig, echo))
   units_in_cm = ultrasonic_sensor.get_distance()
   units_in_inch = ultrasonic_sensor.get_distance(measure='inch')
   units_in_ft = ultrasonic_sensor.get_distance(measure='ft')
   units_in_meter = ultrasonic_sensor.get_distance(measure='m')
