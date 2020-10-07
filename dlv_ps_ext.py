# The MIT License (MIT)

# (c) 2020 HTW Dresden

# Author: robert-hh

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
#

#
# Sample usage I2C:
#
# from machine import I2C
# from dlv_ps import DLV_I2C
# i2c=I2C(1)
# dlv = DLV_I2C(i2c)
# pressure, temperature, status = dlv.measure()
#
#
# Sample usage SPI interface, S type power mode:
#
# from machine import Pin
#
# from dlv_ps import DLV_SPI
# dlv = DLV_SPI((Pin("D1", Pin.OUT), Pin("D11", Pin.IN), Pin("D3", Pin.OUT),),
#               sleep_mode=True)
# pressure, temperature, status = dlv.measure()
#

import time


class DLV_PS:

    _models = { "005D": ( 5.0 * 2, 8192),
                "015D": (15.0 * 2, 8192),
                "030D": (30.0 * 2, 8192),
                "060D": (60.0 * 2, 8192),
                "005G": ( 5.0, 1638),
                "015G": (15.0, 1638),
                "030G": (30.0, 1638),
                "060G": (60.0, 1638),
                "015A": (15.0, 1638),
                "030A": (30.0, 1638),
              }


    _I2C_ADDRESS = 0x28
    _WAKEUP_TIME = 2  # Wakeup-time from sleep mode


    def __init__(self, model, offset):
        assert model.upper() in self._models.keys(), "Wrong model type"

        self.scaling, self.offset =  self._models[model.upper()] # set defaults
        if offset is not None:
            self.offset = offset
        self.scaling = 1.25 * self.scaling / 16384  # precalulate the coefficient

        self.data = bytearray(4)
        self.data2 = bytearray(2)

        try: ## test for working i2c.start() method
            self.i2c.start()
            self.i2c.stop()
            self.i2c_raw = True
        except:
            self.i2c_raw = False

    def measure(self, all=True, cooked=True):
        self.read_data(all)
        status = (self.data[0] >> 6) & 0x03
        if status == 0b00 or status == 0b10:  # data valid, may be old
            pressure = ((self.data[0] << 8) | self.data[1]) & 0x3FFF
            if cooked:
                pressure = self.psi(pressure)
            if all:
                temperature = (self.data[2] << 3) | ((self.data[3] >> 5) & 0x07)
                if cooked:
                    temperature = self.celsius(temperature)
                return pressure, temperature, status
            else:
                return pressure, status
        else:
            raise RuntimeError("Status: {}".format(status))

#
# convenience functions returning the raw to cooked values; used internally too
#
    def psi(self, pressure):
        return (pressure - self.offset) * self.scaling

    def celsius(self, temperature):
        return temperature * 0.097704 - 50  # 0.097704 = 200 / (2**11 - 1)

    #
    # Some conversion methods; can be removed is space is tight
    #
    def kpascal(self, pressure):
        return pressure * 6.89476

    def mbar(self, pressure):
        return pressure * 68.9476

    def kelvin(self, temperature):
        return temperature + 273.15

    def fahrenheit(self, temperature):
        return temperature * 1.8 + 32

    def lowpass_init(self, value, tau):
        self.value = value
        self.tau = tau

    def lowpass(self, value):
        self.value += self.tau * (value - self.value)
        return self.value

class DLV_I2C(DLV_PS):
    def __init__(self, i2c, model="030G", offset=None, sleep_mode=False):
        assert self._I2C_ADDRESS in i2c.scan(), "Device not accessible"
        self.i2c = i2c
        self.sleep_mode = sleep_mode
        self.address = bytearray(1)
        self.address[0] = (self._I2C_ADDRESS << 1) | 1
        super().__init__(model, offset)

    def read_data(self, all):
        if self.sleep_mode:  # Start cmd only in sleep mode
            if all:
                if self.i2c_raw:  # can do primitive operations
                    self.i2c.start()
                    self.i2c.write(self.address)
                    self.i2c.stop()
                else:
                    try:
                        self.i2c.readfrom(self._I2C_ADDRESS, 1) # cannot read 0 bytes
                    except:
                        pass
            else:
                self.i2c.writeto(self._I2C_ADDRESS, b"")
            time.sleep_ms(self._WAKEUP_TIME)

        if all:
            self.i2c.readfrom_into(self._I2C_ADDRESS, self.data)
        else:
            self.i2c.readfrom_into(self._I2C_ADDRESS, self.data2)
            self.data[0:2] = self.data2


#
# If 2 element tuple of (clock, miso) is supplied, use bit-banging, otherwise
# use the SPI interface.
#
class DLV_SPI(DLV_PS):
    def __init__(self, interface, model="030G", offset=None, sleep_mode=False):
        if len(interface) == 2:
            self.spi, self.cs = interface
            self.cs(1)
            self.has_spi = True
        else:
            self.clock, self.miso, self.cs = interface
            self.clock(0)
            self.cs(1)
            self.has_spi = False
        self.sleep_mode = sleep_mode
        super().__init__(model, offset)

    def read_data(self, all):
        if self.sleep_mode:  # Start cmd only in sleep mode
            self.cs(0)
            time.sleep_us(10)
            self.cs(1)
            time.sleep_ms(self._WAKEUP_TIME)

        if self.has_spi:
            self.cs(0)
            time.sleep_us(10)
            if all:
                self.spi.readinto(self.data)
            else:
                self.spi.readinto(self.data2)
                self.data[0:2] = self.data2
            self.cs(1)
        else:  # SPI by  bitbanging
            self.cs(0)
            time.sleep_us(10)
            for byte in range(4 if all else 2):
                value = 0
                for bit in range(8):
                    self.clock(1)
                    value = (value << 1) | self.miso()
                    time.sleep_us(2)
                    self.clock(0)
                    time.sleep_us(2)
                self.data[byte] = value & 0xFF
            time.sleep_us(2)
            self.cs(1)
