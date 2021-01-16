# DLV_PS: Minmal Python class for the AllSensors DLV pressure sensors

The pressure sensors DLV-xxxx come in a wide range of configurations concerning
both the range, the supported communication interface and the measuring time.
Even if both SPI and I2C are supported, only the I2C type seems to be on general sale.

This is the minimal version of the driver, supporting only one method and
the I2C interface only.
## **Constructor**

### **dlv = DLV_I2C(i2c, \*, range=30, offset=1638) # Basic Version I2C**

Arguments: 

- i2c: an I2C object which has to be created by the caller with a freq (baud rate) between 100kHz and 400kHz. 
- range: the full PSI range of the sensor. The default is 30
- offset: the value to be subtracted from the pressure sensor's raw reading. The default is 1638

The table below shows the range and offset values for the various models
|Model|Range|Offset|
|:---:|:---:|:---:|
|005G|6|1638|
|015G|15|1638|
|030G|30|1638|
|060G|60|1638|
|015A|15|1638|
|030A|30|1638|
|005D|10|8192|
|015D|30|8192|
|030D|60|8192|
|060D|120|8192| 

There is no specific support for the power and speed modes 'F', 'N' and 'L',
as these only differ in the conversion time. The calling code must take care
of requesting values not too early. Conversion times according to the data sheet are:

|Mode|Min|Max|Unit|
|:---:|:---:|:---:|:---:|
|F|0.4|1|ms|
|N|1.3|3.1|ms|
|L|6.5|9.5|ms| 

## **Method**

### **pressure, status = dlv.mbar()**

Get tuple of pressure and status, depending. The pressure is given in mbar. Status tells,
whether the values a new or stale:

- 0: This is an actual set of values
- 2: This is a stale set of values from a previous measuring cycle

If the measurement fails, a RuntimeError exception is raised with the status code. 

## **Example**

```
#
# Sample usage I2C, returning the data as PSI and Celsius:
#
from machine import I2C
from dlv_ps_min import DLV_I2C

i2c=I2C(1)
dlv = DLV_I2C(i2c)

pressure, status = dlv.mbar()
```

## **Files**

- **dlv_ps_min.py**: Sensor driver supporting the I2C interface and speed/power modes 'F', 'N', and 'L'.
- **dlvtest_min.py**: Short test script creating the output used for the long run and missing codes test.

