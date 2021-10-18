#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Sat Oct  3 16:57:24 2020."""

import CSVTest
import ThinkSpeakTest
import time , sys , os , csv
from PMSensor.pmsensor import PMS
from BMP280.BMPTest import BMS
from MQX.MQ7 import MQ7 # CO
from MQX.MQ4 import MQ4 # CH4
from MQX.MQ131 import MQ131 # O3
from MQX.MQ135 import MQ135 # NH4 and CO2

class performance():
    """Testing pi Performance"""
    def __init__(self):
        #Sensor init.
        self.pms = PMS()#DHT
        self.bms = BMS()#BMP
        #MQX
        self.MQ4S = MQ4("CH4")
        self.MQ7S = MQ7("CO")
        self.MQ131S = MQ131("O3")
        self.MQ135NH4 = MQ135("NH4")
        self.MQ135CO2 = MQ135("CO2")
        self.__numberofsamples = 20
        
    def data(self):
        #BMP sensor
        temp , pres , hum = self.bms.readFunc()
        
        #PM sensor
        pm = self.pms.reading()
        
        #MQ sensor
        CH4 = self.MQ4S.PPM()
        CO = self.MQ7S.CorrectedPPM()
        O3 = self.MQ131S.CorrectedPPM()
        NH4 = self.MQ135NH4.CorrectedPPM()
        CO2 = self.MQ135CO2.CorrectedPPM()
        #if pm is not None:
        return temp , pres , hum , pm , CH4 , CO , O3 , NH4 , CO2
        #else:
        #   self.data()
    
    def performanceCSV(self):
    #Sensor init 
        
        startcsv = time.time()
        #CSVTest.CSVHead()
        for _ in range(self.__numberofsamples):
            temp , pres , hum , pm , CH4 , CO , O3 , NH4 , CO2 = self.data()   
            CSVTest.saveToCsv(pm[0],pm[1],temp,pres,hum,O3,NH4,CO,CH4,CO2)
        endcsv = time.time()
        return startcsv, endcsv
    
    def performanceTS(self):
        startTs = time.time()
        for _ in range(self.__numberofsamples):
            temp , pres , hum , pm , CH4 , CO , O3 , NH4 , CO2 = self.data()
            ThinkSpeakTest.thingspeakconn(pm[0],pm[1],temp , pres , O3, NH4, CO, CH4)
        endTs = time.time()
        return startTs, endTs
    
    
    def performanceWhole(self):
        
        startWp = time.time()
        #CSVTest.CSVHead()
        for _ in range(self.__numberofsamples):
            temp , pres , hum , pm , CH4 , CO , O3 , NH4 , CO2 = self.data()
            CSVTest.saveToCsv(pm[0],pm[1],temp,pres,hum,O3,NH4,CO,CH4,CO2)
            ThinkSpeakTest.thingspeakconn(pm[0],pm[1],temp , pres , O3, NH4, CO, CH4)
        endWp = time.time()
        return startWp, endWp
        
    
    def main(self, timeInSec=0):
        
        startcsv, endcsv = self.performanceCSV()
        timecsv = endcsv - startcsv + timeInSec
        startTs, endTs = self.performanceTS()
        timeTs = endTs - startTs + timeInSec
        startWp, endWp = self.performanceWhole()
        timeWp = endWp - startWp + timeInSec
        return timecsv, timeTs, timeWp
        #print("Execution time for CSV : {} , Execution time for Think Speak : {} , Execution time for Pi(Both CSV and Think Speak)  : {}".format(timecsv,timeTs,timeWp))
        
    
            
        
        
if __name__ == "__main__":
    
    try:
        #CSVTest.CSVHead()
        start = time.time()
        perf = performance()
        end = time.time()
        Execution_time = end - start
        timecsv, timeTs, timeWp = perf.main(Execution_time)
        print("Execution time for CSV : {} , Execution time for Think Speak : {} , Execution time for Pi(Both CSV and Think Speak)  : {}".format(timecsv, timeTs, timeWp))
        with open("/home/pi/Desktop/Airquality measureAdjusted/CSV/Performance.csv", 'ab') as csvfile:
            file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #if(!headerAdded):
            file.writerow(['Only CSV','Only Think Speak','Both CSV and Think Speak'])
            file.writerow([timecsv, timeTs, timeWp])
            for _ in range(20):
                timecsv, timeTs, timeWp = perf.main()
                file.writerow([timecsv, timeTs, timeWp])
                print("Execution time for CSV : {} , Execution time for Think Speak : {} , Execution time for Pi(Both CSV and Think Speak)  : {}".format(timecsv, timeTs, timeWp))
            csvfile.close()
    except KeyboardInterrupt:
        print('Finished')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)   

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        