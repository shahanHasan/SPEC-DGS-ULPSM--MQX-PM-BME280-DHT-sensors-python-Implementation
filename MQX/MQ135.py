#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Tue Sep 29 17:41:16 2020."""
from __future__ import division
from MQUnifiedSensor import MQUnifiedSensor
import math , time


class MQ135():
    """
    
    A class used to represent MQ-135 sensor.

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
    GAS      | a      | b
    CO       | 605.18 | -3.937  
    Alcohol  | 77.255 | -3.18 
    CO2      | 110.47 | -2.862
    Tolueno  | 44.947 | -3.445
    NH4      | 102.2  | -2.473
    Acetona  | 34.668 | -3.369
  
    """
    
    ######################### Hardware Related Macros #########################
    MQ135 = MQUnifiedSensor("Arduino", 5, 1, 2, "MQ135")
    MQ135.setRegressionMethod(1)
    RatioMQ135CleanAir = 3.6
    ######################### Software Related Macros #########################
    CALIBARAION_SAMPLE_TIMES     = 10       # define how many samples you are going to take in the calibration phase
    CALIBRATION_SAMPLE_INTERVAL  = 100      # define the time interval(in milisecond) between each samples in the
                                            # cablibration phase
    
    ######################### Application Related Macros ######################
    __NH4                      = "NH4"
    __CO2                      = "CO2"
    __C0                       = "C0"
    __ALCOHOL                  = "ALCOHOL"
    __ACETONA                  = "ACETONA"
    __TOLUENO                  = "TOLUENO"
                                            
    def __init__(self, gasType):
        # Curve is a list where index 0 is slope and 1 is intercept i.e A/M and B
        # curve = [A , B]
        self.NH4curve     = [102.2  , -2.473]
        self.CO2curve     = [110.47 , -2.862]
        self.COcurve      = [605.18 , -3.937]
        self.ALCOHOLcurve = [77.255 , -3.18]
        self.ACETONAcurve = [34.668 , -3.369]
        self.TOLUENOcurve = [44.947 , -3.445]
        self.__gas = gasType
        
        #self.GasTypeCheckAndSetA_B(gasType)
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
        if(self.__NH4 == gasType):
            self.set_A_B(self.NH4curve[0], self.NH4curve[1])
        elif(self.__CO2 == gasType):
            self.set_A_B(self.CO2curve[0], self.CO2curve[1])
        elif(self.__C0 == gasType):
            self.set_A_B(self.COcurve[0], self.COcurve[1])
        elif(self.__ALCOHOL == gasType):
            self.set_A_B(self.ALCOHOLcurve[0], self.ALCOHOLcurve[1])
        elif(self.__ACETONA == gasType):
            self.set_A_B(self.ACETONAcurve[0], self.ACETONAcurve[1])
        elif(self.__TOLUENO == gasType):
            self.set_A_B(self.TOLUENOcurve[0], self.TOLUENOcurve[1])
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
        self.MQ135.setA(A)
        self.MQ135.setB(B)
        
    def calibrate(self):
        """
        Calibrate R0.
        
        Methane PPM.

        Returns
        -------
        None.

        """
        print("Calibrating please wait. Gas : {}".format(self.__gas))
        calcR0 = 0
        for _ in range(self.CALIBARAION_SAMPLE_TIMES):
            self.MQ135.update()
            calcR0 += self.MQ135.calibrate(self.RatioMQ135CleanAir)
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL/1000)
        
        self.MQ135.setR0(calcR0/10)
        print("Done!!")
        if(math.isinf(calcR0)):
            print("Warning: Conection issue founded, R0 is infite (Open circuit detected) please check your wiring and supply")
        if(calcR0 == 0):
            print("Warning: Conection issue founded, R0 is zero (Analog pin with short circuit to ground) please check your wiring and supply")
        
        #self.MQ135.serialDebug(True)

    def main(self):
        """
        Void Main function.

        Returns
        -------
        None.

        """
        #self.calibrate()
        #self.set_A_B(605.18, -3.937)# NH4
        while True: 
            self.MQ135.update()
            #print("analog value : {}".format(Analog_value))
            self.MQ135.readSensor()
            self.MQ135.serialDebug()
            #time.sleep(0.1)
            
    def PPM(self):
        """
        Calculate and return Gas PPM  for MQ135 Sensor.

        Returns
        -------
        PPM : TYPE -> Double
            DESCRIPTION. -> Gas Concentration.

        """
        #A, B = 110.47, -2.862
        #self.set_A_B(A, B)
        #self.calibrate()
        self.MQ135.update()
        self.GasTypeCheckAndSetA_B(self.__gas)
        PPM = self.MQ135.readSensor()
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
        if(self.__gas == "NH4"):
            return PPM
        elif(self.__gas == "CO2"):
            PPM += 600
            return PPM


        
            
if __name__ == "__main__":
    #MQ135NH4 = MQ135("NH4")
    MQ135CO2 = MQ135("CO2")
    #MQ135S.calibrate()
    #MQ135CO2.calibrate()
    while True:
        #MQ135NH4.GasTypeCheckAndSetA_B("NH4")
        #PPMNH4 = MQ135NH4.PPM()
        #MQ135CO2.GasTypeCheckAndSetA_B("CO2")
        PPMCO2 = MQ135CO2.PPM()
        print("CO2 : {}".format(PPMCO2))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        