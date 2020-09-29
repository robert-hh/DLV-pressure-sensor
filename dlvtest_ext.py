# The MIT License (MIT)

# Copyright (c) 2020 HTW Dresden

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from machine import Pin
import time
import dlv_ps_ext as dlv_ps

from machine import I2C
i2c=I2C(-1, scl=Pin(25), sda=Pin(26), freq=400000) ## ESP32 Soft
# i2c=I2C(1, scl=Pin(25), sda=Pin(26), freq=400000) ## ESP32 Hard

# i2c=I2C(scl=Pin(5), sda=Pin(4), freq=400000) ## ESP8266 Soft

# i2c=I2C(0, scl=Pin(Pin.PB_13), sda=Pin(Pin.PB_14), freq=400000) ## W600 Hard
# i2c=I2C(-1, scl=Pin(Pin.PB_13), sda=Pin(Pin.PB_14), freq=400000) ## W600 Hard

# i2c=I2C(scl="X1", sda="X2", freq=400000) ## PyBoard Soft
# i2c=I2C("X", freq=400000) ## PyBoard Hard
# Pin("EN_3V3")(1) # enable 3.3V Output on Pyboard D

# i2c=I2C(0, pins=('P9','P10'), baudrate=400000) # Pycom Hard I2C
# i2c=I2C(2, pins=('P9','P10'), baudrate=400000) # Pycom Soft I2C

# import busio    # Circuitpython
# import board    # Circuitpython
# i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)    # Circuitpython Hard I2C
# i2c.try_lock()    # Circuitpython

# i2c=I2C(1, freq=400000) # XBEE 3 Hard I2C

dlv=dlv_ps.DLV_I2C(i2c, model="030g", offset=1638)

# from machine import SPI
# spi =SPI(-1, baudrate=10000, sck=Pin(12, Pin.OUT), miso=Pin(13, Pin.IN), mosi=Pin(4), polarity=0, phase=0)
# dlv=dlv_ps.DLV_SPI((spi, Pin(27, Pin.OUT),), model="015D") # esp32 Soft SPI

# dlv=dlv_ps.DLV_SPI((Pin(25, Pin.OUT), Pin(26, Pin.IN), Pin(27, Pin.OUT),),
#                    model="015D") # esp32 Pin BB

# dlv=dlv_ps.DLV_SPI((Pin("D1", Pin.OUT), Pin("D3", PIN.IN), Pin("D11", Pin.OUT),),
#                    model="015D") # XBEE Pin BB
# XBEE Pin BB is practically useless. Freq 200 Hz, total time 160ms.
# Fastest Pin toggle time 2.5 ms. Other ports are in the range 1-4 µs.

def run(readall=True):

    last_p = None
    last_t = None

    for i in range(1, 1000001):
        try:
            if readall:
                p, t, s = dlv.measure(all=True, cooked=False)
                if last_p is None:
                    print(i, p, 0, t, 0, dlv.psi(p), dlv.celsius(t), s)
                else:
                    print(i, p, last_p - p, t, last_t - t, dlv.psi(p), dlv.celsius(t), s)
                last_t = t
            else:
                p, s = dlv.measure(all=False, cooked=False)
                if last_p is None:
                    print(i, p, 0, dlv.psi(p), s)
                else:
                    print(i, p, last_p - p, dlv.psi(p), s)
            last_p = p
            time.sleep(0.1)
        except RuntimeError:
            print("Runtime Error")
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
        # if input("Next: ") == "q":
            # break

run()
