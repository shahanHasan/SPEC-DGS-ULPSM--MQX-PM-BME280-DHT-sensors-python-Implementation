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
        CO = DGS('/dev/ttyUSB1', 9600, 1)
        CO.sensor_wake()
        CO.EEPROM()
        # gas = CO.get_gas_name()
        # print(f"gas : {gas}")
        # CO.get_firmware_readout()
        # CO.getLMP()
        # r1, r2, r3 = CO.get_registor_values()
        # if(r1 != 0 and r2 != 0 and r3 != 0):
        #     print(f"{r1} {r2} {r3}")
        #     CO.set_LMP(r1,r2,r3)
        # CO.getLMP()
        # CO.EEPROM()
        # time.sleep(5)
        
        # print()
        # print("Sensor Stabilized.")
        
        # bool_val = CO.zero_calibration()
        # if(bool_val):
        #     print("Finished setting zero.")
        #     print("Finished Setup")
        # else:
        #     print("Retry, calibration failed")
        
        # print("Setup finished")
        #time.sleep(1)
        
        #CO.set_continous_mode()
        # CO.set_continous_mode()
        #i = 0
        #while (i < 70):
        #    i += 1
        #    CO.get_sensor_data()
        #    conc = CO.get_conc_ppm()
        #    temp = CO.get_temp()
        #    rh = CO.get_rh()
        #    if conc is not None and temp is not None or rh is not None:
        #        print(f"concentration : {conc} temp : {temp} rh : {rh}")
        #        time.sleep(1)
            
        #CO.stop_continuous_data_flow()
        CO.sensor_sleep()
        CO.close_serial()
                
    except KeyboardInterrupt:
        print('Interrupted')
        CO.sensor_sleep()
        CO.close_serial()
        
if __name__ == "__main__": 
    
    main()
