import network
import time

station = network.WLAN(network.STA_IF)

def connect(ssid, pswd):
    station.active(True)
    station.connect(ssid, pswd)
    while not station.isconnected():
        pass
    time.sleep(2)
    print(station.ifconfig())
    
def disconnect():
    if station.active():
        station.active(False)
    time.sleep(2)
    
def setup_time():
    rtc = RTC()
    ntptime.settime()
    
    (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()

    sec = ntptime.time()
    timezone_hour = -3
    timezone_sec = timezone_hour * 3600
    sec = int(sec + timezone_sec)
    
    (year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)
    
    rtc.datetime((year, month, day, 0, hours, minutes, seconds, 0))
 