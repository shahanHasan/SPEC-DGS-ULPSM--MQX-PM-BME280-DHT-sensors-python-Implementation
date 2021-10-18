#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 21:20:15 2021

@author: shahan
"""

import time , serial
import pyfirmata
import math
import curses


port = '/dev/ttyACM0'
board = pyfirmata.Arduino(port)
it = pyfirmata.util.Iterator(board)
it.start()
time.sleep(0.2)

 # Arduino Setup
analog_input_c = board.get_pin('a:{}:i'.format(1))
time.sleep(0.2)
analog_input_t = board.get_pin('a:{}:i'.format(2))
time.sleep(0.2)
analog_input_c.enable_reporting()
time.sleep(0.2)
analog_input_t.enable_reporting()
time.sleep(0.2)

def voltage(value):#for custom ADC
    #linear mapping of 0 to 1 analog read to 0 to 3.3 sensor voltage
    volt = (value) * 3.31 / (pow(2,1) - 1)
    return volt

def getADC(value):
    adc = (1023 * value) / 3.3
    return adc


def main(stdscr):
    stdscr.nodelay(1)
    for _ in range(20):
        
        c = stdscr.getch()
        if(c != -1):
            print("user input section")
        resp_t = analog_input_t.read()
        resp_t = voltage(resp_t)
        #resp_t = getADC(resp_t)
        resp_c = analog_input_c.read()
        resp_c = voltage(resp_c)
        #resp_c = getADC(resp_c)
        print(f"concentration raw {resp_c}  temperature raw {resp_t} ")
        time.sleep(2)
        
if __name__ == '__main__':
    curses.wrapper(main)
        
    

