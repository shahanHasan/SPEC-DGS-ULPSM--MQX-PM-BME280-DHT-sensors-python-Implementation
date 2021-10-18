#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 13:30:20 2021

@author: shahan
"""
from DGS import DGS
import time
import pprint

class Setup(object):
    
    def __init__(self, BC, port, baud=9600, timeout=1):
        self.gas = DGS(port, baud, timeout)
        self.__BC = BC
        
    
    def Gas(self):
        return self.gas
    
    def fw(self):
        
        self.gas.get_firmware_readout()
        firmware = self.gas.Firmware_readout
        return firmware
        
    def set_BC(self, BC):
        
        self.gas.set_barcode(BC)
        print(f"Barcode : {BC}")
        
    def set_T_off(self, offset=0):
        
        bool_val = self.gas.set_temperature_offset(offset)
        if(bool_val):
            print(f"temp offset : {offset}")
        else: 
            print("Try again, Debug!")
        
    def get_LMP(self):
        
        # time.sleep()
        self.gas.getLMP()
        r1, r2, r3 = self.gas.get_registor_values()
        return r1, r2, r3
        
    def set_LMP(self, r1, r2, r3):
        
        val = self.gas.set_LMP(r1,r2,r3)
        return val
        
    def get_EEPROM(self):
        
        self.gas.EEPROM()
        eeprom = self.gas.EEPROM_dict
        return eeprom
        
    def zeroing(self):
        
        bool_val = self.gas.zero_calibration()
        if(bool_val):
            print("Finished setting zero.")
            print("Finished Setup")
        else:
            print("Retry, calibration failed")
    
    def wake(self):
        self.gas.sensor_wake()
        
    def sleep(self):
        self.gas.sensor_sleep()
        
    def close_serial(self):
        self.gas.close_serial()
    
    def main(self):
        
        try:
            self.wake()
            time.sleep(1)
            
            print("Begin setup")
            
            print()
            eeprom = self.get_EEPROM()
            print()
            
            firmware = self.fw()
            print(f"firmware : {firmware}")
            # time.sleep(1)
            
            print()
            print("set barcode")
            self.set_BC(self.__BC)
            # time.sleep(1)
            
            r1, r2, r3 = self.get_LMP()
            time.sleep(1)
            val = self.set_LMP(r1,r2,r3)
            if val == 0:
                print("Failed , try again")
                return 1
            else:
                print("success")
            time.sleep(1)
            
            print()
            self.set_T_off()
            print()
            time.sleep(0.5)
            
            
            print()
            eeprom = self.get_EEPROM()
            time.sleep(2)
            
            self.gas.set_continous_mode()
            # self.gas.set_continous_mode()
            
            time.sleep(1)
            i = 0
            print("Pre Calibration")
            
            while (i < 20):
                i += 1
                
                self.gas.get_sensor_data()
                conc = self.gas.get_conc_ppm()
                temp = self.gas.get_temp()
                rh = self.gas.get_rh()
                if conc is not None and temp is not None or rh is not None:
                    print(f"concentration : {conc} temp : {temp} rh : {rh}")
                    time.sleep(1)
                
        
            self.gas.stop_continuous_data_flow()
            # self.gas.stop_continuous_data_flow()
            time.sleep(5)            
            
            print()
            print("Sensor Stabilized.")
            print("Remove the sensor")
            confirmation = input('Type anything if sensor is removed: ')
            
            while True:
                if confirmation != None:
                    self.zeroing()
                    break
                confirmation = input('Type anything if sensor is removed: ')
                time.sleep(0.5)
                
            print("Replace Sensor")
            confirmation = input('Type anything if sensor is replaced: ')
            
            while True:
                if confirmation != None:
                    print("replaced, proceeding")
                    break
                confirmation = input('Type anything if sensor is removed: ')
                time.sleep(0.5)
            
            print("Setup finished")
            pprint.pprint(eeprom)
            
            # self.gas.set_continous_mode()
            self.gas.set_continous_mode()
            time.sleep(1)
            i = 0
            print("Post Calibration")
            while (i < 15):
                i += 1
                self.gas.get_sensor_data()
                conc = self.gas.get_conc_ppm()
                temp = self.gas.get_temp()
                rh = self.gas.get_rh()
                print(f"concentration : {conc} temp : {temp} rh : {rh}")
                time.sleep(1)
        
            self.gas.stop_continuous_data_flow()
            time.sleep(5)
            
            self.sleep()
            time.sleep(1)
            self.close_serial()
            
        except KeyboardInterrupt:
            print('Interrupted')
            self.sleep()
            self.close_serial()

if __name__ == '__main__':
    
        SO2 = Setup("120120020411 110601 SO2 2012 32.21", "/dev/ttyUSB1")
        SO2.main()
        
        
        
        
        