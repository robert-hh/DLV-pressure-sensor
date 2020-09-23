# DLV_PS: Python class for the AllSensors DLV pressure sensors

The pressure sensors DLV-xxxx come in a wide range of configurations concerning
both the range, the supported communication interface and the measuring time.
Even if both SPI and I2C are supported, only the I2C type seems to be on general sale.

This class comes in two variants. A basic variant, which supports
the I2C interface only. The extended version supports both I2C and SPI 
(however only tested against a simulation) as well as an option 
specifying wether the device is configured for sleep mode.

Both variants allow specifying the range of the various models.

## **Constructors**

### **dlv = DLV_I2C(i2c, \*, model="030G", offset=None) # Basic Version I2C**
### **dlv = DLV_I2C(i2c, \*, model="030G", offset=None, sleep_mode=False) # Extended Version I2C**
### **dlv = DLV_SPI((spi, cs,), \*, offset=None, model="030G", sleep_mode=False) # Extended Version SPI**
### **dlv = DLV_SPI((clock, miso, cs,), offset=None, \*, model="030G", sleep_mode=False) # Extended Version SPI**

Arguments: 

- i2c: an I2C object which has to be created by the caller with a freq (baudrate) between 100kHz and 400kHz. 
- model: a string with the xxxx part of the DLV pressure sensor. For the DLV-030G 
this is for instance the string "030G". The following sensor models will be
accepted: "005D", "015D", "030D", "060D", "005G", "015G", "030G", "060G",
"015A", and "030A". The parameters for deriving the psi value from the
raw sensor reading are derived by the driver from the model number. Default value: "030G" 
- the value to be subtracted from the pressure sensor's raw reading. The default value
is 8192 for differential sensors and 1638 for the others. For a more precise value
determine the raw reading with no pressure applied to the sensor (open pipes), except 
for the A models.

The parameters below are only supported by the extended version of the driver 

- sleep_mode: a boolean telling whether the sensor is configured for 
sleep mode. This is applies if last character of the model number is 'S'. Default value: False
- (spi, cs,): a tuple consisting of an spi object and a Pin object. The spi
object has to be created upfront with a freq (baudrate) between 50kHz and 800kHz resp. 200 kHz (L type models)
- (clock, miso, cs,): a tuple of three pin objects used for the SPI communication
in bitbanging mode. The driver sets the pin modes as required. 
The pins clock and cs must be OUT capable, miso must be IN capable. 

There is no specific support for the power and speed modes 'F', 'N' and 'L',
as these only differ in the conversion time. The calling code must take care
of requesting values not too fast. Conversion times according to the data sheet are:

|Mode|Min|Max|Unit|
|:---:|:---:|:---:|:---:|
|F|0.4|1|ms|
|N|1.3|3.1|ms|
|L|6.5|9.5|ms|  


## **Methods**

### **pressure, temperature, status = dlv.measure(all=True, cooked=True)**
### **pressure, status = dlv.measure(all=False, cooked=True)**

Get tuple of pressure, temperature and status or pressure and status, depending
on the value of the parameter 'all'. The pressure is given in psi, the temperature is
given in degree Celsius, if the argument cooked is True. Status tells,
wether the values a new or stale:

- 0: This is an actual set of values
- 2: This is a stale set of values from a previous measuring cycle

If the measurement fails, a RuntimeError exception is raised with the status code. 

Arguments: 

- all: If True, return pressure and temperature, if False, return pressure only. Default value: True
- cooked: If True, return the psi and celsius sensor values. If False, return the raw sensor readings for pressure and temperature. Default value: True

### **psi_value = dlv.psi(raw_pressure)**

Convert a raw sensor value into the psi value, taking into account the offset and range of the sensor.
    
### **celsius_value = dlv.celsius(raw_temperature)**

Convert a raw sensor value into the degree celsius value.


## **Convenience methods**

Below are a few convenience methods, which can also be removed from the
driver is the memory is tight.

### **kpascal = dlv.kpascal(psi)**

Convert the supplied psi pressure value into a kPascal value.

### **mbar = dlv.mbar(psi)**

Convert the supplied psi pressure value into a millibar value.

### **kelvin = dlv.kelvin(celsius)**

Convert the supplied celsius temperature value into a degree Kelvin value.

### **fahrenheit = dlv.fahrenheit(celsius)**

Convert the supplied celsius temperature value into a degree Fahrenheit value.

## **Test coverage**

The basic and extended drivers were successfully tested with:

- XBEE 3, I2C interface, DIGI micropython
- Pyboard D, Soft I2C interface, genuine Micropython
- Pyboard D, Hard I2C interface, genuine Micropython
- ESP32, Soft I2C interface, genuine Micropython
- ESP32, SPI interface (sensor simulation), genuine Micropython
- ESP32, Pin bitbang interface (sensor simulation), genuine Micropython
- ESP8266, I2C interface, genuine Micropython
- W600, Hard I2C interface, WinnerMicro adaption of genuine Micropython
- W600, Soft I2C interface, WinnerMicro adaption of genuine Micropython
- LoPy4, Soft I2C interface, Pycom Micropython
- LoPy4, Hard I2C interface, Pycom Micropython
- Teensy 4.0, Circuitpython (only dlv_ps.py)

The pin bitbang method for XBEE 3 creates proper signals, but is way too slow to
be usesful. The data tranfer takes 160ms at the fastest achievable clock frequency
of 200Hz (!) compared to 60µs with I2C and ~400kHz.

The pin bitbang interface was not tested on Pyboard, ESP8266 and W600. These should
work the same way as on the ESP32, and are not needed, since all these boards support
genuine SPI. The Hardware SPI on ESP32 did not work at all

A long run test was made with the sensor, capturin 1 million samples over 13 hours. There
were no false readings and a small amount of noise equivalent to 1-2 bits. In the test
range of values, about every 4th code was missing, 1444 of 5646. Of the
high order 13 bits, 32 codes were missing. Of the 12 bits values all codes were present.




## **Examples**

```
#
# Sample usage I2C, returning the data as psi and celsius:
#
from machine import I2C
from dlv_ps import DLV_I2C

i2c=I2C(1)
dlv = DLV_I2C(i2c)

pressure, temperature, status = dlv.measure(offset=1663)
```

```
#
# Sample usage I2C with raw modes
#
from machine import I2C
from dlv_ps import DLV_I2C

i2c=I2C(1)
dlv = DLV_I2C(i2c)

pressure, temperature, status = dlv.measure(cooked=False)
psi = dlv.psi(pressure)
celsius = dlv.celsius(temperature)
```

```
#
#
# Sample usage SPI interface and sleep mode:
#
from machine import Pin, SPI
from dlv_ps_ext import dlv_ps

spi =SPI(-1, baudrate=10000, sck=Pin(25), miso=Pin(26), mosi=Pin(4), polarity=0, phase=0)
dlv=dlv_ps.DLV_SPI((spi, Pin(27),), model="015D") # esp32 Soft SPI
pressure, temperature, status = dlv.measure()
#
```

## **Files**

- **dlv_ps.py**: Sensor driver supporting the I2C interface and speed/power modes 'F', 'N', and 'L'.
- **dlv_ps_ext.py**: Sensor driver intended for supporting both I2C and SPI interface as well as all four speed/power modes. Due to lack of availibility of sensors with either SPI interface or 'S' speed mode, SPI and sleep_mode were tested only against a simulation.
- **dlvtest.py**: Short test script creating the output used for the long run and missing codes test.
- **histogram.py**: Analysis script for the test output of dlvtest.py. It will calulate the frequency of differences in the raw data and count the missing codes in the raw data.
- **spisimul.py**: SPI simulation used for testing. This simulation script 
is made for a Pyboard.
