#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 13:03:50 2021

@author: shahan
"""

import requests
import json
import pickle
import os




class Location(object):
    url = 'https://extreme-ip-lookup.com/json/'
    directory = "Data"
    path_dir = "/home/pi/Desktop/Module2/SPEC-sensor-python-Implementation"
    loc_data = {}

    
    def location_Data(self):
        r = requests.get(self.url)
        data = json.loads(r.content.decode())
        return data
    
    def get_data(self):
        data = self.location_Data()
        
        continent = data['continent']
        country = data['country']
        city = data['city']
        country_code = data['countryCode']
        latitude = data['lat']
        longitude = data['lon']
        Ip = data['query']
        Ip_type = data['ipType']
        
        return continent, country, city, country_code, latitude, longitude, Ip, Ip_type
    
    def make_data_dir(self):
        dir_data = os.path.join(self.path_dir, self.directory)
        # Make a directory if it does not exist
        
        if not os.path.exists(dir_data):
            print(f'directory does not exist, making new directory, directory path : {dir_data}')
            os.mkdir(dir_data)
            
        return dir_data
    
    def Handle_location(self):
        
        dir_data = os.path.join(self.path_dir, self.directory)
        # Make a directory if it does not exist
        
        if not os.path.exists(dir_data):
            print(f'directory does not exist, making new directory, directory path : {dir_data}')
            os.mkdir(dir_data)
            
        
            
        continent, country, city, country_code, latitude, longitude, Ip, Ip_type = self.get_data()
        #print(f"continent : {continent}, country : {country}, city : {city}, country code : {country_code}, latitude : {latitude}, longitude : {longitude}, Ip : {Ip}, Ip_type : {Ip_type}")
        
        self.loc_data['continent'] = continent
        self.loc_data['country'] = country
        self.loc_data['city'] = city
        self.loc_data['country_code'] = country_code
        self.loc_data['latitude'] = latitude
        self.loc_data['longitude'] = longitude
        self.loc_data['Ip'] = Ip
        self.loc_data['Ip_type'] = Ip_type
        
        loc_dir = f'{latitude}_{longitude}'
        loc_dir_data = os.path.join(dir_data, loc_dir)
        
        if not os.path.exists(loc_dir_data):
            print(f'directory does not exist, making new directory, directory path : {loc_dir_data}')
            os.mkdir(loc_dir_data)
        
        # create a filename to store location data 
        
        filename = 'location'
        full_path = os.path.join(loc_dir_data, filename)
        #print(f'full path : {full_path}')
        # check if the file exists, if not make one
        if(not os.path.isfile(full_path)):
            print(f'file does not exist , making new file, file name : {filename} file path : {full_path}')
            # IF does not Exist, Create
            f = open(full_path, "x")
            f.close()
        # check if file is empty , if not return saved data, fill with pickle data
        if (not os.stat(full_path).st_size == 0):
            print('File is not empty')
            infile = open(full_path,'rb')
            SavedData = pickle.load(infile)
            infile.close()
            return SavedData , loc_dir_data
        else:
            print('file is empty, storing data into it.')
            outfile = open(full_path,'wb')
            pickle.dump(self.loc_data, outfile)
            outfile.close()
            return self.loc_data , loc_dir_data
        
        
        
        
        
if __name__ == '__main__':
    
    loc = Location()
    data, loc_dir_data = loc.Handle_location()
    #continent, country, city, country_code, latitude, longitude, Ip, Ip_type = loc.get_data()
    
    print(f"continent : {data['continent']}, country : {data['country']}, city : {data['city']}, country code : {data['country_code']}, latitude : {data['latitude']}, longitude : {data['longitude']}, Ip : {data['Ip']}, Ip_type : {data['Ip_type']}")
    