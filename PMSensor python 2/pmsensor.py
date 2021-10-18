#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Sun Sep 20 01:14:31 2020."""
from __future__ import print_function
import serial, struct, time, csv, datetime
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ser = serial.Serial()
#ser.port = sys.argv[1]
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

ser.open()
ser.flushInput()

class PMS:
        """Sends data in byte String , so decode it."""
        
        # Sampling interval
        sleep_interval , wake_interval = 5 , 5 
        # 0xAA, 0xB4, 0x06, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x06, 0xAB
        def sensor_wake(self):
            """
            Wake sensor up.
            
            '\x01', data byte 3 set to 0 , to signal sensor to wake up.

            Returns
            -------
            None.

            """
            bytes = ['\xaa', #head
            '\xb4', #command 1
            '\x06', #data byte 1
            '\x01', #data byte 2 (set mode)
            '\x01', #data byte 3 (work)
            '\x00', #data byte 4
            '\x00', #data byte 5
            '\x00', #data byte 6
            '\x00', #data byte 7
            '\x00', #data byte 8
            '\x00', #data byte 9
            '\x00', #data byte 10
            '\x00', #data byte 11
            '\x00', #data byte 12
            '\x00', #data byte 13
            '\xff', #data byte 14 (device id byte 1)
            '\xff', #data byte 15 (device id byte 2)
            '\x06', #checksum
            '\xab'] #tail

            for b in bytes:
                ser.write(b)
        
        # xAA, 0xB4, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x05, 0xAB
        def sensor_sleep(self):
            """
            Sensor to Sleep, turned off till woken.
            
            '\x00', data byte 3 set to 0 , to signal sensor to sleep.
           
            Returns
            -------
            None.
            
            """
            bytes = ['\xaa', #head
            '\xb4', #command 1
            '\x06', #data byte 1
            '\x01', #data byte 2 (set mode)
            '\x00', #data byte 3 (sleep)
            '\x00', #data byte 4
            '\x00', #data byte 5
            '\x00', #data byte 6
            '\x00', #data byte 7
            '\x00', #data byte 8
            '\x00', #data byte 9
            '\x00', #data byte 10
            '\x00', #data byte 11
            '\x00', #data byte 12
            '\x00', #data byte 13
            '\xff', #data byte 14 (device id byte 1)
            '\xff', #data byte 15 (device id byte 2)
            '\x05', #checksum
            '\xab'] #tail

            for b in bytes:
                ser.write(b)

        def process_frame(self, d):
            """
            Process Each byte String and extrapolate PM2.5 and PM10.

            Parameters
            ----------
            d : TYPE -> Raw sensor Data. in byte Strings.
                DESCRIPTION.

            Returns
            -------
            data : TYPE -> List of PM2.5 and PM10 
                DESCRIPTION.

            """
            #dump_data(d) #debug
            r = struct.unpack('<HHxxBBB', d[2:])
            pm25 = r[0]/10.0
            pm10 = r[1]/10.0
            checksum = sum(ord(v) for v in d[2:8])%256
            #print("PM 2.5: {} μg/m^3  PM 10: {} μg/m^3 CRC={}".format(pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))
            #self.result_pm25.set(pm25)
            #self.result_pm10.set(pm10)
            if (checksum==r[2] and r[3]==0xab):
                data = [pm25, pm10]
                return data

            
        def sensor_read(self):
            """
            Read raw sensor Value.

            Returns
            -------
            data : TYPE
                DESCRIPTION.

            """
            byte = 0
            while byte != "\xaa":
                byte = ser.read(size=1)
                d = ser.read(size=10)
                if d[0] == "\xc0":
                    data = self.process_frame(byte + d)
                    return data
                
        def reading(self):
            """
            Return PM values.

            Returns
            -------
            pm : TYPE -> float
                DESCRIPTION. -> reading of pm2.5 and pm10

            """
            self.sensor_wake()
            time.sleep(self.wake_interval)
            pm = self.sensor_read()
            self.sensor_sleep()
            time.sleep(self.sleep_interval)
            if pm is not None:
                return pm
            else:
                return self.reading()

        def sensor_live(self):
            """
            Live Sensor data for debugging.

            Returns
            -------
            None.

            """
            x = []
            y1 = []
            y2 = []
            i = 0
            while True: # change time interval here, if required
                self.sensor_wake()
                time.sleep(self.wake_interval)
                pm = self.sensor_read()
                if pm is not None:
                    x.append(i)
                    y1.append(pm[0])
                    y2.append(pm[1])
                    with open('/home/pi/Desktop/Airquality measure/data.csv', 'ab') as csvfile:
                        file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        file.writerow([datetime.datetime.now().replace(microsecond=0).isoformat().replace('T', ' '), pm[0], pm[1]])
                        csvfile.close()
                #print("PM 2.5: {} μg/m^3  PM 10: {} μg/m^3").format(pm[0], pm[1])
                self.sensor_sleep()
                i += 1
                time.sleep(self.sleep_interval)

if (__name__ == "__main__"):
    obj1 = PMS()
    data = obj1.reading()
    print("pm2.5 : {} pm10 : {}".format(data[0],data[1]))
