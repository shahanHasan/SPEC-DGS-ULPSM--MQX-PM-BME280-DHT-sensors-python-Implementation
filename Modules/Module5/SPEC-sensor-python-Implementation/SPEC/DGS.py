#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  2 19:03:32 2021

@author: shahan, Redwan
"""
import serial
import struct
import time
import numpy as np
import pprint

class DGS(object):
    """
    A class used to represent SPEC DGS sensors.

    Attributes
    ----------
    serial : TYPE -> serial object
    Port : TYPE -> str , port used by the device
        
    Baudrate: TYPE -> int

    User inputs are 
    '\r'
    'c' set to continuous approx. 4 mA to ground (not including uart consumption)
    'S' set span accepts a PPM float above 1.0 "\r\nEnter span gas value in PPM:" atof() "\r\nSetting span..." then:
                          either "done\r\n" or "Temperature error, " or "ADC range error, " or "Serial number error, " & "no changes made\r\n"
    'Z' zero sensor "\r\nSetting zero..." either "done\r\n", "Temperature error, " or "ADC range error, " and "no changes made\r\n"
    'f' output firmware should be "15SEP17\r\n"
    'l' get LMP values: "                               LMP91000 Values\r\n", "LMP91000 Register 0x10= 3\r\n","LMP91000 Register 0x11= 145\r\n","LMP91000 Register 0x12= 3\r\n"
    'L' set LMP values: "\r\nEnter LMP91000 Register 0x10:",atoi(),"\r\nEnter LMP91000 Register 0x11:",atoi(),"\r\nEnter LMP91000 Register 0x12:",atoi(),"\r\n"
    'T' set Temperature offset: "\r\nEnter Temperature_Offset: ", atof(), "\r\n"
    'A' set average: "\r\nEnter Average Total: ", atoi(), "\r\n"
    'B' set Barcode: "\r\nRemove Sensor and Scan: ", BC,"\r\nSetting OC...done\r\nSetting zero...done\r\n"
    'e' get eeprom: "                               EEPROM Values\r\n"
        nA_per_PPM_x100= 340
        ADC_OC= 13035
        ADC_Zero= 13035
        ADC_Span= 16299
        Temperature_Offset_x1000= 1000
        T_Zero= 25336
        RH_Zero= 27602
        T_Span= 25052
        RH_Span= 27710
        LMP91000 Register 0x10= 3
        LMP91000 Register 0x11= 145
        LMP91000 Register 0x12= 3
        Average_Total= 1
        Barcode= 042617040460 110102 CO 1705 2.72
        Serial_Number= 042617040460
        Part_Number= 110102
        Gas= CO
        Date_Code= 1705
        Sensitivity_Code= 2.72\r\n
        
    'r' reset: locks to reset WDT
    's' sleep approx. 30 uA to ground
    
    """
    ##########################################################
    # Variables
    ##########################################################
    EEPROM_dict = {}
    LMP = {}
    sensor_data = {}
    Names = ['SN', 'PPB', "TEMP", "RH", "RawSensor", "TempDigital", "RHDigital", "Day", "Hour", "Minute", "Second" ]
    Debug = False
    __is_sleeping = False
    Firmware_readout = ""
    
    
    def __init__(self, port, baud, timeout=1):
        
        self.__port = port
        self.__baud = baud
        self.__timeout = timeout
        self.ser = serial.Serial(port=self.__port, baudrate=self.__baud, timeout=self.__timeout)
        
    def sensor_sleep(self):
        
        self.__is_sleeping = True
        code = b's'
        print(f"Going to sleep, code : {code}")
        while self.ser.is_open:
            self.ser.flush()
            self.write_data(byte_string=code)
            time.sleep(2)
            break
        print("Sleeping")
        
    def reset(self):
        code = b'r'
        print("Resets Module")
        while self.ser.is_open:
            self.ser.flush()
            self.write_data(byte_string=code)
            # 5 second delay after reset.
            time.sleep(5)
            break
        print("Sensor is reset.")
    
    def sensor_wake(self):
        
        self.__is_sleeping = False
        code = b'start'
        print(f"Waking up , code : {code}")
        while self.ser.is_open:
            self.ser.flush()
            self.write_data(byte_string=code)
            time.sleep(2)
            break
        print("Sensor Awake")
        

    def set_continous_mode(self,c=b'c'):
        
        connection = self.ser.is_open
        
        if connection:
            self.ser.reset_output_buffer()
            self.ser.flush()
            self.write_data()
            time.sleep(1)
            self.ser.flush()
            self.write_data(byte_string=c)
                
        else:
            print("Serial port is not open")
            print("Openning")
            self.ser.open()
            self.set_continous_mode()
            
    def __get_continuous_data(self):
        """
        SN [XXXXXXXXXXXX], PPB [0 : 999999], TEMP [-99 : 99], RH [0 :
        99], RawSensor[ADCCount], TempDigital, RHDigital, Day [0 : 99], Hour [0 : 23], 
        Minute [0 : 59], Second [0 : 59]
        """
        
        try:
            self.ser.reset_input_buffer()
            self.ser.flush()
            resp = self.read_data(time_out=0.2)
            resp = resp.split(sep=",")
            if (len(resp) < 10):
                print("data is short")
                #self.set_continous_mode()
                self.__get_continuous_data()
            for i,j in zip(resp, self.Names):          
                self.sensor_data[j] = i.lstrip().rstrip()

        except serial.SerialException as e:
            #There is no new data from serial port
            self.close_serial()
        except TypeError as e:
            #Disconnect of USB->UART occured
            raise IOError
            raise OSError
            print("Disconnected : connect it back ")
            self.close_serial()

    def stop_continuous_data_flow(self):
        c = b'R'
        c = b'r'
        self.ser.reset_output_buffer()
        self.ser.flush()
        self.write_data(byte_string=c)
        time.sleep(2)
        print("stopped data transmission")
        
    def get_sensor_data(self):
        self.__get_continuous_data()
        #pprint.pprint(self.sensor_data)
    
    def close_serial(self):
        self.ser.close()
    
    def read_data(self, time_out=0):
        time.sleep(time_out)
        resp = self.ser.readline().decode()
        if resp is not None:
            return resp
        else:
            self.read_data()
    
    def write_data(self, byte_string=b'\r'):
        self.ser.write(byte_string)
    
    
    def Check_command(self,command_read, command_check):
        if (command_read == command_check):
            return True
        else:
            return False
    
    def __EEPROM_Data_read(self):
        
        for _ in range(19):
            
            data = self.read_data(time_out=0.2)
            data = data.split(sep="=")
            data[1] = data[1].lstrip().rstrip()
            self.EEPROM_dict[data[0]] = data[1]
                
        
    def __EEPROM_setup(self):
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()
        self.ser.flush()
        self.write_data(byte_string=b'e')
        time.sleep(1)
        
        command_read = self.read_data().strip()
        command_bool = self.Check_command(command_read,"EEPROM Values")
        return command_bool
    
    def __get_EEPROM(self):
        
        command_bool = self.__EEPROM_setup()
        if command_bool == True:
            print(f"command bool : {command_bool}")
            self.__EEPROM_Data_read()
        if command_bool == False:
            print(f"command bool : {command_bool}")
            self.__get_EEPROM()
                
    def __print_EEPROM_Data(self):
        pprint.pprint(self.EEPROM_dict)
        
    def EEPROM(self):
        self.__get_EEPROM()
        self.__print_EEPROM_Data()
    
    def unlock(self):
        code = "12345"
        print(f"Unlocking , code : {code}\r")
        self.ser.flush()
        self.write_data(byte_string=b'12345\r')
        time.sleep(0.5)
        
    def set_temperature_offset(self, offset=0):
        offset = str(offset).encode()
        print("Starting Temperature OFFset adjustment")
        code = b"T"
        print(f"Temperature offset code : {code}\r")
        self.ser.flush()
        self.write_data(byte_string=code)
        #self.write_data()
        time.sleep(0.2)
        
        while(self.ser.is_open):
            command = self.read_data()
            command = self.read_data()
            command_bool = self.Check_command(command, "Enter Temperature_Offset: ")
            if(command_bool):
                self.write_data(byte_string=offset)
                self.write_data()
                return True
            else:
                print("Temperature adjustment failed")
                return False
                
            break
        time.sleep(2)
        
    def set_barcode(self, Barcode):
        
        num = len(Barcode)
        Barcode = Barcode.encode()
        
        Barcode = struct.unpack(f'{num}c', Barcode)
        print("Setting Barcode")
        code = b"B"
        print(f"Barcode set code : {code}\r")
        self.ser.flush()
        self.write_data(byte_string=code)
        #self.write_data()
        time.sleep(0.2)
        while(self.ser.is_open):
            command = self.read_data()
            command = self.read_data()
            command_bool = self.Check_command(command, "Remove Sensor and Scan: ")
            if(command_bool):
                for i in Barcode:
                    self.write_data(byte_string=i)
                    time.sleep(0.01)
                self.write_data()
            else:
                print("Failed Entering Barcode!!")
                break
            
            command = self.read_data()
            print(command)
            command = self.read_data()
            print(command)
            command = self.read_data()
            print(command)
            
            break
            
        time.sleep(2)
        
    def get_firmware_readout(self):
        
        code = b"f"
        print(f"Firmware readout code : {code}\r")
        self.ser.flush()
        self.write_data(byte_string=code)
        #self.write_data()
        time.sleep(0.2)
        while(self.ser.is_open):  
            for _ in range(1):
                fw = self.read_data().strip()
                #fw = self.read_data()
                print(f'command : {fw}')
            command_bool = self.Check_command(fw, "15SEP17")
            print(command_bool)
            if(command_bool):
                self.Firmware_readout = fw
                print(f"Firmware Version : {fw}")
            else:
                print("Unsupported FW , try again")
            
            break  
        time.sleep(1)
    
    def getLMP(self):
        code = b"l"
        print("Getting LMP Registors : ")
        self.ser.flush()
        self.write_data(byte_string=code)
        time.sleep(0.2)
        while(self.ser.is_open):
            command = self.read_data().strip()
            print(f'command : {command}')
            command_bool = self.Check_command(command, "LMP91000 Values")
            if (command_bool):
                for i in range(3):
                    data = self.read_data()
                    data = data.split('=')
                    self.LMP[data[0]] = int(data[1].lstrip().rstrip())
                    
                    #print(command)
            else:
                #self.getLMP()
                print("Sensor Error , Try again")
            
            break
        print("LMP register values : ")
        pprint.pprint(self.LMP)
        time.sleep(1)
            
    def set_LMP(self, R1, R2, R3):
        
        print("Setting LMP Registers : ")
        code = b"L"
        self.ser.flush()
        self.write_data(byte_string=code)
        time.sleep(0.2)
        #First register
        while(self.ser.is_open):
            command = self.read_data()
            command = self.read_data().strip()
            print(f'command : {command}')
            command_bool = self.Check_command(command, "Enter LMP91000 Register 0x10:")
            if (command_bool):
                self.write_data((str(R1)).encode())
                self.write_data()
            
            else:
                print("Failed entering register value")
                return 0
            break
        #First register check
        while(self.ser.is_open):
            val = self.read_data().strip()
            print(val)
            if(int(val) != R1):
                print("Failure")
                return 0
            break
        
        #2nd register
        while(self.ser.is_open):
            command = self.read_data().strip()
            print(f'command : {command}')
            command_bool = self.Check_command(command, "Enter LMP91000 Register 0x11:")
            if (command_bool):
                self.write_data((str(R2)).encode())
                self.write_data()
            
            else:
                print("Failed entering register value")
                return 0
            break
        #2nd register check
        while(self.ser.is_open):
            val = self.read_data().strip()
            print(val)
            if(int(val) != R2):
                print("Failure")
                return 0
            break
        
        #3rd register
        while(self.ser.is_open):
            command = self.read_data().strip()
            print(f'command : {command}')
            command_bool = self.Check_command(command, "Enter LMP91000 Register 0x12:")
            if (command_bool):
                self.write_data((str(R3)).encode())
                self.write_data()
            
            else:
                print("Failed entering register value")
                return 0
            break
        #3rd register check
        while(self.ser.is_open):
            val = self.read_data().strip()
            print(val)
            if(int(val) != R3):
                print("Failure")
                return 0
            else:
                
                print("success")
                time.sleep(2)
                return 1
               
        
    def get_registor_values(self):
    
        if self.LMP is not None:
            pprint.pprint(self.LMP)
            values = []
            for i in self.LMP:
                values.append(self.LMP[i])
            r1 , r2 , r3 = values[0], values[1], values[2]
            return r1, r2, r3
        else:
            print("NO values recorded")
            return 0
                 
    def span_user_calibration(self, X):
        
        print("Span user caibration starting!")
        code = b'S'
        self.ser.flush()
        self.write_data(byte_string=code)
        time.sleep(0.2)
        
        while(self.ser.is_open):
            command = self.read_data().strip()
            print(f'command : {command}')
            command_bool = self.Check_command(command, "Enter Unlock Code:")
            print(f"bool {command_bool}")
            if (command_bool):
                self.unlock()
            else:
                print("Failed unlock sequence")
                return 0
            break
        
        while(self.ser.is_open):
            command = self.read_data().strip()
            time.sleep(0.1)
            print(f'command : {command}')
            command_bool = self.Check_command(command, "Enter span gas value in PPM:")
            print(f"bool {command_bool}")
            if (command_bool):
                self.write_data((str(X)).encode())
                self.write_data()
            
            else:
                print("Failed entering span gas value in PPM")
                return 0
            break
        
        while(self.ser.is_open):
            insf = self.read_data().strip()
            print(insf)
            if(float(insf) == X):
                print("Matched - insf and X")
                
            else:
                print("Does not match")
                return 0
            
            break
        
        while(self.ser.is_open):
            commandString1 = self.read_data()
            print(f"command string 1  :  {commandString1}")
            time.sleep(0.2)
            commandString2 = self.read_data().strip()
            print(f"command string 2  :  {commandString1}")
            command_bool = self.Check_command(commandString2, "done")
            if(command_bool):    
                print("Success")
                time.sleep(0.5)
                return 1
            else:
                
                print("Failed Span Calibration")
                time.sleep(0.5)
                return 0

    def zero_calibration(self):
        code = b"Z"
        print("Starting Zero Calibration : ")
        command_bool = False
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()
        self.ser.flush()
        # self.ser.write(b'start')
        # time.sleep(1)
        self.write_data(byte_string=code)
        self.write_data(byte_string=code)
        time.sleep(1)
        while(self.ser.is_open):
            # self.ser.reset_output_buffer()
            # self.ser.reset_input_buffer()
            # self.ser.flush()
            
            
            # command = self.read_data().strip()
            # print(f'command : {command}')
            # command_bool = self.Check_command(command, "Setting zero...done")
            # # time.sleep(0.2)
            i = 0
            while command_bool == False:
                i += 1
                command = self.read_data().strip()
                print(f'command : {command}')
                command_bool = self.Check_command(command, "Setting zero...done")
                if i == 6:
                    command_bool = False
                    break
            
            # command = self.read_data().strip()
            # print(f'command : {command}')

            if (command_bool):
                print("Calibration Completed!!!")
                return True
            else:
                print("Calibration failed")
                print(f'command : {command}')
                return False
                
            break
                
    def set_average(self,t):
        print("Changes the number of samples in the running average (1 to 300 seconds)")
        
        if(t > 300):
            t = 300
        if(t<1):
            t = 1
        code = b"A"
        self.ser.flush()
        self.write_data(byte_string=code)
        time.sleep(0.2)
        while(self.ser.is_open):
            command = self.read_data().strip()
            print(f'command : {command}')  
            command_bool = self.Check_command(command, "Enter Average Total:")
            if (command_bool):
                self.write_data(str(t).encode())
                self.write_data()
                time.sleep(0.1)
            else:
                print("setting average failed")
                return 0
                
            break
        
        while(self.ser.is_open):
            commandString = self.read_data().strip()
            print(f"final command : {commandString}")
            return 1
        
    def get_conc_ppm(self):
        ppb = self.sensor_data['PPB']
        ppm = round(int(ppb) / 1000, 2)
        return ppm
    def get_temp(self):
        temp = self.sensor_data['TEMP']
        return int(temp)
    
    def get_rh(self):
        rh = self.sensor_data['RH']
        return int(rh)
    
    def get_sensitivity_code(self):
        sense = self.EEPROM_dict['Sensitivity_Code']
        return int(sense)
    
    def get_gas_name(self):
        gas = self.EEPROM_dict['Gas']
        return gas
         
if __name__ == "__main__": 
    try:
        CO = DGS('/dev/ttyUSB0', 9600, 1)
        CO.sensor_wake()
        CO.EEPROM()
        CO.get_firmware_readout()
        CO.getLMP()
        r1, r2, r3 = CO.get_registor_values()
        if(r1 != 0 and r2 != 0 and r3 != 0):
            print(f"{r1} {r2} {r3}")
            #CO.set_LMP(r1,r2,r3)
        #CO.getLMP()
        time.sleep(1)
        CO.set_continous_mode()
        i = 0
        while (i < 15):
            i += 1
            CO.get_sensor_data()
            conc = CO.get_conc_ppm()
            temp = CO.get_temp()
            rh = CO.get_rh()
            print(f"concentration : {conc} temp : {temp} rh : {rh}")
            
        
        
        # # CO.set_temperature_offset(0)
        # # CO.EEPROM()
        # #022321011118 110102 CO 2103 4.21
        
        # CO.set_barcode("022321011118 110102 CO 2103 4.21")
        # CO.EEPROM()
        CO.sensor_sleep()
        CO.close_serial()
                
    except KeyboardInterrupt:
        print('Interrupted')
        CO.sensor_sleep()
        CO.close_serial()
    
    # SO2 = DGS("/dev/ttyUSB1", 9600, 1)
    # SO2.EEPROM()
    
    
    