#libraries from sds
from sds011 import SDS011
from machine import UART

class sds011:
    
    def __init__(self, uart):
        self._observers = set()
        self._sds_sensor = SDS011(uart)
 
    def add_observer(self, observer):
        self._observers.add(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def read_pm(self):
        self._sds_sensor.read()
        pm25 = self._sds_sensor.pm25
        pm10 = self._sds_sensor.pm10
       
        self._notify_observers(pm25, pm10)
        
    def wake(self):
        self._sds_sensor.wake()
    
    def sleep(self):
        self._sds_sensor.sleep()

    def _notify_observers(self, pm25, pm10):        
        for observer in self._observers:
            observer.update(pm25 = pm25, pm10 = pm10)