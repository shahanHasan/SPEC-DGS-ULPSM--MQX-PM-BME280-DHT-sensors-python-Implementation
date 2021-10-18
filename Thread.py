#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Sun Oct  4 05:08:15 2020."""

import threading
import os , sys
import CSVTest
import ThinkSpeakTest
from PiPerformance import performance



#threadLock = threading.Lock()
# temp , pres , hum , pm , CH4 , CO , O3 , NH4 , CO2 = perf.data()
# csvlist = []
# thinkspeaklist = []
# csvlist.extend([pm[0],pm[1],temp,pres,hum,O3,NH4,CO,CH4,CO2])
# thinkspeaklist.extend(pm[0],pm[1],temp , pres , O3, NH4, CO, CH4)

class ThreadCSV (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.running = True

      
    def run(self):
        while self.running:
            # Get lock to synchronize threads
            threadLock.acquire()
            print("Starting " + self.name)
            CSV_write()
            #Free lock to release next thread
            threadLock.release()

    def stop(self):
        self.running = False
      

class ThreadTS (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.running = True
      
    def run(self):
        while self.running:
            # Get lock to synchronize threads
            threadLock.acquire()
            print("Starting " + self.name)
            TS_send()
            # Free lock to release next thread
            threadLock.release()
            
    def stop(self):
        self.running = False



def CSV_write():
    #while True:
    #if exitFlag:
    #    threadName.exit()
    temp , pres , hum , pm , CH4 , CO , O3 , NH4 , CO2 = perf.data()
    CSVTest.saveToCsv(pm[0],pm[1],temp,pres,hum,O3,NH4,CO,CH4,CO2)

def TS_send():
    #while True:
    #if exitFlag:
    #    threadName.exit()
    temp , pres , hum , pm , CH4 , CO , O3 , NH4 , CO2 = perf.data()
    ThinkSpeakTest.thingspeakconn(pm[0],pm[1],temp , pres , O3, NH4, CO, CH4)
        
def main():
    
    #threadLock = threading.Lock()
    threads = []
    # Create new threads
    thread1 = ThreadCSV(1, "Thread-CSV")
    thread2 = ThreadTS(2, "Thread-Think Speak")
    
    thread1.daemon = True #set this thread as a Daemon Thread
    thread2.daemon = True
    # Start new Threads
    thread1.start()
    thread2.start()
    
    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)

    # Wait for all threads to complete
    for t in threads:
        t.join()
    #print("Exiting Main Thread")


if (__name__ == "__main__"):
    try:
        #exitFlag = 0
        perf = performance()
        threadLock = threading.Lock()
        main()
    except KeyboardInterrupt:
        ThreadCSV.stop()
        ThreadTS.stop()
        print('Finished')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)  




































