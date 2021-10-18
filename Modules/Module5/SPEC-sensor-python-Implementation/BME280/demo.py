#!/usr/bin/env python

import bme280
import time
import math

def altitude(pressure):
    p = 0.01 * pressure
    alt = 145366.45 * (1 - math.pow(p/1013.25,0.190284))
    return alt

def main():
    bme = bme280.Bme280()
    bme.set_mode(bme280.MODE_FORCED)
    
    
    for i in range(20):
        t, p, h = bme.get_data()
        alt = altitude(p)
        print(f"Temperature : {t} °C , Pressure : {p} P , Humidity : {h} %% , altitude : {alt} ft")
        time.sleep(60)


if __name__ == '__main__':
    main()
