Servo Motor
-----------------

The connection diagram for servo motor is shown below:


.. image:: ../../_static/gpio/servo_motor.png
   :alt: Servo motor connection
   :align: center


+----------+--------------+
| Relay    | Raspberry Pi |
+==========+==============+
| VCC      | 5V           |
+----------+--------------+
| GND      | GND          |
+----------+--------------+
| Data     | GPIO18       |
+----------+--------------+

Rotating Servo Motor
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import raspidevkit
   import time

   machine = raspidevkit.Machine()
   servo_motor = machine.attach_servo_motor(18)
   servo_motor.rotate(90)
   time.sleep(1)
   servo_motor.rotate(180)
   time.sleep(1)
   servo_motor.rotate(0)
