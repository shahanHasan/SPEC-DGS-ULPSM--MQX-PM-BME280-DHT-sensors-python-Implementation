#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Tue Sep 29 17:41:16 2020."""
from __future__ import division
from MQUnifiedSensor import MQUnifiedSensor
import math , time 


class MQ131():
    """
    
    A class used to represent MQ-131 sensor.

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
  
    Exponential regression:
    GAS     | a/m - slope |  b - intercept
    NOx     | -462.43     | -2.204
    CL2     | 47.209      | -1.186
    O3      | 23.943      | -1.11
  
    """
    
    ######################### Hardware Related Macros #########################
    MQ131 = MQUnifiedSensor("Arduino", 5, 1, 0, "MQ131")
    RatioMQ131CleanAir = 15
    MQ131.setRegressionMethod(1)
    
    
    ######################### Software Related Macros #########################
    CALIBARAION_SAMPLE_TIMES     = 10       # define how many samples you are going to take in the calibration phase
    CALIBRATION_SAMPLE_INTERVAL  = 100      # define the time interval(in milisecond) between each samples in the
                                            # cablibration phase
                                            
    ######################### Application Related Macros ######################
    __NOX                      = "NOX"
    __CL2                      = "CL2"
    __O3                       = "O3"
    
    def __init__(self, gasType):
        # Curve is a list where index 0 is slope and 1 is intercept i.e A/M and B
        # curve = [A , B]
        self.NOXcurve = [-462.43, -2.204]
        self.CL2curve = [47.209, -1.186]
        self.O3curve  = [23.943, -1.11]
  
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
        if(self.__NOX == gasType):
            self.set_A_B(self.NOXcurve[0], self.NOXcurve[1])
        elif(self.__CL2 == gasType):
            self.set_A_B(self.CL2curve[0], self.CL2curve[1])
        elif(self.__O3 == gasType):
            self.set_A_B(self.O3curve[0], self.O3curve[1])
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
        self.MQ131.setA(A)
        self.MQ131.setB(B)
        
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
            self.MQ131.update()
            calcR0 += self.MQ131.calibrate(self.RatioMQ131CleanAir)
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL/1000)
        
        self.MQ131.setR0(calcR0/10)
        print("Done!!")
        if(math.isinf(calcR0)):
            print("Warning: Conection issue founded, R0 is infite (Open circuit detected) please check your wiring and supply")
        if(calcR0 == 0):
            print("Warning: Conection issue founded, R0 is zero (Analog pin with short circuit to ground) please check your wiring and supply")
        
        #self.MQ131.serialDebug(True)

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
            self.MQ131.update()
            #print("analog value : {}".format(Analog_value))
            self.MQ131.readSensor()
            self.MQ131.serialDebug()
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
        self.MQ131.update()
        PPM = self.MQ131.readSensor()
        return PPM
    
    def CorrectedPPM(self):
        """
        Adjust Concentration.

        Parameters
        ----------
        PPM : TYPE -> Float
            DESCRIPTION. -> Concentration

        Returns
        -------
        PPM : TYPE -> FLoat
            DESCRIPTION. -> Adjusted Concentration

        """
        PPM = self.PPM()
        PPM /= 100
        return PPM
            
        
        
            
if __name__ == "__main__":
    MQ131S = MQ131("O3")
    #MQ4.calibrate()
    MQ131S.main()