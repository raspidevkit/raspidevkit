import serial
import time
import datetime
import re


class Sim808(serial.Serial):
    def __init__(self, machine, port: str | None = None, baudrate: int = 9600, **kwargs) -> None:
        """
        Initialize SIM808 device. 

        :param machine: Machine instance as this device parent
        :param port: Port the SIM808 attach to
        :param baudrate: Baudrate of serial commnication
        :param **kwargs: Other args for serial.Serial object
        """
        super().__init__(port, baudrate, **kwargs)
        self.__initialize()
        self._machine = machine



    def __initialize(self):
        """
        Check if SIM808 exists and functioning
        """
        self.send_command('AT\r\n')
        response = self.read_response()
        if('OK' not in response):
            raise Exception('Error starting sim808')
        self.send_command('AT+CMGF=1\r\n')
        self.read_response()
 


    def cleanup(self):
        """
        Perform cleanup
        """
        self.reset_input_buffer()
        self.reset_output_buffer()
        self.close()



    def read_response(self):
        """
        Get the response from SIM808 Serial COM

        :return: SIM808 response
        """
        response = ''
        while(self.in_waiting):
            bit = self.read()
            response = response + bit.decode()
        return response
 


    def send_command(self, command: str, delay: float = 1):
        """
        Send a command to SIM808 Serial COM

        :param command: Command to send
        :param delay: Delay allows module to recieve command in full
        """
        self.write(command.encode())
        time.sleep(delay)
 


    def send_sms(self, number: str, message: str):
        """
        Send a SMS message

        :param number: Number to send message to. Should contain country code
        :param message: Message to send
        """
        self.send_command('AT+CMGS="' + number + '"\r')
        time.sleep(0.1)
        self.send_command(message + '\x1A\n')
        time.sleep(0.1*(len(message)/5))
        response = self.read_response()
        while 'OK' not in response:
            time.sleep(0.1)
            response = self.read_response()



    def read_unread_sms(self):
        """
        Get unread sms

        :return: unread sms
        """
        self.send_command('AT+CMGL=\"REC UNREAD\"\r\n')
        time.sleep(1)
        response = self.read_response()
        return response



    def get_time(self):
        """
        Get network date and time

        :return: Network date and time
        """
        self.send_sms("+639155882825", "CLOCK COMMAND")
        start_time = datetime.datetime.now()
        time.sleep(3)
        messages = self.read_unread_sms()
        end_time = datetime.datetime.now()
        datetime_pattern = r'\d{2}/\d{2}/\d{2},\d{2}:\d{2}:\d{2}\+32'
        match = re.findall(datetime_pattern, messages)
        if match:
            returned_datetime = datetime.datetime.strptime(match[-1].replace('+32',''),'%y/%m/%d,%H:%M:%S')
            returned_datetime += (end_time - start_time)
        return returned_datetime
    


    def delete_all_sms(self):
        """
        Delete all stored sms (inbox and sent)
        """
        self.send_command('AT+CMGD=1,4\r\n')
        time.sleep(5)
