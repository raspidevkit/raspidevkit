import sys
sys.path.append('../')

from ..base import I2CDevice
import time


class LCD(I2CDevice):
    def __init__(self, machine, address: int = 0x27, width: int = 16, 
                 rows: int = 2, line_mode: int = 2, pixel_mode: str = '5x8',
                 bit_mode: int = 4, entry_mode: str = 'left') -> None:
        """
        Create an I2C LCD object

        :param machine: Machine instance
        :param address: Device I2C address, default to 0x27
        :param width: Number of characters per line
        :param line_mode: Line mode (`2` or `1`)
        :param pixel_mode: Pixel mode (`5x8` or `5x10`)
        :param bit_mode: Bit mode (`4` or `8`)
        :param entry_mode: Starting direction of text (`left` or `right`)
        :param rows: Number of lines
        """
        super().__init__(machine, address)
        self.__commands = {
            "clear_display": 0x01,
            "return_home": 0x02,
            "entry_mode_set": 0x04,
            "display_control": 0x08,
            "cursor_shift": 0x10,
            "function_set": 0x20,
            "set_cgram_addr": 0x40,
            "set_ddram_addr": 0x80,
            "entry_right": 0x00,
            "entry_left": 0x02,
            "entry_shift_increment": 0x01,
            "entry_shift_decrement": 0x00,
            "display_on": 0x04,
            "display_off": 0x00,
            "cursor_on": 0x02,
            "cursor_off": 0x00,
            "blink_on": 0x01,
            "blink_off": 0x00,
            "display_move": 0x08,
            "cursor_move": 0x00,
            "move_right": 0x04,
            "move_left": 0x00,
            "8bit_mode": 0x10,
            "4bit_mode": 0x00,
            "2line": 0x08,
            "1line": 0x00,
            "5x10dots": 0x04,
            "5x8dots": 0x00,
            "backlight_on": 0x08,
            "backlight_off": 0x00
        }
        self.__command_delay = 0.0005
        self.__en_bit = 0b00000100
        self.__rw_bit = 0b00000010
        self.__rs_bit = 0b00000001
        self.__width = width
        self.__rows = rows

        if line_mode == 1:
            line_mode_cmd = self.__commands.get('1line')
        elif line_mode == 2:
            line_mode_cmd = self.__commands.get('2line')
        else:
            raise ValueError('Unsupported line mode')
        
        if pixel_mode == '5x8':
            pixel_mode_cmd = self.__commands.get('5x8dots')
        elif pixel_mode == '5x10':
            pixel_mode_cmd = self.__commands.get('5x10dots')
        else:
            raise ValueError('Unsupported pixel mode')
        
        if bit_mode == 4:
            bit_mode_cmd = self.__commands.get('4bit_mode')
        elif bit_mode == 8:
            raise NotImplemented('8 bit mode is not yet supported')
        else:
            raise ValueError('Unsupported bit mode')
    
        if entry_mode == 'left':
            entry_mode_cmd = self.__commands.get('entry_left')
        elif entry_mode == 'right':
            entry_mode_cmd = self.__commands.get('entry_right')
        else:
            raise ValueError('Unsupported entry mode')

        function_set_cmd = self.__commands.get('function_set')
        display_control_cmd = self.__commands.get('display_control')
        display_on_cmd = self.__commands.get('display_on')
        clear_cmd = self.__commands.get('clear_display')
        entry_mode_set_cmd = self.__commands.get('entry_mode_set')
        self.__write_command(0x03)
        self.__write_command(0x03)
        self.__write_command(0x03)
        self.__write_command(0x02)
        self.__write_command(function_set_cmd | line_mode_cmd | pixel_mode_cmd | bit_mode)
        self.__write_command(display_control_cmd | display_on_cmd)
        self.__write_command(clear_cmd)
        self.__write_command(entry_mode_set_cmd | entry_mode_cmd)



    @property
    def width(self) -> int:
        """
        Number of character per lines
        """
        return self.__width


    
    @property
    def rows(self) -> int:
        """
        Number of lines
        """
        return self.__rows
    

    
    def __strobe(self, data: int):
        """
        Clocks EN to latch command

        :param data: Data to write
        """
        backlight_on = self.__commands.get('backlight_on')
        self.write_byte(data | self.__en_bit | backlight_on)
        time.sleep(self.__command_delay)
        self.write_byte(((data & ~self.__en_bit) | backlight_on))
        time.sleep(self.__command_delay)



    def __write_cmd_four_bits(self, data: int):
        """
        Write 4 bits command to LCD

        :param data: 4-bit command
        """
        backlight_on = self.__commands.get('backlight_on')
        self.write_byte(data | backlight_on)
        self.__strobe(data)



    def __write_command(self, command: int, mode: int = 0):
        """
        Write a command to LCD

        :param command: Command to write
        :param mode: Write mode
        """
        self.__write_cmd_four_bits(mode | (command & 0xF0))
        self.__write_cmd_four_bits(mode | ((command << 4) & 0xF0))

        

    def __lcd_write_char(self, charvalue: int, mode=1):
        """
        Write a character to LCD

        :param charvalue: Character value
        :param mode: Write mode
        """
        self.__write_cmd_four_bits(mode | (charvalue & 0xF0))
        self.__write_cmd_four_bits(mode | ((charvalue << 4) & 0xF0))


    
    def clear(self):
        """
        Clear LCD screen
        """
        clear_cmd = self.__commands.get('clear_display')
        return_home_cmd = self.__commands.get('return_home')
        self.__write_command(clear_cmd)
        self.__write_command(return_home_cmd)



    def display_text(self, text: str, line: int = 1, pos: int = 0):
        """
        Display a text to the LCD

        :param text: String to display
        :param line: Position from the top
        :param pos: Position from left side
        :raise ValueError: If line is greater than device rows 
        :raise ValueError: If pos is greater than device width 
        """
        if line > self.__rows:
            raise ValueError('Line is greater than device rows')
        
        if pos > self.__width:
            raise ValueError('Position is greater than device width')

        if line == 1:
            new_pos = pos
        elif line == 2:
            new_pos = 0x40 + pos
        elif line == 3:
            new_pos = 0x14 + pos
        elif line == 4:
            new_pos = 0x54 + pos

        set_ddram_addr_cmd = self.__commands.get('set_ddram_addr')
        self.__write_command(set_ddram_addr_cmd + new_pos)

        for char in text:
            self.__write_command(ord(char), self.__rs_bit)



    def set_backlight(self, state: bool):
        """
        Turn on/off backlight

        :param state: Backlight state
        """
        if state:
            self.__write_command(self.__commands.get('backlight_on'))
        else:
            self.__write_command(self.__commands.get('backlight_off'))
