'''
Created on 2017. 7. 24.

@author: SJ
'''
import time, xlwt
from pyowm import OWM
import sys

class WeatherAPI():
    API_key = '1f5aaef161771efd6c64b08553f03a31'
    tFlag = False
    
    def __init__(self):
        self.now = time.localtime()
        self.curHour = self.now.tm_hour
        self.now = time.localtime()
        self.today = str(self.now.tm_year)+'.'+str(self.now.tm_mon)+'.'+str(self.now.tm_mday)
        self.time = str(self.now.tm_hour)+':'+str(self.now.tm_min)

    def run(self):
        owm = OWM(self.API_key)
        obs = owm.weather_at_coords(37.566553, 126.977909)
        w = obs.get_weather()
            
        status = w.get_status()
        temperature =  w.get_temperature(unit='celsius')['temp']
        humidity = w.get_humidity()
        
        wb = xlwt.Workbook(encoding="utf-8")
        ws = wb.add_sheet('Sheet1')
        ws.write(0,1,"Status")
        ws.write(0,2,'Temperature')
        ws.write(0,3,'Humidity')
        ws.write(1,0,self.time)
        ws.write(1,1,status)
        ws.write(1,2,temperature)
        ws.write(1,3,humidity)
        
        wb.save('uploader/Weather.xls')
        
        
            
        
        
        
        
