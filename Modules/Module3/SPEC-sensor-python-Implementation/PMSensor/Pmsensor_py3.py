#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 12 06:06:54 2021

@author: shahan
"""

import serial
import struct
import time

class ParticulateMolecular(object):
    
    HEAD = b'\xaa'
    CMD_ID = b'\xb4'
    TAIL = b'\xab'
    
    REPORT_MODE = b'\x02'
    QUERY_DATA = b'\x04'
    SET_DEVICE_ID = b'\x05'
    SLEEP_AND_WORK = b'\x06'
    SET_WOKING_PERIOD_MODE = b'\x08'
    FIRMWARE_VERSION = b'\x07'
    
    READ = b'\x00'
    WRITE = b'\x01'
    
    ACTIVE = b'\x00'
    PASSIVE_QUERY = b'\x01'
    
    DEVICE_ID_1 = b'\xff'
    DEVICE_ID_2 = b'\xff'
    
    EMPTY_BYTE = b'\x00'
    
    SLEEP = b'\x00'
    WORK = b'\x01'
    
    builder = {
        "sleep_or_wake_cmd" : False,
        "sleep" : False,
        "read" : False, 
        "write" : False,
        "active" : False,
        "passive" : False,
        "setDataReportMode" : False,
        "queryData" : False,
        "set_dev_id" : False,
        "set_working_period" : False,
        "get_firmware_version" : False
        
        }
    
    #device_ID = ["a1","1a"]
    device_ID = []
    
    # Sampling interval
    sleep_interval , wake_interval = 3 , 3
    
    def __init__(self, port, baud=9600, timeout=2):
        self.__port = port
        self.__baud = baud
        self.__timeout = timeout
        self.ser = serial.Serial(port=self.__port, baudrate=self.__baud, timeout=self.__timeout)
        self.ser.flush()
        # self.__wake()
        # self.__set_data_report_mode(True, True)

        
        
    def close_serial(self):
        self.ser.close()
    
    def __command_builder(self, worktime=0, new_dev_id_1 = b'\x00', new_dev_id_2 = b'\x00'):
        #Head
        cmd = self.HEAD + self.CMD_ID
        if self.builder["sleep_or_wake_cmd"]:
            cmd += (self.SLEEP_AND_WORK 
            + (self.READ if self.builder["read"] else self.WRITE)
            + (self.SLEEP if self.builder["sleep"] else self.WORK))
        
        if self.builder["setDataReportMode"]:
            cmd += (self.REPORT_MODE
            + (self.READ if self.builder["read"] else self.WRITE)
            + (self.ACTIVE if self.builder["active"] else self.PASSIVE_QUERY))
            
        if self.builder["queryData"]:
            cmd += (self.QUERY_DATA
            + self.EMPTY_BYTE * 2)
            
        if self.builder["set_dev_id"]:
            cmd += self.SET_DEVICE_ID
            
        if self.builder["set_working_period"]:
            cmd += (self.SET_WOKING_PERIOD_MODE
            + (self.READ if self.builder["read"] else self.WRITE)
            + bytes([worktime]))
            
        if self.builder["get_firmware_version"]:
            cmd += (self.FIRMWARE_VERSION
            + self.EMPTY_BYTE * 2)
            
        cmd += self.EMPTY_BYTE * 10
        
        if self.builder["set_dev_id"]:
            cmd += new_dev_id_1 + new_dev_id_2
            
        cmd += self.DEVICE_ID_1 + self.DEVICE_ID_2

        # Fletcher-16 checksum
        checksum = sum(b for b in cmd[2:]) % 256
        #print(f"check sum : {bytes([checksum])}  and {checksum} and {type(checksum)}")
        cmd += bytes([checksum]) + self.TAIL
        
        return cmd
        
    def sleep(self):
    
        self.builder["sleep_or_wake_cmd"] = True
        self.builder["read"] = False
        self.builder["sleep"] = True
        # print("Sleeping")
        # print(self.builder["sleep_or_wake_cmd"])
        cmd = self.__command_builder()
        # print(f"{cmd} {len(cmd)}")
        self.__write(cmd)
        # self.__reply("Sleeping")
        
        self.builder["sleep_or_wake_cmd"] = False
        self.builder["read"] = False
        self.builder["sleep"] = False
        print("PM is sleeping.")
        
        
    def wake(self):
        
        self.builder["sleep_or_wake_cmd"] = True
        self.builder["read"] = False
        self.builder["sleep"] = False
        # print("waking")
        # print(self.builder["sleep_or_wake_cmd"])
        cmd = self.__command_builder()
        # print(f"{cmd} {len(cmd)}")
        self.__write(cmd)
        # time.sleep(0.1)
        #self.__reply()
        # d = self.reply_check(b'\xc5')
        # print(f" byte reply : {d} , reply received, PMsensor")
        
        self.builder["sleep_or_wake_cmd"] = False
        self.builder["read"] = False
        self.builder["sleep"] = False
        print("PM is awake.")
        
    def __write(self, cmd):
        
        self.ser.write(cmd)
        
    def __reply(self):
        
        byte = self.ser.read(size=10)
        # d = self.ser.read(size=9)
        # full = byte + d
        # print(full)
        if len(byte) == 0:
            return None
        if (sum(d for d in byte[2:8]) & 255) != byte[8]:
            return None  #TODO: also check cmd id
        return byte
          
        
    def continuous_mode(self):
        """
        For testing , doesnot work so well
        advice : 
            For data use query mode
        """
        self.__wake()
        time.sleep(2)
        data = self.read_pm_data()
        self.__sleep()
        time.sleep(2)
        return data
        
        
        """
        data = self.read_pm_data()
        if data is not None:
            return data
        else:
            self.continuous_mode()
        """
    
    def Check_sleep_wake_reply_cycle(self):
        """
        Debug reply!!
        """
        print("wake")
        self.__wake()
        time.sleep(self.wake_interval)
        print("sleep")
        self.__sleep()
        time.sleep(self.sleep_interval)
        
    def read_pm_data(self):
        """Read sensor data.
        @return: PM2.5 and PM10 concetration in micrograms per cude meter.
        @rtype: tuple(float, float) - first is PM2.5.
        """
        
        byte = 0
        data = 0
        #self.ser.reset_input_buffer()
        #self.ser.reset_output_buffer()
        self.ser.flush()
        print("start reading")
        while byte != self.HEAD:
            
            #print("detecting start command")
            byte = self.ser.read(1)
            d = self.ser.read(10)
            if d[0:1] == b"\xc0":
                full = byte + d 
                data = self.__data(full)
                return data
                #print("While loop of read pm data function.")
                #print(f"d : {d} len : {len(d)}")
                #print(f"byte : {byte} ")
                #print(f"byte + d {full} len : {len(full)}")
        
      
    def __data(self, data):
        """Process a SDS011 data frame.
        Byte positions:
            0 - Header
            1 - Command No.
            2,3 - PM2.5 low/high byte
            4,5 - PM10 low/high
            6,7 - ID bytes
            8 - Checksum - sum of bytes 2-7
            9 - Tail
        """
        # print(f"data rep : {data} {len(data)}")
        if len(data) != 11:
            return None
        raw = struct.unpack('<HHxxBBB', data[2:])
        checksum = sum(v for v in data[2:8]) % 256
        if checksum != data[8]:
            return None
        pm25 = raw[0] / 10.0
        pm10 = raw[1] / 10.0
        print(f"pm25 {pm25} pm10 {pm10}")
        if pm25 is None or pm10 is None:
            return None
        return (pm25, pm10)
    
    def __process_version(self,d):
        raw = struct.unpack('<BBBHBB', d[3:])
        checksum = sum(v for v in d[2:8]) % 256
        if checksum == d[8]:
            # print(f"Y : {raw[0]}, M : {raw[1]}, D : {raw[2]}, ID : {hex(raw[3])}, CRC : OK")
            return raw
        else:
            # print("CRC : NOK")
            return None
        
    def __set_data_report_mode(self, read, active):
        """
        Default factory settings!!
        """
        self.builder["setDataReportMode"] = True
        self.builder["read"] = read
        self.builder["active"] = active
        
        #print(self.builder["setDataReportMode"])
        cmd = self.__command_builder()
        #print(f"{cmd} {len(cmd)}")
        self.__write(cmd)
        #raw = self.__reply()
        raw = self.reply_check(b'\xc5')
        #print(f"report raw : {raw}")
        self.builder["setDataReportMode"] = False
        self.builder["read"] = False
        self.builder["active"] = False
        
    def __set_query_mode(self):
        
        self.builder["queryData"] = True
        # print(self.builder["queryData"])
        cmd = self.__command_builder()
        # print(f"{cmd} {len(cmd)}")
        self.__write(cmd)
        data = self.read_pm_data()
        print(data)
        
        self.builder["queryData"] = False
        return data
        
    def __set_device_id(self):
        """
        Run Instructions: 
            Only run this subroutine after self.Check_firmware_version()
            in the same main function.
        """
        
        self.builder["set_dev_id"] = True
        # print(self.builder["set_dev_id"])
        dev1, dev2 = self.__process_device_id()
        cmd = self.__command_builder(new_dev_id_1 = dev1, new_dev_id_2 = dev2)  
        # print(f"{cmd} {len(cmd)}")
        # print(self.builder)
        
        self.__write(cmd)
        self.__reply()
        
        self.builder["set_dev_id"] = False
        
    def __set_working_period(self):
        
        self.builder["set_working_period"] = True
        # print(self.builder["set_working_period"])
        cmd = self.__command_builder(worktime=0)
        
        self.__write(cmd)
        self.__reply()
        # print(f"{cmd} {len(cmd)}")
        
        self.builder["set_working_period"] = False
        
    def Check_firmware_version(self):
        
        self.builder["get_firmware_version"] = True
        # print(self.builder["get_firmware_version"])
        cmd = self.__command_builder()
        # print(f"cmd firmware : {cmd}")
        self.__write(cmd)
        # self.__write(cmd)
        # time.sleep(0.5)
        raw = self.reply_check(b'\xc5')
        print(f"raw : {raw}")
        if raw != None:
            self.__process_version(raw)
            print(f"Y : {raw[0]}, M : {raw[1]}, D : {raw[2]}, ID : {hex(raw[3])}, CRC : OK")
        
        
            self.device_ID.append(raw[6])
            self.device_ID.append(raw[7])
            print(self.device_ID)
        else:
            raw = self.ser.read(10)
            print("read error, check reply")
            print(f"manual reply : {raw}")
        # print(f"{cmd} {len(cmd)}")
        
        self.builder["get_firmware_version"] = False
    
    def __process_device_id(self):
        
        dev_id_1 = struct.pack('B', self.device_ID[0])
        dev_id_2 = struct.pack('B', self.device_ID[1])
        return dev_id_1, dev_id_2
        
    
    def reply_check(self, byte_to_check_for):
        
        """
        Debug purpose
        """
        byte = 0

        while byte != self.HEAD:
            # self.ser.flush()
            byte = self.ser.read(size=1)
            d = self.ser.read(size=9)
            print(byte + d)
            if d[0:1] == byte_to_check_for:   
                return byte + d
            
            # print("looping")
    def set_report_mode(self, read, active):
        self.__set_data_report_mode(read, active)
        
    def main(self):
        
        try:
            self.wake()
            time.sleep(self.wake_interval)
            
            self.Check_firmware_version()
            time.sleep(2)
            
            self.sleep()
            time.sleep(5)
            
            while True:
                # data = self.continuous_mode()
                self.wake()
                time.sleep(2)
                data = self.read_pm_data()
                # data = self.__set_query_mode()
                # print(data)
                if data != None:
                    print(f"pm2.5 and pm10 : {data[0]} {data[1]}")
                else:
                    print("None Type error")
                    
                self.sleep()
                time.sleep(6)
                # time.sleep(3)
                
               
        except KeyboardInterrupt:
            print('Interrupted')
            self.sleep()
            time.sleep(self.sleep_interval)
            # time.sleep(1)
            self.close_serial()
        
        
if __name__ == '__main__':
    
    pms = ParticulateMolecular('/dev/ttyUSB0')
    pms.main()
        
