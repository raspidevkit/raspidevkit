from .__logger import MachineLogger
from .utils import fileutil
from .constants import INPUT, PULL_UP, PULL_DOWN, OUTPUT
from typing import Union
import json
import re
import subprocess
import sys
import time

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO
    import RPi.GPIO as GPIO


class GpioInterface:
    def __init__(self, mode: str, logger: MachineLogger) -> None:
        """
        Initialize Machine GPIO Interface

        :param mode: GPIO board setup
        :param logger: Machine Logger object
        """
        self.__logger = logger
        if mode.upper() == 'BCM':
            GPIO.setmode(GPIO.BCM)
        elif mode.upper() == 'BOARD':
            GPIO.setmode(GPIO.BCM)
        else:
            raise ValueError('GPIO mode can only be BCM or BOARD.')
        


    def setup(self, pin: int,  setup: str):
        """
        Explicitly setup a GPIO pin

        :param pin: Pin to setup
        :param setup: Pin mode (INPUT or OUTPUT)
        """
        self.__logger.debug(f'[GPIO][SETUP] {pin}:{setup}')
        if setup.upper() == INPUT:
            GPIO.setup(pin, GPIO.IN)
        elif setup.upper() == PULL_UP:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        elif setup.upper() == PULL_DOWN:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        elif setup.upper() == OUTPUT:
            GPIO.setup(pin, GPIO.OUT)
        else:
            raise ValueError('Invalid pin mode')
        


    def write(self, pin: int, value: bool):
        """
        Perform a GPIO output on a pin

        :param pin: The pin to write
        :param value: Can be HIGH or LOW
        """
        self.__logger.debug(f'[GPIO][WRITE] Write on {pin}: {value}')
        if value:
            GPIO.output(pin, GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.LOW)



    def read(self, pin: int) -> bool:
        """
        Read the value from a GPIO pin
        
        :param pin: The pin to read
        :return: Value, either True of False
        """
        self.__logger.debug(f'[GPIO][READ] Read on: {pin}')
        value = GPIO.input(pin)
        self.__logger.debug(f'[GPIO][READ] Value from {pin}: {value}')
        return value
    


    def cleanup(self):
        """
        Perform cleanup
        """
        GPIO.cleanup()


class I2cInterface:
    def __init__(self, i2cbus: int, logger: MachineLogger) -> None:
        """
        Initialize Machine GPIO Interface

        :param i2cbus: I2C bus to use
        :param logger: Machine Logger object
        """
        self.__logger = logger
        self.__bus = None
        self.__enabled = False
        if i2cbus is not None:
            import smbus2
            self.__bus = smbus2.SMBus(i2cbus)
            self.__enabled = True



    @property
    def enabled(self) -> bool:
        """
        I2C Interface enabled
        """
        return self.__enabled



    def read_byte(self, address: int, force: bool = False) -> int:
        """
        Read a single byte from an I2C address.

        :param address: Device I2C address
        :param force: Force read flag
        :return: Read byte value
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][READ] Read on {address}')
        value = self.__bus.read_byte(address, force)
        self.__logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def read_word_data(self, address: int, register: int, 
                           force: bool = False) -> int:
        """
        Read a single word (2 bytes) from a given register

        :param address: Device I2C address
        :param register: Register address
        :param force: Force read flag
        :return: 2-byte word
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][READ] Read word data on {address}-{register}')
        value = self.__bus.read_word_data(address, register, force)
        self.__logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def read_byte_data(self, address: int, register: int, 
                           force: bool = False) -> int:
        """
        Read a single byte from a designated register
        
        :param address: Device I2C address
        :param register: Register address
        :param force: Force read flag
        :return: Read byte value
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][READ] Read byte data on {address}-{register}')
        value = self.__bus.read_byte_data(address, register, force)
        self.__logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def read_block_data(self, address: int, register: int, 
                            length: int = 32, force: bool = False) -> list[int]:
        """
        Read a block of data from a given register

        :param address: Device I2C address
        :param register: Register address
        :param length: Block length, default to 32 bytes
        :param force: Force read flag
        :return: List of bytes
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][READ] Read block data ({length}) on {address}-{register}')
        value = self.__bus.read_i2c_block_data(address, register, length, force)
        self.__logger.debug(f'[I2C][READ] Returned: {value}')
        return value
    


    def write_byte(self, address: int, value: int, force: bool = False):
        """
        Write a single byte to an I2C address

        :param address: Device I2C address
        :param value: Value to write
        :param force: Force write flag
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][WRITE] Write on {address}: {value}')
        self.__bus.write_byte(address, value, force)



    def write_word_data(self, address: int, register: int, 
                            value:int, force: bool = False):
        """
        Write a single word (2 bytes) to a given register

        :param address: Device I2C address
        :param register: Register address
        :param value: Word value to write
        :param force: Force write flag
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][WRITE] Write word data on {address}-{register}: {value}')
        self.__bus.write_word_data(address, register, value, force)


        
    def write_byte_data(self, address: int, register: int, 
                            value: int, force: bool = False):
        """
        Write a byte to a given register

        :param address: Device I2C address
        :param register: Register address
        :param value: Byte value to write
        :param force: Force write flag
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][WRITE] Write yte data on {address}-{register}: {value}')
        self.__bus.write_byte_data(address, register, value, force)


    
    def write_block_data(self, address: int, register: int, 
                             data: list[int], force: bool = False):
        """
        Write a block of byte data to a given register

        :param address: Device I2C address
        :param register: Register address
        :param data: List of byte values to write
        :param force: Force write flag
        """
        if not self.__enabled:
            raise Exception('I2C bus is not enabled.')
        self.__logger.debug(f'[I2C][WRITE] Write block data on {address}-{register}: {data}')
        self.__bus.write_block_data(address, register, data, force)



class ArduinoCliInterface:
    def __init__(self, arduino_cli_path: Union[str, None], logger: MachineLogger) -> None:
        """
        Initialize Arduino CLI interface

        :param arduino_cli_path: Path to Arduino CLI
        :param logger: Machine Logger object
        """
        self.__logger = logger
        if arduino_cli_path is None:
            self.__path = None
            self.__enabled = None
            self.__formatting = False
        else:
            self.__enabled = self.__is_arduino_cli_installed(arduino_cli_path)
            self.__path = arduino_cli_path if self.__enabled else None
            self.__formatting = self.__is_clang_format_installed()
            self.__setup_libraries()



    @property
    def path(self) -> Union[str, None]:
        """
        Arduino CLI path
        """
        return self.__path
    


    @property
    def enabled(self) -> bool:
        """
        Arduino CLI enabled and working
        """
        return self.__enabled
    


    @property
    def formatting(self) -> bool:
        """
        Formatting enabled. Useful if manually generating code
        """
        return self.__formatting
    


    def __is_arduino_cli_installed(self, path: str) -> bool:
        """
        Check if arduino is found in the path given

        :param arduino_cli_path: Arduino CLI path
        :return: Arduino CLI installed
        """
        try:
            subprocess.run(['arduino-cli', 'version'],
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True,
                           cwd=path,
                           shell=True)
            self.__logger.info('Arduino CLI found.')
            return True
        except subprocess.CalledProcessError:
            self.__logger.warning('Arduino CLI not found.')
            return False
        


    def __is_clang_format_installed(self) -> bool:
        """
        Check if clang-format is installed
        """
        try:
            subprocess.run(['clang-format', '--version'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True, 
                           shell=True)
            self.__logger.info('Clang-format found.')
            return True
        except subprocess.CalledProcessError:
            self.__logger.warning('Clang-format not found. Arduino generated code will not be formatted')
            return False
        


    def __setup_libraries(self):
        """
        Check for required libraries and install as neccessary
        """
        if not self.__enabled:
            self.__logger.info(f'Skipping arduino library setup')
            return
        
        required_libraries = {
            'Servo': '1.2.1',
        }
        installed_libraries = self.get_installed_libraries()
        for name, version in required_libraries.items():
            if name not in installed_libraries.keys():
                self.__logger.info(f'Installing {name}@{version}', to_stdout=True)
                self.install_library(name=name, version=version)
            elif installed_libraries.get(name) != version:
                self.__logger.info(f'Updating {name} to {version}', to_stdout=True)
                self.install_library(name=name, version=version)
            else:
                # Skip
                pass



    def get_boards(self) -> dict:
        """
        Get available Arduino boards
        """
        if not self.__enabled:
            raise Exception('Arduino CLI not found')
        
        result = subprocess.run(['arduino-cli', 'board', 'listall',
                                 '--format', 'json'], 
                                check=True, 
                                cwd=self.__path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        result = json.loads(result.stdout)
        boards = result['boards']

        board_mapping = {}
        for board in boards:
            name = board['name']
            fqbn = board['fqbn']
            board_mapping[name] = fqbn
        
        return board_mapping
    


    def get_installed_libraries(self) -> dict:
        """
        Get a list of installed libraries in the arduino

        :return: List of installed libraries and version
        """
        if not self.__enabled:
            raise Exception('Arduino CLI not found')
        
        result = subprocess.run(['arduino-cli', 'lib', 'list',
                                 '--format', 'json'], 
                                check=True, 
                                cwd=self.__path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        libraries = json.loads(result.stdout)

        library_info_map = {}
        for library in libraries:
            name = library['library']['name']
            version = library['library']['version']
            library_info_map[name] = version

        return library_info_map



    def install_library(self, name: str, version: str = 'latest',
                                git_url: str = '', zip_path: str = ''):
        """
        Install an Arduino library
        Priority: zip_path > git_url > name

        :param name: Arduino library name
        :param version: Library version
        :param git_url: Git url of library
        :param zip_path: Path to library zip
        """
        version_pattern = r'(\d+\.\d+\.\d+)'
        if version != 'latest' and not re.search(version_pattern, version):
            raise Exception('Incorrect version format')
        
        command = ['arduino-cli', 'lib', 'install']
        if zip_path:
            command.append('--zip-path')
            command.append(zip_path)
            self.__logger.info(f'Installing library via zip path: {zip_path}')
        elif git_url:
            command.append('--git_url')
            url = f'{git_url}{'#' + version if version != 'latest' else ''}'
            command.append(url)
            self.__logger.info(f'Installing library via git url: {git_url}')
        else:
            name = f'{name}{'@' + version if version != 'latest' else ''}'
            command.append(name)
            self.__logger.info(f'Installing library via name: {name}')
        
        result = subprocess.run(command, 
                                cwd=self.__path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        
        if result.returncode == 1:
            raise Exception(result.stderr)
            


    def uninstall_library(self, library: str):
        """
        Uninstall an Arduino library

        :param library: Library name
        """
        if library not in self.get_installed_libraries():
            raise Exception('Library not installed')
        
        result = subprocess.run(['arduino-cli', 'lib',
                                 'uninstall', library], 
                                cwd=self.__path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        
        if result.returncode == 1:
            raise Exception(result.stderr)
        

    def compile_code(self, file_path: str, fqbn: str):
        """
        Compile arduino code

        :param file_path: Sketch file path (should be a directory)
        :param fqbn: Fully Qualified Board Name
        :raises Exception: If build error occurs
        """
        if not self.__enabled:
            raise Exception('Arduino CLI not found')

        abs_path = fileutil.get_absolute_path(file_path)
        result = subprocess.run(['arduino-cli', 'compile',
                                 '--fqbn', fqbn, abs_path], 
                                cwd=self.__path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        
        if result.returncode == 1:
            raise Exception(result.stderr)
        


    def upload_code(self, file_path: str, port: str, 
                            fqbn: str, compile: bool = True):
        """
        Upload a sketch to the arduino

        :param file_path: Sketch file path (should be a directory)
        :param port: Arduino port
        :param fqbn: Fully Qualified Board Name
        :param compile: Try to compile the arduino first before upload
        """
        if not self.__enabled:
            raise Exception('Arduino CLI not found')
        
        self.__logger.info('Starting arduino code upload')
        start = time.time()
        abs_path = fileutil.get_absolute_path(file_path)
        self.compile_code(abs_path, fqbn)
        result = subprocess.run(['arduino-cli', 'upload',
                                 '-p', port, '--fqbn', fqbn, 
                                 abs_path], 
                                cwd=self.__path, 
                                shell=True, 
                                capture_output=True, 
                                text = True)
        end = time.time()
        if result.returncode == 1:
            raise Exception(result.stderr)
        self.__logger.info(f'Arduino code uploaded in {end - start} seconds')
