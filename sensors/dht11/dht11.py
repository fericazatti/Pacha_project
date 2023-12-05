#libraries from dht
from dht import DHT11

class dht11:
    
    def __init__(self, pin):
        self._observers = set()
        self._dht_sensor = DHT11(pin)         

    def add_observer(self, observer):
        self._observers.add(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def read_temperature(self):
        self._dht_sensor.measure()
        temperature = self._dht_sensor.temperature()
        humidity = self._dht_sensor.humidity()
        
        self._notify_observers(temperature, humidity)

    def _notify_observers(self, temperature, humidity):        
        for observer in self._observers:
            observer.update(temp = temperature, hum = humidity)
            