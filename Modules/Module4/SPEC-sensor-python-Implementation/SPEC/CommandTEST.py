#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 21:40:28 2021

@author: shahan
"""

import serial
import struct
import time

class TsT():
    
    def __init__(self, port, baud, timeout=1):
        self.__port = port
        self.__baud = baud
        self.__timeout = timeout
        
    def Check_command(self,command_read, command_check):
        if (command_read == command_check):
            return True
        else:
            return False
        
    def main(self):
        
        # barcode = "022321011118 110102 CO 2103 4.21"
        # barcode = barcode.encode()
        # print(barcode)
        # barcode = struct.unpack('32c', barcode)
        # print(f"port {self.__port} baud : {self.__baud} timeout : {self.__timeout}")
        # print(f"port {type(self.__port)} baud : {type(self.__baud)} timeout : {type(self.__timeout)}")
        ser = serial.Serial(port = self.__port , baudrate=self.__baud, timeout=self.__timeout)
        ser.flushInput()
        ser.write(b'Z')
        time.sleep(0.2)
        
        
        
        # while(ser.is_open):
        #     command = ser.readline().decode('utf-8')
        #     print(command)
        #     command = ser.readline().decode('utf-8').strip()
        #     print(command)
        #     command_bool = self.Check_command(command, "Remove Sensor and Scan:")
        #     print(command_bool)
        #     if(command_bool):
        #         for i in barcode:
        #             ser.write(i)
        #             time.sleep(0.01)
        #         ser.write(b'\r')
        #     else:
        #         print("Failed Entering Barcode!!")
        #         break
            
        #     command = ser.readline()
        #     print(command)
        #     command = ser.readline()
        #     print(command)
        #     command = ser.readline()
        #     print(command)
        #     break
        
        for i in range(3):
            data = ser.readline().decode().strip()
            print(data)
            # if i == 0:
            #     print(data.strip())
            # if i != 0:
            #     data = data.split('=')
            #     print(data)
        ser.close()

if __name__ == '__main__':
    
    t = TsT("/dev/ttyUSB0" , 9600, timeout=1)
    t.main()
