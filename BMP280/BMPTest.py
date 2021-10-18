#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 16:28:17 2020.

@author: shahan
"""

import bme280
import time

class BMS(object):
    """BMS temp , pressure and humidity."""
    
    def Chip_version(self):
        """
        Chip_version.

        Returns
        -------
        None.

        """
        (chip_id, chip_version) = bme280.readBME280ID()
        print("Chip ID : {}").format(chip_id)
        print("Version : {}").format(chip_version)
      
    def read_value(self):
        """
        Read and print value.

        Returns
        -------
        None.

        """
        (temperature,pressure,humidity) = bme280.readBME280All()
        #print("Temperature : {} C").format(temperature)
        #print("Pressure : {} hPa").format(pressure)
        #print("Humidity : {} %").format(humidity)
        print("Temperature : {} C , Pressure : {} hPa , Humidity : {} %").format(temperature,pressure,humidity)
        
    
    def readFunc(self):
        """
        Read Sensor data.

        Returns
        -------
        temperature : TYPE -> Float
            DESCRIPTION.
        pressure : TYPE -> Float
            DESCRIPTION.
        humidity : TYPE -> Float
            DESCRIPTION.

        """
        (temperature,pressure,humidity) = bme280.readBME280All()
        #print("Temperature : {} C").format(temperature)
        #print("Pressure : {} hPa").format(pressure)
        #print("Humidity : {} %").format(humidity)
        #print("Temperature : {} C , Pressure : {} hPa , Humidity : {} %").format(temperature,pressure,humidity)
        return temperature,pressure,humidity
    
    def celsiusToFahrenheit(self, celsius):
        """
        Convert data.

        Parameters
        ----------
        celsius : TYPE
            DESCRIPTION.

        Returns
        -------
        fahrenheit : TYPE -> Float
            DESCRIPTION.

        """
        fahrenheit = (celsius * 9/5) + 32
        return fahrenheit
    
    def reading(self):
        """
        Read Value.

        Returns
        -------
        None.

        """
        self.Chip_version()
        while True:
            self.read_value()
            time.sleep(5)
    
if (__name__ == "__main__"):
    obj1 = BMS()
    obj1.reading()
    
