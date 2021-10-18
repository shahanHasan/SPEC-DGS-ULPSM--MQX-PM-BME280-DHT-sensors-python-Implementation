#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  6 21:43:50 2021

@author: shahan
"""
from DGS import DGS
import time

def main():
    try:
        SO2 = DGS('/dev/ttyUSB0', 9600, 1)
        SO2.sensor_wake()
        SO2.EEPROM()
        # gas = SO2.get_gas_name()
        # print(f"gas : {gas}")
        # SO2.get_firmware_readout()
        # SO2.getLMP()
        # r1, r2, r3 = SO2.get_registor_values()
        # if(r1 != 0 and r2 != 0 and r3 != 0):
        #     print(f"{r1} {r2} {r3}")
        #     #CO.set_LMP(r1,r2,r3)
        # #CO.getLMP()
        time.sleep(1)
        SO2.set_continous_mode()
        i = 0
        while (i < 30):
            i += 1
            SO2.get_sensor_data()
            conc = SO2.get_conc_ppm()
            temp = SO2.get_temp()
            rh = SO2.get_rh()
            if conc is not None and temp is not None or rh is not None:
                print(f"concentration : {conc} temp : {temp} rh : {rh}")
                time.sleep(1)
            
        
        
        
        SO2.stop_continuous_data_flow()
        SO2.sensor_sleep()
        SO2.close_serial()
                
    except KeyboardInterrupt:
        print('Interrupted')
        SO2.sensor_sleep()
        SO2.close_serial()
        
if __name__ == "__main__": 
    
    main()