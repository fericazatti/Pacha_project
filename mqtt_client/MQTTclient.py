from umqtt.simple import MQTTClient
import json
import time

class MQTTclient:
    
    def __init__(self, mqtt_server, client_id, topic):
        self._client = MQTTClient(client_id, mqtt_server)
        #self.client.connect()        
        self._topic = topic
        
        self._message = {'temp': None,
                        'hum': None,
                        'pm10': None,
                        'pm25': None}
        
        self._timedata = {'year': None,
                          'month': None,
                          'mday': None,
                          'hour': None,
                          'minute':None,
                          'second':None                                                    
                        }
        
    def is_complete(self):        
        for value in self._message.values():
            if value is None:
                return False
        return True
              
    def connect(self):
        self._client.connect()       
            
    def update(self, temp=None, hum=None, pm25=None, pm10=None, hour=None, minute=None):        
        
        if (temp != None):
           self._message['temp'] = temp
           self._message['hum'] = hum
           #self._client.publish(self._topic, "temp: {} hum: {}".format(temp, hum))
        if (pm25 != None):
           self._message['pm25'] = pm25
           self._message['pm10'] = pm10
           #self._client.publish(self._topic, "pm2.5: {} pm10: {}".format(pm25, pm10))
        
        if self.is_complete():
           year, month, mday, hour, minute, second, weekday, yearday = time.localtime()
           self._timedata['hour'] = hour
           self._timedata['minute'] = minute
           self._timedata['second'] = second
           self._timedata['year'] = year
           self._timedata['month'] = month
           self._timedata['mday'] = mday
           self._timedata.update(self._message)
           jsonmsg = json.dumps(self._timedata)
           self._client.publish(self._topic, jsonmsg)
           self._message = {value: None for value in self._message.keys()}
