import sys
sys.path.append('../')

from ..base import GpioDevice, PwmDevice
from raspidevkit.constants import OUTPUT
from raspidevkit.utils import soundutil
from typing import Union
import time


class ActiveBuzzer(GpioDevice):
    def __init__(self, machine, pin: int):
        """
        Create an active buzzer object

        :param pin: Pin this device is attached to
        """
        pin_setup = {
            str(pin): OUTPUT
        }
        super().__init__(machine, pin_setup, device_type=OUTPUT)
        self._state = False



    @property
    def state(self):
        """
        Device current state
        """
        return self._state
    


    def turn_on(self):
        """
        Turn this buzzer on
        """
        if not self.state:
            self.gpio_write(self.pin, True)
            self._state = True



    def turn_off(self):
        """
        Turn this buzzer off
        """
        if self.state:
            self.gpio_write(self.pin, False)
            self._state = False



class PassiveBuzzer(PwmDevice):
    def __init__(self, machine, pin: int) -> None:
        """
        Create a passive buzzer object

        :param pin: Pin this device is attached to
        """
        super().__init__(pin, 440)
        self._machine = machine



    def buzz(self, frequency: int, duration: float = None):
        """
        Activate buzzer with defined frequency.
        If duration not set, must manually call `stop()`

        :param frequency: Frequency
        :param duration: Play for x seconds (blocking)(optional).
        """
        self.start(50)
        self.change_frequency(frequency)
        if duration:
            time.sleep(duration)
            self.stop()
        


    def play_note(self, note: str, duration: float = 1):
        """
        Play a note
        If duration not set, must manually call `stop()`

        :param note: a note like string (e.g. F4, FS3)
        :param duration: Play for x seconds
        """
        self.start(50)
        frequency = soundutil.get_note_frequency(note)
        self.buzz(frequency, duration)



    def play_music(self, notes: Union[list[str], tuple[str]], beats: Union[list[int], tuple[int]]):
        """
        Play a music from notes and beats

        :param notes: Iterables of note like strings
        :param beats: Iterables of beats
        """
        music = zip(notes, beats)
        for note, beat in music:
            self.play_note(note, beat)



    def __repr__(self):
        return f"Buzzer <pin={self.pin}, state={self._state}>"
