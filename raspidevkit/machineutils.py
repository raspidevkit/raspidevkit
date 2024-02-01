import re

class dictutils:
    """
    Dictionary utility helper
    """

    @staticmethod
    def get(dictionary: dict, *keys: str, default=None,):
        """
        Traverse a dictionary in a tree-like structure

        :param *keys: Keys to search
        :param default: Value to return if key not found else raise KeyError
        :return: Value
        """
        current_value = dictionary
        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                if default:
                    return default
                raise KeyError(f'Key not found: {key}')
        return current_value
    


    @staticmethod
    def map_key_value(keys: list, values: list) -> dict:
        """
        Map a values to keys.

        :param keys: List of keys
        :param values: List of values
        :return: Mapped dictionary
        """
        result_dict = dict(zip(keys, values))
        return result_dict
    


    @staticmethod
    def does_keys_exists(dictionary: dict, keys: list[str], strict: bool = True) -> bool:
        """
        Check if all keys exists in the input dictionary

        :param dictionary: Dictionary to check
        :param keys: List of keys to validate
        :param strict: Should all keys exist in the dictionary
        """

        if strict:
            for key in keys:
                if not key in dictionary.keys():
                    return False
            return True
        
        else:
            for key in keys:
                if key in dictionary.keys():
                    return True
            return False

    


class formatutil:
    """
    Formatter utility helper
    """

    @staticmethod
    def snake_to_camel(text: str) -> str:
        """
        Convert a snake_case string to camelCase

        :param text: snake_case string
        :return: camelCase string
        """
        parts = text.split('_')
        camel_case = parts[0] + ''.join(word.capitalize() for word in parts[1:])
        return camel_case
    


    @staticmethod
    def escape_whitespace(text: str) -> str:
        """
        Escape whitespace characters

        :param text: Raw string
        :return: Escaped string
        """
        chars = {
            '\r': '\\r',
            '\n': '\\n',
            '\t': '\\t',
            '\f': '\\f',
            '\v': '\\v'
        }
        result = text
        for key, value in chars.items():
            result = result.replace(key, value)
        return result
    


class soundutil:
    """
    Sound utility helper
    """

    @staticmethod
    def get_note_frequency(note: str) -> int:
        """
        Get equivalent frequency of a note

        :param note: Note
        :return: Frequency
        :raises: Value Error if note is not supported 
        """
        notes = {'B0': 31, 'C1': 33, 'CS1': 35, 'D1': 37, 'DS1': 39, 
                 'E1': 41, 'F1': 44, 'FS1': 46, 'G1': 49, 'GS1': 52, 
                 'A1': 55, 'AS1': 58, 'B1': 62, 'C2': 65, 'CS2': 69, 
                 'D2': 73, 'DS2': 78, 'E2': 82, 'F2': 87, 'FS2': 93, 
                 'G2': 98, 'GS2': 104, 'A2': 110, 'AS2': 117, 'B2': 123, 
                 'C3': 131, 'CS3': 139, 'D3': 147, 'DS3': 156, 'E3': 165, 
                 'F3': 175, 'FS3': 185, 'G3': 196, 'GS3': 208, 'A3': 220, 
                 'AS3': 233, 'B3': 247, 'C4': 262, 'CS4': 277, 'D4': 294, 
                 'DS4': 311, 'E4': 330, 'F4': 349, 'FS4': 370, 'G4': 392, 
                 'GS4': 415, 'A4': 440, 'AS4': 466, 'B4': 494, 'C5': 523, 
                 'CS5': 554, 'D5': 587, 'DS5': 622, 'E5': 659, 'F5': 698, 
                 'FS5': 740, 'G5': 784, 'GS5': 831, 'A5': 880, 'AS5': 932, 
                 'B5': 988, 'C6': 1047, 'CS6': 1109, 'D6': 1175, 'DS6': 1245, 
                 'E6': 1319, 'F6': 1397, 'FS6': 1480, 'G6': 1568, 'GS6': 1661, 
                 'A6': 1760, 'AS6': 1865, 'B6': 1976, 'C7': 2093, 'CS7': 2217, 
                 'D7': 2349, 'DS7': 2489, 'E7': 2637, 'F7': 2794, 'FS7': 2960, 
                 'G7': 3136, 'GS7': 3322, 'A7': 3520, 'AS7': 3729, 'B7': 3951, 
                 'C8': 4186, 'CS8': 4435, 'D8': 4699, 'DS8': 4978
                }
        frequency = notes.get(note.upper())
        if not frequency:
            raise ValueError('Note is not supported.')
        return frequency



class mathutil:
    """
    Math utility helper
    """

    @staticmethod
    def map_range(x: float, in_min: float, in_max: 
                  float, out_min: float, out_max: float) -> float:
        """
        Get the x equivalent based on min and max value.
        Just like `map` function of Arduino

        :param x: Input to check for equivalent
        :param in_min: Input lowest value
        :param in_max: Input highest value
        :param out_min: Output lowest value
        :param out_max: Output lowest value
        :return: Output equivalent value
        """
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
    