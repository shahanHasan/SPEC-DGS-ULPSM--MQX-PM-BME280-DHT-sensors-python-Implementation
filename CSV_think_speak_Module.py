#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Sat Oct  3 14:37:05 2020."""

import time, datetime , csv , os , sys
from PMSensor.Pmsensor_py3 import ParticulateMolecular
from SPEC.DGS import DGS
import http.client
import urllib.parse
import BME280.bme280
import time
import math

def altitude(pressure):
    p = 0.01 * pressure
    alt = 145366.45 * (1 - math.pow(p/1013.25,0.190284))
    return alt

class CSV_ThinkSpeak_module(object):
    
    Number_of_samples = 20
    key = "INA8UXNZ478DYF8G"  # Put your API Key here
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    api_url = "api.thingspeak.com:80"
    datafile = 'data.csv'
    
    def thing_speak_connection(self, sense1, sense2, sense3, sense4, sense5, sense6, sense7, sense8):
        """
        Think Speak set up.
        
        Returns
        -------
        None.
    
        """
        params = urllib.parse.urlencode(
             {'field1': sense1, 
              'field2': sense2,
              'field3': sense3, 
              'field4': sense4, 
              'field5': sense5, 
              'field6': sense6, 
              'field7': sense7, 
              'field8': sense8, 
              'key':self.key })
        #param2 = urllib.urlencode({'field2': pm[1], 'key':key })
        #print("parameters taken")
        
        conn = http.client.HTTPConnection(self.api_url)
        try:
            #print("----try catch 1 ------")
            conn.request("POST", "/update", params, self.headers)
            response = conn.getresponse()
            #print("PM2.5 : " + pm[0])
            #print("PM10 : " + pm[1])
            #print(response.status, response.reason)
            data = response.read()
            conn.close()
        except:
            print("connction failed")
            #print("why???")

    def CSVHead(self):
        """
        Add csv head row.
    
        Returns
        -------
        None.
    
        """
        with open(self.datafile, 'a') as csvfile:
            file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            #if(!headerAdded):
            file.writerow(['date and Time', 'CO', 'SO2', 'pm2.5','pm10', 'Temperature', 'Pressure', 'Humidity', 'Pressure Altitude'])
            csvfile.close()
                
    
    def saveToCsv(self, sense1, sense2, sense3, sense4, sense5, sense6, sense7, sense8):
        """
        Save data to CSV, CSV set up.
    
        Parameters
        ----------
        sense1 : TYPE -> Float
            DESCRIPTION. -> Sensor Data
        sense2 : TYPE
            DESCRIPTION.
        sense3 : TYPE
            DESCRIPTION.
        sense4 : TYPE
            DESCRIPTION.
        sense5 : TYPE
            DESCRIPTION.
        sense6 : TYPE
            DESCRIPTION.
        sense7 : TYPE
            DESCRIPTION.
        sense8 : TYPE
            DESCRIPTION.

    
        Returns
        -------
        None.
    
        """
        with open(self.datafile, 'a') as csvfile:
            file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            file.writerow([datetime.datetime.now().replace(microsecond=0).isoformat().replace('T', ' ')
            , sense1, sense2, sense3, sense4, sense5, sense6, sense7, sense8])
            csvfile.close()
            
    
    def main(self):
        """
        Main.
    
        Returns
        -------
        None.
    
        """
        
        try:
            bme = BME280.bme280.Bme280()
            bme.set_mode(BME280.bme280.MODE_FORCED)
            
            pms = ParticulateMolecular('/dev/ttyUSB0')
            pms.wake()
            time.sleep(2)
            
            SO2 = DGS('/dev/ttyUSB1', 9600, 1)
            SO2.sensor_wake()
            SO2.set_continous_mode()
            
            CO = DGS('/dev/ttyUSB2', 9600, 1)
            CO.sensor_wake()
            CO.set_continous_mode()
            
            if(os.path.getsize(self.datafile) == 0):
                self.CSVHead()
                
            # for _ in range(self.Number_of_samples):
            while True:
                #BME
                t, p, h = bme.get_data()
                alt = altitude(p)
                
                #PM sensor
                data_pm = pms.read_pm_data()
                
                #SPEC sensor
                SO2.get_sensor_data()
                conc_so2 = SO2.get_conc_ppm()
                
                CO.get_sensor_data()
                conc_co = CO.get_conc_ppm()
                if not [x for x in (data_pm, conc_so2, conc_co, t, p, h) if x is None]:
                    self.thing_speak_connection(data_pm[0], data_pm[1], conc_so2, conc_co, t, p, h, alt)
                    self.saveToCsv(conc_co, conc_so2, data_pm[0], data_pm[1], t, p, h, alt)
                    print(f" SO2 : {conc_so2} ppm , CO : {conc_co} ppm , pm2.5 : {data_pm[0]} μ g/cubic m , pm10 : {data_pm[1]} μ g/cubic m , Temperature : {t} °C , Pressure : {p} P , Humidity : {h} %% , altitude : {alt} ft")
                    time.sleep(600)
                continue
    
            
            # SO2.stop_continuous_data_flow()
            # SO2.sensor_sleep()
            # SO2.close_serial()
            
            # CO.stop_continuous_data_flow()
            # CO.sensor_sleep()
            # CO.close_serial()
            
            # pms.sleep()
            # time.sleep(3)
            # pms.close_serial() 
            
        except KeyboardInterrupt:
            print("Keyboard exit")
            SO2.stop_continuous_data_flow()
            SO2.sensor_sleep()
            SO2.close_serial()
            
            CO.stop_continuous_data_flow()
            CO.sensor_sleep()
            CO.close_serial()
            
            pms.sleep()
            time.sleep(3)
            pms.close_serial() 
            
        
            
if __name__ == "__main__":
    
    
    csv_think_speak_module = CSV_ThinkSpeak_module()
    start = time.time()
    csv_think_speak_module.main()
    end = time.time()
    print(f"time : {end - start}")
    # try:
    #     pass
    # except KeyboardInterrupt:
    #     print('Interrupted')
    #     try:
    #         sys.exit(0)
    #     except SystemExit:
    #         os._exit(0)   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    