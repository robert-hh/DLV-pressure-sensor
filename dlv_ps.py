#
# Driver for the DLV-xxx pressure sensor family
#
#
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
# pressure, temperature = dlv.measure()
#



class DLV_I2C:

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

    def __init__(self, i2c, model="030G", offset=None):
        assert self._I2C_ADDRESS in i2c.scan(), "Device not accessible"
        assert model.upper() in self._models.keys(), "Wrong model type"

        self.i2c = i2c

        self.scaling, self.offset =  self._models[model.upper()] # set defaults
        if offset is not None:
            self.offset = offset
        self.scaling = 1.25 * self.scaling / 16384  # precalulate the coefficients
        self.offset *= self.scaling

        self.data = bytearray(4)
        self.data2 = bytearray(2)

        self.value = 0
        self.tau = 0.1

    def _get_pressure(self, data, cooked):
        pressure = ((data[0] << 8) | data[1]) & 0x3FFF
        if cooked:
            return self.psi(pressure)
        else:
            return pressure

    def measure(self, all=True, cooked=True):
        if all:
            self.i2c.readfrom_into(self._I2C_ADDRESS, self.data)
            status = (self.data[0] >> 6) & 0x03
            if status == 0b00 or status == 0b10:  # data valid, may be old
                temperature = (self.data[2] << 3) | ((self.data[3] >> 5) & 0x07)
                if cooked:
                    temperature = self.celsius(temperature)
                return self._get_pressure(self.data, cooked), temperature, status
        else:
            self.i2c.readfrom_into(self._I2C_ADDRESS, self.data2)
            status = (self.data[0] >> 6) & 0x03
            if status == 0b00 or status == 0b10:  # data valid, may be old
                return self._get_pressure(self.data2, cooked), status

        raise RuntimeError("Status: {}".format(status))
#
# convenience functions returning the raw to cooked values; used internally too
#
    def psi(self, pressure):
        return pressure * self.scaling - self.offset

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