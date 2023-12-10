#imports
from lcd.lcd import LCD1602
from wifi_functions import connect, disconnect, setup_time
from sensors.dht11.dht11 import dht11
from sensors.sds011.sds011 import sds011
from config import SSID, PSWD

import time

from machine import Pin, Timer, UART, SoftI2C

#constants 

fila_cero = [2, 6, 9, 11, 12, 15]
fila_uno = [1, 2, 3, 4, 9, 10, 11, 12]
char_filacero = [":", 0, "%", "T", ":", 3]
char_filauno = ["P", "M", 2, ":", "P", "M", 1, ":"]

hr = bytearray([0x14, 0x1C, 0x14, 0x00,  0x07, 0x05, 0x06, 0x05])
pm10 = bytearray([ 0x00, 0x00, 0x00, 0x00, 0x17, 0x15, 0x15, 0x17])
pm25 = bytearray([0x00, 0x00, 0x00, 0x1B, 0x0A, 0x1B, 0x11, 0x1B])
grados_cent = bytearray([ 0x18, 0x18, 0x00, 0x07, 0x04, 0x04, 0x04, 0x07])

global fan_on 

DHT11_PIN = 5 
SDS011_UART = UART(1, baudrate = 9600, rx = 16, tx = 17)

#interruption
def timer_callback():
  global read_data
  read_data = True

#set up wifi
connect(SSID, PSWD)
setup_time()
disconnect()

# sensors and lcd instances
lcd_display = LCD1602(scl=Pin(22), sda=Pin(21), freq=1000, addr=0x3f)
dht11_sensor = dht11(DHT11_PIN)
sds011_sensor = sds011(SDS011_UART)

# Adding the LCD as an observer
dht11_sensor.add_observer(lcd_display)
sds011_sensor.add_observer(lcd_display)

#Timer instance
timer = Timer(0)

#interrupt config
timer.init(period=10000, mode=Timer.PERIODIC, callback=timer_callback)

#Creating an LCD template
lcd_display.create_templeate(char_position={'fila0': fila_cero, 'fila1': fila_uno},
                             chars={'fila0':char_filacero, 'fila1':char_filauno},
                             char_hex=[hr, pm10, pm25, grados_cent])

read_data =  False
fan_on = False      

# Simulating temperature reading and notifying observers only every 20 seconds
while True:
  
  year, month, mday, hour, minute, second, weekday, yearday = time.localtime()
  if read_data:
    read_data = False
    if fan_on:
      sds011_sensor.read_pm()
      sds011_sensor.sleep()
      fan_on = False
     else:
      sds011_sensor.wake()
      fan_on = True
    dht11_sensor.read_temperature()
    lcd_display.update(hour = hour, minute = minute) 