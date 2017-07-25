'''
Created on 2017. 7. 24.

@author: SJ
'''
from pyowm import OWM

class Weather:
    API_key = '1f5aaef161771efd6c64b08553f03a31'
    
    def WeatherAPI(self):
        owm = OWM(self.API_key)
        obs = owm.weather_at_coords(37.566553, 126.977909)
        w = obs.get_weather()
        
        status = w.get_status()
        temperature =  w.get_temperature(unit='celsius')['temp']
        humidity = w.get_humidity()
        
        wList = [status, temperature, humidity]
        print 'Seoul :', w.get_status(), w.get_temperature(unit='celsius')['temp'],  w.get_humidity()

A = Weather()
A.WeatherAPI()
