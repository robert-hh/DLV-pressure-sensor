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
import dlv_ps_min as dlv_ps

from machine import I2C
i2c=I2C(1)  ## ESP32 Hard

dlv=dlv_ps.DLV_I2C(i2c, offset=8192)

def run():

    for i in range(1, 100001):
        try:
            p, s = dlv.mbar()
            print(i, p, s)
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as err:
            print("Error: ", err)
            time.sleep(0.1)
        # if input("Next: ") == "q":
            # break

run()
