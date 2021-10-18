#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Mon Sep 28 21:59:19 2020."""
from __future__ import division
import math , time 
import pyfirmata


class MQUnifiedSensor(object):
    """
    A class used to represent MQ-X sensors.

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
    Setters : setR0, setRL, setA, setB, setRegressionMethod, 
              setVoltResolution, setADC, serialDebug
    Getters : getA, getB, getR0, getRL, getVoltResolution,
              getRegressionMethod, getVoltage
    User Functions : calibrate, readSensor, validateEquation
    """
    
################## Software Related Macros / Private names #################
    __firstFlag = False
    #__VOLT_RESOLUTION  = 5.0 -> Assign your own
    __RL = 1 # Value in KiloOhms , set based on sensor
    #__ADC_Bit_Resolution = 10 -> Assign your own 
    __regressionMethod = 1 # 1 -> Exponential || 2 -> Linear
    
    __adc, __a, __b, __sensor_volt = 0, 0, 0, 0
    __R0, __RS_air, __ratio, __PPM, __RS_Calc = 0, 0, 0, 0, 0
    
    READ_SAMPLE_INTERVAL         = 200      # define the time interval(in milisecond) between each samples in
    READ_SAMPLE_TIMES            = 5        # define how many samples you are going to take in normal operation 
                                            # normal operation
# =============================================================================
#     __Type : str
#     __BOARD : str
# =============================================================================
    #Arduino set up :
    port = '/dev/ttyACM0'
    board = pyfirmata.Arduino(port)
    it = pyfirmata.util.Iterator(board)
    it.start()
    time.sleep(0.2)
    
    
    def __init__(self, BOARD, Voltage_Resolution, ADC_Bit_Resolution, pin, Type):
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
        self.__VOLT_RESOLUTION = Voltage_Resolution
        self.__ADC_Bit_Resolution = ADC_Bit_Resolution
        self.__Type = Type # E.G : "CUSTOM MQ"
        self.__pin = pin # analog pin , 0 ,1 ,2 ,3 ,4 ...
        # Arduino Setup
        self.analog_input = self.board.get_pin('a:{}:i'.format(self.__pin))
        time.sleep(0.2)
        self.analog_input.enable_reporting()
        time.sleep(0.2)
        
        #Arduino Setup
        #self.analog_input = MQUnifiedSensor.setArduino(self.__pin)
        
    def setA(self, A):
        """
        M/m = [log(y) - log(y0)] / [log(x) - log(x0)].
        
        Parameters
        ----------
        A : TYPE -> int
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.__a = A
    
    def setB(self, B):
        """
        
        B/b = log(y) - m*log(x).

        Parameters
        ----------
        B : TYPE -> Float 
            DESCRIPTION. -> slope of the graph from data Sheet

        Returns
        -------
        None.

        """
        self.__b = B
        
    def setR0(self, R0 = 0):
        """
        
        Resistance for gas in clean air.

        Parameters
        ----------
        R0 : TYPE, optional
            DESCRIPTION. The default is 0.

        Returns
        -------
        None.

        """
        self.__R0 = R0
    
    def setRL(self, RL = 1):
        """
        Resistance between analog output and GND in Voltage divider.

        Parameters
        ----------
        RL : TYPE, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        None.

        """
        self.__RL = RL
        
    def setADC(self, value):#for custom ADC
        """
        If a Custom / Separate ADC is used.

        Parameters
        ----------
        value : TYPE -> float
            DESCRIPTION. -> ADC sensor value/ Output of A0

        Returns
        -------
        None.

        """
        self.__sensor_volt = (value) * self.__VOLT_RESOLUTION / (pow(2,self.__ADC_Bit_Resolution) - 1)
        self.__adc = value


    def setVoltResolution(self, voltage_resolution = 5):
        """
        Use 5 volt sensors, Adjust as needed.

        Parameters
        ----------
        voltage_resolution : TYPE, optional
            DESCRIPTION. The default is 5.

        Returns
        -------
        None.

        """
        self.__VOLT_RESOLUTION = voltage_resolution
        
    
    def setRegressionMethod(self, regression_Method):
        """
        Linear scale or Logarithmic Scale.

        Parameters
        ----------
        regression_Method : TYPE -> Int
            DESCRIPTION. -> if 1 then linear else logarithmic

        Returns
        -------
        None.

        """
        self.__regressionMethod = regression_Method

    def getR0(self):
        """
        Return value of R0.

        Returns
        -------
        TYPE -> float
    

        """
        return self.__R0
    
    def getRL(self):
        """
        Adjust as you used in setRL.

        Returns
        -------
        TYPE -> float
            DESCRIPTION. -> Returns the value of RL the is set

        """
        return self.__RL
    
    def getVoltResolution(self):
        """
        Get voltage resolution.

        Returns
        -------
        TYPE -> float
        DESCRIPTION. -> Voltage of the sensors

        """
        return self.__VOLT_RESOLUTION
    
    def getRegressionMethod(self):# -> str:
        """
        Use of method for regression.

        Returns
        -------
        str
            DESCRIPTION. -> Exponential or Linear/Logarithmic

        """
        return "Exponential" if(self.__regressionMethod == 1) else "Linear"
    
    def getA(self):
        """
        Slope of the Graph in datasheet.

        Returns
        -------
        TYPE -> float
        DESCRIPTION. ->Slope

        """
        return self.__a

    def getB(self):
        """
        Intercept of Y axis.

        Returns
        -------
        TYPE -> float
        DESCRIPTION. -> Intercept

        """
        return self.__b
    
    def serialDebug(self, onSetup = False):
        """
        
        Represent the Class in Strings.
        
        step 1 : Prints the class desc.
        step 2 : The last part
        
        Parameters
        ----------
        onSetup : TYPE, optional
        
        DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """   
        if(onSetup):
            print()
            print("*******************************************************************")
            print("MQ sensor reading library for arduino \n" + 
            "Note: remember that all the parameters below can be modified during the program execution with the methods : \n" + 
            "setR0, setRL, setA, setB where you will have to send as parameter the new value, example: mySensor.setR0(20); //R0 = 20KΩ \n" +
            "Authors: Shahan Hasan \n" +
            "Contributors: ___________________replace with names______________________ \n" + 
            "Sensor : {} \n".format(self.__Type) +
            "Supply voltage: {} VDC \n".format(self.__VOLT_RESOLUTION) +
            "ADC Resolution:  {} Bits \n".format(self.__ADC_Bit_Resolution) +
            "R0: {} KΩ \n".format(self.__R0) +
            "RL: {} KΩ".format(self.__RL))
            
            if(self.__regressionMethod == 1):
                print("Model : Exponential")
            else:
                print("Model : Linear")
            print("MQ-Type : " + self.__Type + "\n" +
            "Slope of the graph :       __a {} \n".format(self.__a) +
            "Y intercept of the graph : __b {} \n".format(self.__b) +
            "Development board: " + self.__BOARD) 
        
        else:
            if not self.__firstFlag: # Header
                print("| ******************** " + self.__Type + "********************* | \n" +
                "| ADC_In | Equation_V_ADC | Voltage_ADC |        Equation_RS        |  Resistance_RS  |    EQ_Ratio  |     Ratio (RS/R0)   |       Equation_PPM        |     PPM    |")
                self.__firstFlag = True
                
            else:
                
                print(" | {}".format(self.__adc) + " | v = ADC * {}/{}".format(self.__VOLT_RESOLUTION,(pow(2, self.__ADC_Bit_Resolution) - 1)) +
                " | {}".format(self.__sensor_volt) + "  | RS = (( {} *RL)/Voltage) - RL|    {}".format(self.__VOLT_RESOLUTION,self.__RS_Calc)  +
                "     | Ratio = RS/R0|    {}       |   ".format(self.__ratio) +
                "ratio*a + b  |   {}   |".format(self.__PPM) if(self.__regressionMethod == 1) else "pow(10, (log10(ratio)-b)/a)  |   {}   |".format(self.__PPM))
    
    
    def update(self):
        """
        Get current value of the sensor.

        Returns
        -------
        None.

        """
        self.__sensor_volt = self.getVoltage()
        #print("sensor_volt : {}".format(self.__sensor_volt))
    
    def getVoltage(self, read = True):# -> float:
        """
        Low level implementation of reading sensor data.

        Parameters
        ----------
        read : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        float
            DESCRIPTION. -> return sensor voltage / A0 in volts 

        """
        sensor_voltage = 0
        
        if(read):
            avg_voltage = 0
            #count = 0
            for _ in range(self.READ_SAMPLE_TIMES):
                self.__adc = self.getanalogvoltage()
                #time.sleep(0.2)
                #if(self.__adc != None): # Pyfirmata None input check
                avg_voltage = avg_voltage + self.__adc
                time.sleep(self.READ_SAMPLE_INTERVAL/1000)
                #count += 1
                #else:
                #    pass
                
            sensor_voltage = ((avg_voltage / self.READ_SAMPLE_TIMES) * self.__VOLT_RESOLUTION) / ((math.pow(2, self.__ADC_Bit_Resolution)) - 1)
        
        else:
            sensor_voltage = self.__sensor_volt
        
        return sensor_voltage
         

    def getanalogvoltage(self):
        """
        Read voltage data raw.

        Returns
        -------
        TYPE -> analog voltage.
            DESCRIPTION.

        """
        adc_volt = self.analog_input.read()
        if adc_volt is not None:
            return adc_volt
        else:
            return self.getanalogvoltage()
        
    #@classmethod
    def setArduino(self, pin):# -> object:
        """
        Set up arduino with python.

        Parameters
        ----------
        cls : TYPE -> self
            DESCRIPTION.
        pin : TYPE -> Arduino pin
            DESCRIPTION.

        Returns
        -------
        object -> analog_input
        DESCRIPTION.

        """   
        port = '/dev/ttyACM0'
        board = pyfirmata.Arduino(port)
        it = pyfirmata.util.Iterator(board)
        it.start()
        
        analog_input = board.get_pin('a:{}:i'.format(pin))
        return analog_input
    
    
    def calibrate(self, ratioInCleanAir):# -> float:
        """
        More explained in: https://jayconsystems.com/blog/understanding-a-gas-sensor.
        
        V = I x R 
        VRL = [VC / (RS + RL)] x RL 
        VRL = (VC x RL) / (RS + RL) 
        Así que ahora resolvemos para RS: 
        VRL x (RS + RL) = VC x RL
        (VRL x RS) + (VRL x RL) = VC x RL 
        (VRL x RS) = (VC x RL) - (VRL x RL)
        RS = [(VC x RL) - (VRL x RL)] / VRL
        RS = [(VC x RL) / VRL] - RL
        
        TODO : 
        1. When getting the R0 value, do it in a clean environment where no other gases are present.

        2. The datasheet recommends to calculate R0 in an environment that has 10000 
        ppm of methane. If you can simulate such environment, calculate R0 under these conditions.

        Parameters
        ----------
        ratioInCleanAir : TYPE -> Float
            DESCRIPTION. -> Ration i.e R0/RS in Clean Air from Graph

        Returns
        -------
        float
            DESCRIPTION. -> Returns R0

        """
        # Define variable for sensor resistance
        RS_air = ((self.__VOLT_RESOLUTION * self.__RL ) / self.__sensor_volt ) - self.__RL
        if(RS_air < 0):# No negative values accepted
            RS_air = 0 
        R0 = RS_air/ratioInCleanAir # Calculate R0 
        if(R0 < 0):# No negative values accepted  
            R0 = 0
        return R0 
    
    def readSensor(self):# -> float:
        """
        
        Convert sensor volt to gas concentration in PPM.

        Returns
        -------
        float
            DESCRIPTION.

        """
        self.__RS_Calc = ((self.__VOLT_RESOLUTION * self.__RL ) / self.__sensor_volt ) - self.__RL
        
        if(self.__RS_Calc < 0):  
            self.__RS_Calc = 0

        self.__ratio = self.__RS_Calc / self.__R0
        
        if(self.__ratio <= 0): 
            self.__ratio = 0
            
        if(self.__regressionMethod == 1): 
            self.__PPM = self.__a * math.pow( self.__ratio , self.__b )
   
        else:
            ppm_log = (math.log10( self.__ratio ) - self.__b ) / self.__a
            self.__PPM = math.pow(10, ppm_log)
            
        if( self.__PPM < 0):  
            self.__PPM = 0
            
        return self.__PPM
    
    def validateEquation(self, ratioInput):# -> float:
        """
        Validate Equation for testing.

        Parameters
        ----------
        ratioInput : TYPE -> float
        DESCRIPTION. -> R0/Rs

        Returns
        -------
        float 
        DESCRIPTION. -> PPM , gas concentration

        """ 
        if(self.__regressionMethod == 1): 
            self.__PPM = self.__a * pow( ratioInput , self.__b )
        else:
            ppm_log = (math.log10( ratioInput ) - self.__b ) / self.__a
            self.__PPM = pow(10, ppm_log)
        
        return self.__PPM
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    















        