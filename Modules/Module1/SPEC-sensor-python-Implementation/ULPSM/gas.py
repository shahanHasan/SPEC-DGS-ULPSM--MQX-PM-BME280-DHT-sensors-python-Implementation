#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 17:15:51 2021

@author: shahan
"""
from .ULP import ULP
import math , time


class H2S_gas():
    
    sf = 180.43
    H2S = ULP("Arduino", 1, 2, "Analog", sf)
    H2S.setVref(+3, 2000)
    H2S.pGain = 49.9
    H2S.pn = -300.0
    H2S.pTc = 0.007
    
    def setup_for_continuous_data(self):
        self.H2S.pVcc = 3.33
        self.H2S.pVsup = 3.33
        #self.H2S.pVref_set = 1665.0
        self.H2S.pVref_set = 1598.4
    
    def getData(self):
        self.H2S.getIgas()
        self.H2S.getTemp()
        self.H2S.getConc(self.H2S.pT)
        temp = self.H2S.convertT('C')
        conc = self.H2S.convertX('M')
        return conc, temp
        
    def zero(self):
        print("Zeroing")
        self.H2S.zero()
        print(f"Izero : {self.H2S.pIzero} and Tzero: {self.H2S.pTzero}")
    
    def setup(self):
        
        self.H2S.pVcc = 3.33
        self.H2S.pVsup = 3.33
        ## self.H2S.pVref_set = 1641.33 , 1621.89
        #serial.flush()
        print("setting up")
        print(f"Vsup , Vcc, Vref : {self.H2S.pVsup}  {self.H2S.pVcc}  {self.H2S.pVref}")
        
        print("Remove Sensor")
        confirmation = input('Type anything if sensor is removed: ')
        if (confirmation != None):
            if(self.H2S.OCzero()):
                print(f"Vref new = {self.H2S.pVref_set}")
            else:
                print("Recheck Settings, Zero out of range")
                while(1):
                    print(self.H2S.read_c())
                    time.sleep(2)
        print("Finished Setting Up, Replace Sensor Now.")
        confirmation = input('Type anything after sensor is replaced: ')
        if (confirmation != ""):
            print("Ready for data")
            print()
            print("T1, mV, nA, C1")
            i = 0
            while True:      
                conc, temp = self.getData()
                print(f"{temp} {self.H2S.pVgas} {self.H2S.pInA} {conc}")
                
                if(conc < 0):
                    i += 1
                    if(i > 50):
                        self.zero()
                time.sleep(5)
        else:
            print("error")
            return 0
                   
        
class NO2_gas():
    
    sf = -16.43
    NO2 = ULP("Arduino", 3, 4, "Analog", sf)
    NO2.setVref(-25, 16200)
    NO2.pGain = 499.0
    NO2.pn = 109.6
    NO2.pTc = 0.005
       
    def setup_for_continuous_data(self):
        self.NO2.pVcc = 3.33
        self.NO2.pVsup = 3.33
        #self.NO2.pVref_set = 1631.6999999999998
        self.NO2.pVref_set = 1631.6999999999998
    
    def getData(self):
        self.NO2.getIgas()
        self.NO2.getTemp()
        self.NO2.getConc(self.NO2.pT)
        temp = self.NO2.convertT('C')
        conc = self.NO2.convertX('M')
        return conc, temp
        
    def zero(self):
        print("Zeroing")
        self.NO2.zero()
        print(f"Izero : {self.NO2.pIzero} and Tzero: {self.NO2.pTzero}")
    
    def setup(self):
        
        self.NO2.pVcc = 3.33
        self.NO2.pVsup = 3.33
        ## self.H2S.pVref_set = 1641.33 , 1621.89
        #serial.flush()
        print("setting up")
        print(f"Vsup , Vcc, Vref : {self.NO2.pVsup}  {self.NO2.pVcc}  {self.NO2.pVref}")
        
        print("Remove Sensor")
        confirmation = input('Type anything if sensor is removed: ')
        if (confirmation != None):
            if(self.NO2.OCzero()):
                print(f"Vref new = {self.NO2.pVref_set}")
            else:
                print("Recheck Settings, Zero out of range")
                while(1):
                    print(self.NO2.read_c())
                    time.sleep(2)
        print("Finished Setting Up, Replace Sensor Now.")
        confirmation = input('Type anything after sensor is replaced: ')
        if (confirmation != ""):
            print("Ready for data")
            print()
            print("T1, mV, nA, C1")
            i = 0
            while True:      
                conc, temp = self.getData()
                print(f"{temp} {self.NO2.pVgas} {self.NO2.pInA} {conc}")
                
                if(conc < 0):
                    i += 1
                    if(i > 50):
                        self.zero()
                time.sleep(5)
        else:
            print("error")
            return 0
        
if __name__ == '__main__':
    
    
    try:
        
        #H2S = H2S_gas()
        #H2S.setup_for_continuous_data()
        
        #NO2 = NO2_gas()
        #NO2.setup_for_continuous_data()
        
        #while True:
        #    conc_H2S, temp_H2S = H2S.getData()
        #    conc_NO2, temp_NO2 = NO2.getData()
        #    if not [x for x in (conc_H2S, temp_H2S, conc_NO2, temp_NO2) if x is None]:
        #        print(f"H2S concentration (PPM): {conc_H2S} temperature (C) {temp_H2S} NO2 concentration (PPM) {conc_NO2} temperature (C) {temp_NO2}")
        
        
        #NO2 = NO2_gas()
        #NO2.setup()
        
        H2S = H2S_gas()
        H2S.setup()
        
    except KeyboardInterrupt:
            print('Exitting')
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        