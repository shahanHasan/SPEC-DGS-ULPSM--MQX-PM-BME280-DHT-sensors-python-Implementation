#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Tue Sep 29 17:41:16 2020."""
from __future__ import division
from MQUnifiedSensor import MQUnifiedSensor
import math , time 


class MQ4():
    """
    
    A class used to represent MQ-4 sensor.

    Attributes
    ----------
    BOARD : TYPE -> str 
        A formatted string to print out the name of the Board i.e Arduino 
    Voltage_Resolution : TYPE -> int
        The voltage resolution of the sensors
    ADC_Bit_Resolution : TYPE -> int
        Analog to Digital bit resolution
    pin : TYPE -> int
        Analog pin on ADC or Arduino
    Type : TYPE -> str
        A formatted string to print out the type of sensor i.e MQ-4 

    Methods
    -------
    Setters : From MQUnified
    Getters : From MQUnified , PPM
    User Functions : calibrate, Main, PPM
    Exponential regression:
  
    Gas    | a      | b
    LPG    | 3811.9 | -3.113
    CH4    | 1012.7 | -2.786
    CO     | 200000000000000 | -19.05
    Alcohol| 60000000000 | -14.01
    smoke  | 30000000 | -8.308
  
    """
    
    ######################### Hardware Related Macros #########################
    MQ4 = MQUnifiedSensor("Arduino", 5, 1, 3, "MQ4")
    RatioMQ4CleanAir = 4.4
    MQ4.setRegressionMethod(1)
    
    
    ######################### Software Related Macros #########################
    CALIBARAION_SAMPLE_TIMES     = 10       # define how many samples you are going to take in the calibration phase
    CALIBRATION_SAMPLE_INTERVAL  = 100      # define the time interval(in milisecond) between each samples in the
                                            # cablibration phase
                                            
    ######################### Application Related Macros ######################
    __CH4                      = "CH4"
    __CO                       = "CO"
    __LPG                      = "LPG"
    __ALCOHOL                  = "ALCOHOL"
    __SMOKE                    = "SMOKE"
    
    def __init__(self, gasType):
        # Curve is a list where index 0 is slope and 1 is intercept i.e A/M and B
        # curve = [A , B]
        self.CH4curve = [1012.7 , -2.786]
        self.COcurve = [200000000000000 , -19.05]
        self.LPGcurve = [3811.9 , -3.113]
        self.ALCOHOLcurve = [60000000000 , -14.01]
        self.SMOKEcurve = [30000000 , -8.308]
        
        self.GasTypeCheckAndSetA_B(gasType)
        self.calibrate()
        
    def GasTypeCheckAndSetA_B(self,gasType):
        """
        Check Gas type and set corresponding A and B.

        Parameters
        ----------
        gasType : TYPE -> Str
            DESCRIPTION. -> Name of Gas to be Measure

        Raises
        ------
        TypeError -> Str
            DESCRIPTION. -> Incorrect Gas

        Returns
        -------
        None.

        """
        if(self.__CH4 == gasType):
            self.set_A_B(self.CH4curve[0], self.CH4curve[1])
        elif(self.__CO == gasType):
            self.set_A_B(self.COcurve[0], self.COcurve[1])
        elif(self.__LPG == gasType):
            self.set_A_B(self.LPGcurve[0], self.LPGcurve[1])
        elif(self.__ALCOHOL == gasType):
            self.set_A_B(self.ALCOHOLcurve[0], self.ALCOHOLcurve[1])
        elif(self.__SMOKE == gasType):
            self.set_A_B(self.SMOKEcurve[0], self.SMOKEcurve[1])
        else:
            raise TypeError("Only Valid gas types are allowed")
        
    def set_A_B(self,A,B):
        """
        Set A/M and B for different gas concentration.

        Parameters
        ----------
        A : TYPE -> float
            DESCRIPTION. -> Slope
        B : TYPE -> float
            DESCRIPTION. -> Intercept of y axis

        Returns
        -------
        None.

        """
        self.MQ4.setA(A)
        self.MQ4.setB(B)
        
    def calibrate(self):
        """
        Calibrate R0.
        
        Methane PPM.

        Returns
        -------
        None.

        """
        print("Calibrating please wait.")
        calcR0 = 0
        for _ in range(self.CALIBARAION_SAMPLE_TIMES):
            self.MQ4.update()
            calcR0 += self.MQ4.calibrate(self.RatioMQ4CleanAir)
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL/1000)
        
        self.MQ4.setR0(calcR0/10)
        print("Done!!")
        if(math.isinf(calcR0)):
            print("Warning: Conection issue founded, R0 is infite (Open circuit detected) please check your wiring and supply")
        if(calcR0 == 0):
            print("Warning: Conection issue founded, R0 is zero (Analog pin with short circuit to ground) please check your wiring and supply")
        
        #self.MQ4.serialDebug(True)

    def main(self):
        """
        Void Main function.

        Returns
        -------
        None.

        """
        #self.set_A_B(self.CH4curve[0], self.CH4curve[1])# 
        #self.calibrate()
        while True: 
            self.MQ4.update()
            #print("analog value : {}".format(Analog_value))
            self.MQ4.readSensor()
            self.MQ4.serialDebug()
            #time.sleep(0.1)
        
    def PPM(self):
        """
        Calculate and return PPM  foro MQ4 Sensor.

        Returns
        -------
        PPM : TYPE -> Double
            DESCRIPTION. -> Gas Concentration.

        """
        #self.set_A_B(self.CH4curve[0], self.CH4curve[1])
        #self.calibrate()
        self.MQ4.update()
        PPM = self.MQ4.readSensor()
        return PPM
        
        
            
if __name__ == "__main__":
    MQ4S = MQ4("CH4")
    #MQ4.calibrate()
    MQ4S.main()
    