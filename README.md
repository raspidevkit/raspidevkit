# Raspidevkit
Easily control devices with Raspberry Pi

## Building
First, ensure that the `setuptools` and `wheel` packages as installed with `pip install setuptools wheel`

Navigate to root directory and run `python setup.py sdist bdist_wheel` to create the distribution package

After creating the package, we can now install the package with `pip install dist/raspidevkit-{version}.tar.gz`

## Usage
### Blinking an LED
```python
import raspidevkit
import time

machine = raspidevkit.Machine()
led = machine.attach_led(14)
led.turn_on()
time.sleep(3)
led.turn_off()
```
In this example, first we need to create a `Machine` object which represents our Raspberry Pi machine and by calling `attach_{device}` we can spawn a device which we can use to do various things such as for this led, turning on and off.

### Specifying Board Layout
By default, the board layout is set to `BCM`, if you want to set it to `BOARD` layout you can specify the `gpio_mode` for the `Machine`
```python
import raspidevkit
import time

machine = raspidevkit.Machine(gpio_mode=raspidevkit.BOARD)
```

### Logging
The `Machine` class has also a logger which can be enabled on `enable_logging` and `debug` arguments of the Machine class. When `debug` is `True` the logger object will be set to debug level regardless of the logger configuration given. Below is a sample configuration for logger, though this is just option
```python
'logging': {
    'format': '%(asctime)s [%(levelname)s] - %(message)s.',
    'file': 'machine.log',
    'level': logging.INFO
}
```

### Motors, Drivers and Etc.
#### Motors and other devices that may require external drivers that may not be directly connected to the Raspiberry Pi
Devices such as this requires their respective drivers to be first attach to the Raspiberry Pi then from that driver will spawn the Motor or other device object. Below is a sample snippet for L298N motor driver.
```python
import raspidevkit
import time

machine = raspidevkit.Machine()
pins = (12, 13, 14)
l298n = machine.attach_l298n(pins)
motor = l298n.attach_motor()
motor.run()
time.sleep(5)
motor.stop()
```
You can also set the speed of the motor by enabling the PWM mode of the motor by setting `is_pwm` to `True` when attaching motor to the drive
```python
motor = l298n.attach_motor(is_pwm=True)
```

### I2C Communication
The library will also support devices that uses I2C Protocol for communications. By default, when initializing the `Machine` object, the I2C interface is not enabled yet. You can enable it by setting the `i2cbus` to the bus you want to use. For Raspi4 and above it is `1`. 
```python
import raspidevkit
import time

machine = raspidevkit.Machine(i2cbus=1)
```
As of this writing, the I2C communication is still in testing mode and currently no devices has been implemented yet :(

### Arduino Boards
Raspidevkit also supports controlling devices that are attached to an Arduino in which the Arduino is attached to the Arduino. As of now, the currenly supported communication mode is just for serial. This also features auto code generation, compilation and upload to the Arduino Board. 

#### Auto Code Generation and Upload
If you plan to use the auto upload feature, you must first install the `arduino-cli` in your system. Below is a sample snippet with auto upload feature.
```python
import raspidevkit
import time

machine = raspidevkit.Machine(arduino_cli_path=r'/path/to/arduino-cli')
arduino = machine.attach_arduino('/tty/USB0', timeout=5)
led = arduino.attach_led(13)
arduino.compile()
led.turn_on()
time.sleep(3)
led.turn_off()
```
The principle of drivers mentioned above is also true for the arduino board wherein we attached first the arduino object on the machine then spawning the LED object from the arduino. The `Arduino` object is also just a subclass of `serial.Serial` object so any other arguments such as baudrate can also be applied when initializing the object. I also recommend putting a timeout of higher than 3 especially when dealing with devices that needs to send higher size of data to the Arduino.

When working with the Arduino, it is required to call the `compile` method which would handle the code generation and auto upload of the code to the Arduino board. So, before you call this method make sure that all devices you want to use in your Arduino Board are declared as this will only include devices attached up until the `compile` method was called.

#### Without Arduino-cli
If you have not installed the arduino-cli in your system or the library could not find the arduino-cli in the path you have provided. Then it will throw an exception when the compile method was called. You can however generate the code and have it manually uploaded to the Arduino. Here's how:
```python
import raspidevkit
import time

machine = raspidevkit.Machine()
arduino = machine.attach_arduino('/tty/USB0', timeout=5)
led = arduino.attach_led(13)
arduino.generate_code('test.ino')
### Have it uploaded then run the script again ###
led.turn_on()
time.sleep(3)
led.turn_off()
```
Here, we first generate the code to the file `test.ino` and manually uploaded the sketch file to the Arduino. after the sketch is uploaded we can then skip the code generation part and control our LED. However, this may be too much time-consuming in the long run

## Contribution
Thank you for considering contributing to our project! We welcome contributions from everyone. Please take a moment to review this document in order to make the contribution process straightforward and effective for everyone involved.

### Ways to Contribute
There are many ways to contribute to this project:

- Reporting bugs
- Suggesting enhancements
- Writing documentation
- Fixing bugs
- Implementing new features
- Providing feedback on issues

### Getting Started
If you're new to contributing to open source projects, check out the following resources to get started:

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Timers Only](https://www.firsttimersonly.com/)

### Issues
Issues are tracked in our [GitHub issue tracker](https://github.com/yourusername/your_project_name/issues). Please search the existing issues before filing a new one to avoid duplicates. If you find your issue already exists, you can contribute to the discussion or provide additional information.

### Pull Requests
We use Pull Requests (PRs) to review and merge changes into the main codebase. If you're not familiar with Pull Requests, please refer to GitHub's documentation on [Creating a Pull Request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/raspidevkit/raspidevkit/blob/development/LICENSE) file for details.

## TODO
- [ ] Launch to PyPi
- [ ] Create documentation
- [ ] Add support for SPI devices
- [ ] Add more supported devices
