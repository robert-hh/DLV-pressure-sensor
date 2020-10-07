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
# from dlv_ps_min import DLV_I2C
# i2c=I2C(1)
# dlv = DLV_I2C(i2c)
# mbar, status = dlv.mbar()
#

class DLV_I2C:

    _I2C_ADDRESS = const(0x28)

    def __init__(self, i2c, range=30, offset=1638):
        self.i2c = i2c
        self.offset = offset
        self.scaling = 0.005260284 * range  # 0.005260284 = 1.25 * 68.9476 / 16384
        self.data = bytearray(2)

    def mbar(self):
        self.i2c.readfrom_into(_I2C_ADDRESS, self.data)
        status = (self.data[0] >> 6) & 0x03
        if status == 0b00 or status == 0b10:  # 0b00: new data, 0b10: old data
            return ((((self.data[0] << 8) | self.data[1]) & 0x3FFF) - self.offset) * self.scaling, status
        raise RuntimeError("Status: {}".format(status))
