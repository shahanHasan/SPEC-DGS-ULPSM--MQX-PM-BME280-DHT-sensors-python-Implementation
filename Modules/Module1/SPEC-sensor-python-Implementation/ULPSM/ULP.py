#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 15:09:08 2021

@author: shahan
"""
from __future__ import division
import pyfirmata
import serial
import time, math


class ULP(object):
    #Arduino set up :
    port = '/dev/ttyACM0'
    board = pyfirmata.Arduino(port)
    it = pyfirmata.util.Iterator(board)
    it.start()
    time.sleep(0.2)
    
    ############### Software Macros ##############
    
    ## Temperature sensor settings ##
    
    ## temps for cal of temp sensor
    ## volts for cal of temp sensor
    ## volts for cal of temp sensor
    pHtemp , pLtemp , pHvolt , pLvolt = 0,0,0,0
    pTb , pTs = 0, 0
    
    
    ## Gas concentration settings ##
    
    ## initializers for sensor, sensor sensitivity factor
    ## analog read reference voltage, usually 5 V for Uno
    ## voltage supplied to ULP, !!!! max 3.3 V !!!!
    ## initially set to pVref, then reset to include V of open circuit voltage during OCzero()
    ## divider, this is set ideally voltage with no current through circuit (electronic zero)
    ## the last calculated value of current for the sensor
    ## the last measured value of voltage for the sensor
    ## the last calculated value of temperature in degrees C
    ## the last calculated value of concentration in ppb
    pSf , pVcc , pVsup , pVref_set = 0, 3.3, 3.3, 0
    pVref , pInA , pT , pX = 0,0,0,0
    
    ## temperature correction coefficient ##
    pTc = 0     ## sensitivity coeficient
    pn = 0      ## exponential correction to baseline
    pIzero = 0  ## exponential coeficeient to correction to baseline reset during zero()
    pTzero = 0  ## exponential zero temperature factor
    
    pGain = 0   ## gain of trans impedance amplifier (TIA)
    
    
    
    def __init__(self, BOARD, pin_c, pin_t, Type, sf):
        """
        Initialize / Constructor.

        Parameters
        ----------
        BOARD : TYPE -> str
        Voltage_Resolution : TYPE -> int
        ADC_Bit_Resolution : TYPE -> int
        pin : TYPE -> int
        Type : TYPE -> str

        Returns
        -------
        None.

        """
        self. __BOARD = BOARD # E.G : "Arduino"
        self.__Type = Type # E.G : "CUSTOM MQ"
        self.__pin_c = pin_c # analog pin , 0 ,1 ,2 ,3 ,4 ...]
        self.__pin_t = pin_t 
        # Arduino Setup
        self.analog_input_c = self.board.get_pin('a:{}:i'.format(self.__pin_c))
        time.sleep(0.2)
        self.analog_input_t = self.board.get_pin('a:{}:i'.format(self.__pin_t))
        time.sleep(0.2)
        self.analog_input_c.enable_reporting()
        time.sleep(0.2)
        self.analog_input_t.enable_reporting()
        time.sleep(0.2)
        
        self.pTzero = 20.0;
        self.pIzero = 0.0;
  
        ## Temperature Sensor Settings
        self.pHtemp = 40.0;
        self.pLtemp = 20.0; ## temps for cal of temp sensor
        self.pTb = 18.0;     ## temperature sensor coef
        self.pTs = 87.0;     ## temperature sensor coef
        self.pHvolt = (self.pHtemp + self.pTb) * self.pVsup / self.pTs  ## volts for cal of temp sensor
        self.pLvolt = (self.pLtemp + self.pTb) * self.pVsup / self.pTs ## volts for cal of temp sensor
        self.pSf = sf
        
        #Arduino Setup
        #self.analog_input = ULP.setArduino(self.__pin)
    
    def voltage(self, value):#for custom ADC
        #linear mapping of 0 to 1 analog read to 0 to 3.3 sensor voltage
        volt = (value) * self.pVcc / (pow(2,1) - 1)
        return volt
    
    def getTemp(self, n=10):
        Sampling_times, i, anaCounts = 300, 0, 0
        
        while (i <= Sampling_times):
            anaCounts += self.analog_input_t.read()
            time.sleep(0.001)
            i += 1
        ave = anaCounts / i
        Cnts = round(ave, 2)
        #Volts = Cnts * self.pVcc / (pow(2,1) - 1)
        Volts = self.voltage(Cnts)
        
        self.pT = (self.pTs/ self.pVsup) * Volts - self.pTb
        
        #return pT

    
    def convertT(self, U = 'B'):
        if (U == "F"):
            Temp_f = (self.pT * (9 / 5) ) + 32
            return Temp_f
        elif(U == "C"):
            return self.pT
        else:
            return 0
        
    def convertX(self, U):
        if(U=='B'):
            return self.pX
        elif (U=='M'):
            return self.pX/1000.0
        else:
            return 0
    
    def setTSpan(self, t, R):
        print(f"Old temp. span and offset: {self.pTs}  ,  {self.pTb}")
        
        Sampling_times, i, anaCounts = 300, 0, 0
        
        while (i <= Sampling_times):
            anaCounts += self.analog_input_t.read()
            time.sleep(0.001)
            i += 1
        ave = anaCounts / i
        Cnts = round(ave, 2)
        #Volts = Cnts * self.pVcc / (pow(2,1) - 1)
        Volts = self.voltage(Cnts)
        
        if(R == "HIGH"):
            self.pHtemp = t
            self.pHvolt = Volts
        else:
            self.pLtemp = t
            self.pLvolt = Volts
            
        self.pTs = self.pVsup * (self.pHtemp - self.pLtemp) / (self.pHvolt - self.pLvolt)
        self.pTb = self.pLvolt * (self.pHtemp - self.pLtemp) / (self.pHvolt - self.pLvolt) - self.pLtemp;
        
        print(f"New temp. span and offset: {self.pTs}  ,  {self.pTb}")
        
        
    def setVref(self, b, R2):
        if (b >= 0):
            self.pVref = self.pVsup * (R2 + 1000000) / (R2 + 2000000) * 1000.0
        else:
            self.pVref = self.pVsup * (1000000) / (R2 + 2000000) * 1000.0
        
        self.pVref_set = self.pVref
      
    def OCzero(self, n =10):
        
        print("Zeroing and Calibration. ")
        # confirmation = input('Type anything after sensor is removed: ')
        
        Sampling_times, i, anaCounts = 300, 0, 0
        
        while (i <= Sampling_times):
            anaCounts += self.analog_input_c.read()
            time.sleep(0.001)
            i += 1
            
        average = anaCounts / i
        Cnts = round(average, 2)
        print(f"i : {i} analog sum : {anaCounts} average : {Cnts}")
        self.pVref_set = Cnts * self.pVcc * 1000.0 / (pow(2,1) - 1)  ##in mV
        
        print(f"pVref_set  : {self.pVref_set}")
        print(f"difference : {abs(self.pVref - self.pVref_set)}")
        
        if (abs(self.pVref - self.pVref_set) > 50):
            return False
        else:
            return True
        
    def zero(self):
        self.pIzero = self.pInA
        self.pTzero = self.pT
    
    def getIgas(self,n=10):
        
        Sampling_times, i, anaCounts = 300, 0, 0
        
        while (i <= Sampling_times):
            anaCounts += self.analog_input_c.read()
            time.sleep(0.001)
            i += 1
        ave = anaCounts / i
        Cnts = round(ave, 2)
        self.pVgas = Cnts * self.pVcc * 1000.0 / (pow(2,1) - 1) ##in mV
        self.pInA = (self.pVgas-self.pVref_set)/self.pGain * 1000.0 
        
    def getConc(self, t = 20.00):
        
        nA = self.pInA - self.pIzero * self.expI(t-self.pTzero)
        Sens = self.pSf * (1.0 + self.pTc * (t - 20.0))
        self.pX = nA / Sens *1000.0
    
    def expI(self, T):
        return math.exp(T/self.pn)
        
    
    def setXSpan(self):
        time.sleep(10)
        X, nA, Sf = 0, 0, 0
        print("When gas concentration steady, enter Concentration in ppm followed by 'cr' = ")
        X = 10 #random placeholder for Serial.parseFloat() function
        
        self.getIgas(10)
        Sf = self.pInA / X
        #if(abs(Sf - self.pSf) * 2 / (Sf + self.pSf) < 0.1):
        if(X < 10):
            self.pSf = Sf
        else:
            print("Error setting span")
        
        
    def read_c(self):
        
        return self.analog_input_c.read()
        
        
    def read_t(self):
        
        return self.analog_input_t.read()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


        