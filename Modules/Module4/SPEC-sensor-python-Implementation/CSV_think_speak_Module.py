#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Sat Oct  3 14:37:05 2020."""

import time, datetime , csv , os 
from PMSensor.Pmsensor_py3 import ParticulateMolecular
from SPEC.DGS import DGS
import http.client
import urllib.parse , urllib.error, urllib.request
import BME280.bme280
import math
from Location import Location
import socket

def altitude(pressure):
    p = 0.01 * pressure
    alt = 145366.45 * (1 - math.pow(p/1013.25,0.190284))
    return alt

def internet_on():
    try:
        urllib.request.urlopen('https://www.google.com/', timeout=1)
        return True
    except urllib.error.URLError as err: 
        return False
    except socket.timeout: 
        return False    

class CSV_ThinkSpeak_module(object):
    
    Number_of_samples = 20
    key = "CHMD4ZKPHEJII17Q"  # Put your API Key here
    #key = "6W64ICAQTZF70U63"  # Put your API Key here
    #key = "VTZA5FRW18BJVCGU"  # Put your API Key here
    #key = "K2KI3PJ1SQFJSR2U"  # Put your API Key here
    
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    api_url = "api.thingspeak.com:80"
    flag = True
    pm_flag = True
    #datafile = 'data.csv'
    
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
            resp = response.read()
            print(resp)
            conn.close()
        except:
            print("connction failed")
            #print("why???")

    def CSVHead(self, fileName):
        """
        Add csv head row.
    
        Returns
        -------
        None.
    
        """
        with open(fileName, 'a') as csvfile:
            file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            #if(!headerAdded):
            file.writerow(['date and Time', 'CO', 'SO2', 'O3', 'NO2', 'pm2.5','pm10', 'Temperature', 'Pressure', 'Humidity', 'Pressure Altitude'])
            csvfile.close()
                
    
    def saveToCsv(self, fileName, sense1, sense2, sense3, sense4, sense5, sense6, sense7, sense8, sense9, sense10):
        """
        Save data to CSV, CSV set up.
    
        Returns
        -------
        None.
    
        """
        with open(fileName, 'a') as csvfile:
            file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            file.writerow([datetime.datetime.now().replace(microsecond=0).isoformat().replace('T', ' ')
            , sense1, sense2, sense3, sense4, sense5, sense6, sense7, sense8, sense9, sense10])
            csvfile.close()
            
    
    def main(self):
        """
        Main.
    
        Returns
        -------
        None.
    
        """
        
        try:
            
            while True:
                internet_flag = internet_on()
                if(internet_flag):
                    break
                else:
                    print("Please wait!!!")
            
            loc = Location()
            dir_data = loc.make_data_dir()
            Data_File_Name = 'data.csv'
            full_path = os.path.join(dir_data, Data_File_Name)
            
            # check if the file exists, if not make one
            if(not os.path.isfile(full_path)):
                print(f'file does not exist , making new file, file name : {Data_File_Name} file path : {full_path}')
                f = open(full_path, "x")
                f.close()
                
            if(os.path.getsize(full_path) == 0):
                self.CSVHead(full_path)
            
            
            #bme = BME280.bme280.Bme280()
            #bme.set_mode(BME280.bme280.MODE_FORCED)
            
            pms = ParticulateMolecular('/dev/ttyUSB4')
            
            SO2 = DGS('/dev/ttyUSB3', 9600, 1)
            SO2.sensor_wake()
            SO2.set_continous_mode()
            
            CO = DGS('/dev/ttyUSB1', 9600, 1)
            CO.sensor_wake()
            CO.set_continous_mode()
            
            O3 = DGS('/dev/ttyUSB0', 9600, 1)
            O3.sensor_wake()
            O3.set_continous_mode()
            
            NO2 = DGS('/dev/ttyUSB2', 9600, 1)
            NO2.sensor_wake()
            NO2.set_continous_mode()
            
            
            i = 0   
            # for _ in range(self.Number_of_samples):
            while True:
                print(f"------- Iteration {i} --------")
                i += 1
                #BME
                #t, p, h = bme.get_data()
                #alt = altitude(p)
                
                #PM sensor
                if self.pm_flag:
                    pms.wake()
                    time.sleep(2)
                self.flag = False
                
                data = pms.read_pm_data()
                
                #SPEC sensor
                SO2.get_sensor_data()
                conc_so2 = SO2.get_conc_ppm()
                
                CO.get_sensor_data()
                conc_co = CO.get_conc_ppm()
                
                O3.get_sensor_data()
                conc_O3 = O3.get_conc_ppm()
                
                NO2.get_sensor_data()
                conc_NO2 = NO2.get_conc_ppm()
                
                
                if not [x for x in (data, conc_so2, conc_co, conc_O3, conc_NO2) if x is None]:
                    
                    self.thing_speak_connection(data[0], data[1], conc_so2, conc_co, conc_O3, conc_NO2, 0, 0)
                    self.saveToCsv(full_path, conc_co, conc_so2, conc_O3, conc_NO2, data[0], data[1], 0, 0, 0, 0)
                    
                    #self.thing_speak_connection(data[0], data[1], conc_so2, conc_co, conc_O3, conc_NO2, t, h)
                    #self.saveToCsv(full_path, conc_co, conc_so2, conc_O3, conc_NO2, data[0], data[1], t, p, h, alt)
                    
                    # print(f" SO2 : {conc_so2} ppm , CO : {conc_co} ppm , O3 : {conc_O3} ppm , NO2 : {conc_NO2} ppm , pm2.5 : {data[0]} μ g/cubic m , pm10 : {data[1]} μ g/cubic m , Temperature : {t} °C , Temperature from ULPSM_H2S : {temp_H2S} °C , Temperature from ULPSM_NO2 : {temp_NO2} °C ,  Pressure : {p} P , Humidity : {h} %% , altitude : {alt} ft")
                    #print(f" SO2 : {conc_so2} ppm , CO : {conc_co} ppm , O3 : {conc_O3} ppm , NO2 : {conc_NO2} ppm , pm2.5 : {data[0]} μ g/cubic m , pm10 : {data[1]} μ g/cubic m , Temperature : {t} °C , Pressure : {p} P , Humidity : {h} %% , altitude : {alt} ft")
                    pms.sleep()
                    self.flag = True
                    self.pm_flag = True
                    time.sleep(600)
                else:
                    
                    self.pm_flag = False
                    self.flag = False
            
        except KeyboardInterrupt:
            print("Keyboard exit")
            SO2.stop_continuous_data_flow()
            SO2.sensor_sleep()
            SO2.close_serial()
            
            CO.stop_continuous_data_flow()
            CO.sensor_sleep()
            CO.close_serial()
            
            O3.stop_continuous_data_flow()
            O3.sensor_sleep()
            O3.close_serial()
            
            NO2.stop_continuous_data_flow()
            NO2.sensor_sleep()
            NO2.close_serial()
            
            if(not self.flag):
                pms.sleep()
                time.sleep(3)
                pms.close_serial() 
            
        
            
if __name__ == "__main__":
    
    
    csv_think_speak_module = CSV_ThinkSpeak_module()
    start = time.time()
    csv_think_speak_module.main()
    end = time.time()
    print(f"time : {end - start}")

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
