#imports
from lcd.lcd import LCD1602
from sensors.dht11.dht11 import dht11

import network
import ntptime
import time

from machine import Pin
from machine import RTC, UART, SoftI2C

fila_cero = [2, 6, 9, 11, 12, 15]
fila_uno = [1, 2, 3, 4, 9, 10, 11, 12]
char_filacero = [":", 0, "%", "T", ":", 3]
char_filauno = ["P", "M", 2, ":", "P", "M", 1, ":"]

hr = bytearray([0x14, 0x1C, 0x14, 0x00,  0x07, 0x05, 0x06, 0x05])
pm10 = bytearray([ 0x00, 0x00, 0x00, 0x00, 0x17, 0x15, 0x15, 0x17])
pm25 = bytearray([0x00, 0x00, 0x00, 0x1B, 0x0A, 0x1B, 0x11, 0x1B])
grados_cent = bytearray([ 0x18, 0x18, 0x00, 0x07, 0x04, 0x04, 0x04, 0x07])

DHT11_PIN = 5 

station = network.WLAN(network.STA_IF)

SSID = 'Icazatti'
PSWD = 'Geniuslg'

def connect(ssid, pswd):
  ssid = ssid
  password = pswd  
  station.active(True)
  station.connect(ssid, password)
  while station.isconnected() == False:    
    pass
  time.sleep(2)
  print(station.ifconfig())
 
def disconnect():
  if station.active() == True: 
   station.active(False)
  if station.isconnected() == False:
#     lcd.clear()
#     lcd.putstr("Disconnected")
      time.sleep(2)
#     lcd.clear()


 
connect(SSID, PSWD)

rtc = RTC()
ntptime.settime()
(year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
print ("UTC Time: ")
print((year, month, day, hours, minutes, seconds))

sec = ntptime.time()
timezone_hour = -3
timezone_sec = timezone_hour * 3600
sec = int(sec + timezone_sec)
(year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)
print ("IST Time: ")
print((year, month, day, hours, minutes, seconds))
rtc.datetime((year, month, day, 0, hours, minutes, seconds, 0))
disconnect()

# sensors and lcd instances
lcd_display = LCD1602(scl=Pin(22), sda=Pin(21), freq=1000, addr=0x3f)
dht11_sensor = dht11(DHT11_PIN)



# Agregar la pantalla LCD como observador del sensor y del reloj
dht11_sensor.add_observer(lcd_display)

# crear templeate del lcd
lcd_display.create_templeate(char_position={'fila0': fila_cero, 'fila1': fila_uno},
                             chars={'fila0':char_filacero, 'fila1':char_filauno},
                             char_hex=[hr, pm10, pm25, grados_cent])

# Simular lectura de temperatura y notificar a los observadores solo cada 5 segundos
while True:
    year, month, mday, hour, minute, second, weekday, yearday = time.localtime()
    lcd_display.update(hour = hour, minute = minute)
    dht11_sensor.read_temperature()    
    time.sleep(3)  # Esperar 1 segundo antes de la próxima iteración