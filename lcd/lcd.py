from i2c_lcd import I2cLcd
from machine import Pin, SoftI2C

class LCD1602:
   
    def __init__(self, scl, sda, freq, addr, cols=16, rows=2, ):
        # Configurar el LCD
        i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda), freq=freq)
        self._connection = I2cLcd(i2c, addr, rows, cols)
        
    def update(self, temp=None, hum=None, pm25=None, pm10=None, hour=None, minute=None):
        # Lógica para mostrar la temperatura en la pantalla LCD 1602
                
        if (temp != None):
            self._connection.move_to(13,0)
            self._connection.putstr("{}".format(temp))
        
        if(hum != None):
            self._connection.move_to(7,0)
            self._connection.putstr("{}".format(hum))
                    
        if(pm25 != None):
            self._connection.move_to(5,1)
            self._connection.putstr('   ')
            self._connection.move_to(5,1)
            self._connection.putstr("{}".format(round(pm25)))
            
        if(pm10 != None):
            self._connection.move_to(13,1)
            self._connection.putstr('   ')
            self._connection.move_to(13,1)
            self._connection.putstr("{}".format(round(pm10)))
    
        if(minute!= None):
            self._connection.move_to(0,0)
            self._connection.putstr("{:02d}".format(hour))
            self._connection.move_to(3,0)
            self._connection.putstr("{:02d}".format(minute))
    
    def create_templeate(self, chars: dict,  char_position: dict, char_hex : list):
        
        [self._connection.custom_char(i, char) for i, char in enumerate(char_hex)]

        self._connection.clear()
        
        fila = 1
        for char_element, pos_element in zip(chars, char_position):
            for char, num_col in zip(chars[char_element], char_position[pos_element]):
                self._connection.move_to(num_col, fila)
                if (type(char)==int):
                    self._connection.putchar(chr(char))
                else:
                    self._connection.putstr(char)
            fila = fila - 1