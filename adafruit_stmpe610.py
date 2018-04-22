# The MIT License (MIT)
#
# Copyright (c) 2017 Jerry Needell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_stmpe610`
====================================================

This is a CircuitPython Driver for the STMPE610 Resistive Touch sensor

* Author(s): Jerry Needell
"""

# imports

import time, math
from micropython import const
try:
    import struct
except ImportError:
    import ustruct as struct


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_stmpe610.git"



_STMPE_ADDR = const(0x41)
_STMPE_VERSION = const(0x0811)

STMPE_SYS_CTRL1 = const(0x03)
STMPE_SYS_CTRL1_RESET = const(0x02)
STMPE_SYS_CTRL2 = const(0x04)

STMPE_TSC_CTRL = const(0x40)
STMPE_TSC_CTRL_EN = const(0x01)
STMPE_TSC_CTRL_XYZ = const(0x00)
STMPE_TSC_CTRL_XY = const(0x02)

STMPE_INT_CTRL = const(0x09)
STMPE_INT_CTRL_POL_HIGH = const(0x04)
STMPE_INT_CTRL_POL_LOW = const(0x00)
STMPE_INT_CTRL_EDGE = const(0x02)
STMPE_INT_CTRL_LEVEL = const(0x00)
STMPE_INT_CTRL_ENABLE = const(0x01)
STMPE_INT_CTRL_DISABLE = const(0x00)



STMPE_INT_EN = const(0x0A)
STMPE_INT_EN_TOUCHDET = const(0x01)
STMPE_INT_EN_FIFOTH = const(0x02)
STMPE_INT_EN_FIFOOF = const(0x04)
STMPE_INT_EN_FIFOFULL = const(0x08)
STMPE_INT_EN_FIFOEMPTY = const(0x10)
STMPE_INT_EN_ADC = const(0x40)
STMPE_INT_EN_GPIO = const(0x80)

STMPE_INT_STA = const(0x0B)
STMPE_INT_STA_TOUCHDET = const(0x01)

STMPE_ADC_CTRL1 = const(0x20)
STMPE_ADC_CTRL1_12BIT = const(0x08)
STMPE_ADC_CTRL1_10BIT = const(0x00)

STMPE_ADC_CTRL2 = const(0x21)
STMPE_ADC_CTRL2_1_625MHZ = const(0x00)
STMPE_ADC_CTRL2_3_25MHZ = const(0x01)
STMPE_ADC_CTRL2_6_5MHZ = const(0x02)

STMPE_TSC_CFG = const(0x41)
STMPE_TSC_CFG_1SAMPLE = const(0x00)
STMPE_TSC_CFG_2SAMPLE = const(0x40)
STMPE_TSC_CFG_4SAMPLE = const(0x80)
STMPE_TSC_CFG_8SAMPLE = const(0xC0)
STMPE_TSC_CFG_DELAY_10US = const(0x00)
STMPE_TSC_CFG_DELAY_50US = const(0x08)
STMPE_TSC_CFG_DELAY_100US = const(0x10)
STMPE_TSC_CFG_DELAY_500US = const(0x18)
STMPE_TSC_CFG_DELAY_1MS = const(0x20)
STMPE_TSC_CFG_DELAY_5MS = const(0x28)
STMPE_TSC_CFG_DELAY_10MS = const(0x30)
STMPE_TSC_CFG_DELAY_50MS = const(0x38)
STMPE_TSC_CFG_SETTLE_10US = const(0x00)
STMPE_TSC_CFG_SETTLE_100US = const(0x01)
STMPE_TSC_CFG_SETTLE_500US = const(0x02)
STMPE_TSC_CFG_SETTLE_1MS = const(0x03)
STMPE_TSC_CFG_SETTLE_5MS = const(0x04)
STMPE_TSC_CFG_SETTLE_10MS = const(0x05)
STMPE_TSC_CFG_SETTLE_50MS = const(0x06)
STMPE_TSC_CFG_SETTLE_100MS = const(0x07)

STMPE_FIFO_TH = const(0x4A)

STMPE_FIFO_SIZE = const(0x4C)

STMPE_FIFO_STA = const(0x4B)
STMPE_FIFO_STA_RESET = const(0x01)
STMPE_FIFO_STA_OFLOW = const(0x80)
STMPE_FIFO_STA_FULL = const(0x40)
STMPE_FIFO_STA_EMPTY = const(0x20)
STMPE_FIFO_STA_THTRIG = const(0x10)

STMPE_TSC_I_DRIVE = const(0x58)
STMPE_TSC_I_DRIVE_20MA = const(0x00)
STMPE_TSC_I_DRIVE_50MA = const(0x01)

STMPE_TSC_DATA_X = const(0x4D)
STMPE_TSC_DATA_Y = const(0x4F)
STMPE_TSC_FRACTION_Z = const(0x56)

STMPE_GPIO_SET_PIN = const(0x10)
STMPE_GPIO_CLR_PIN = const(0x11)
STMPE_GPIO_DIR = const(0x13)
STMPE_GPIO_ALT_FUNCT = const(0x17)



class Adafruit_STMPE610:
    """
    A driver for the STMPE610 Resistive Touch sensor.
    """
    def __init__(self):
        """Check the STMPE610 was found"""
        # Check device version.
        version = self.getVersion
        if _STMPE_VERSION != version:
            raise RuntimeError('Failed to find STMPE610! Chip Version 0x%x' % version)
        self._write_register_byte(STMPE_SYS_CTRL1, STMPE_SYS_CTRL1_RESET)
        time.sleep(.001)


        self._write_register_byte(STMPE_SYS_CTRL2, 0x0) # turn on clocks!
        self._write_register_byte(STMPE_TSC_CTRL, STMPE_TSC_CTRL_XYZ | STMPE_TSC_CTRL_EN) # XYZ and enable!
        self._write_register_byte(STMPE_INT_EN, STMPE_INT_EN_TOUCHDET)
        self._write_register_byte(STMPE_ADC_CTRL1, STMPE_ADC_CTRL1_10BIT | (0x6 << 4)) # 96 clocks per conversion
        self._write_register_byte(STMPE_ADC_CTRL2, STMPE_ADC_CTRL2_6_5MHZ)
        self._write_register_byte(STMPE_TSC_CFG, STMPE_TSC_CFG_4SAMPLE | STMPE_TSC_CFG_DELAY_1MS | STMPE_TSC_CFG_SETTLE_5MS)
        self._write_register_byte(STMPE_TSC_FRACTION_Z, 0x6)
        self._write_register_byte(STMPE_FIFO_TH, 1)
        self._write_register_byte(STMPE_FIFO_STA, STMPE_FIFO_STA_RESET)
        self._write_register_byte(STMPE_FIFO_STA, 0)    # unreset
        self._write_register_byte(STMPE_TSC_I_DRIVE, STMPE_TSC_I_DRIVE_50MA)
        self._write_register_byte(STMPE_INT_STA, 0xFF) # reset all ints
        self._write_register_byte(STMPE_INT_CTRL, STMPE_INT_CTRL_POL_HIGH | STMPE_INT_CTRL_ENABLE)

    def readData(self):
        """Request next stored reading - return tuple containing  (x,y,pressure) """
        d1 = self._read_byte(0xD7)
        d2 = self._read_byte(0xD7)
        d3 = self._read_byte(0xD7)
        d4 = self._read_byte(0xD7)
        x = d1 << 4 | d2 >> 4
        y = (d2 & 0xF) << 8 | d3
        z = d4
        # reset all ints  (not sure what this does)
        if self.bufferEmpty:
            self._write_register_byte(STMPE_INT_STA, 0xFF)
        return (x, y, z)

    def _read_byte(self, register):
        """Read a byte register value and return it"""
        return self._read_register(register, 1)[0]


    # pylint: disable=unused-variable
    @property
    def touches(self):
        """
        Returns a list of touchpoint dicts, with 'x' and 'y' containing the
        touch coordinates, and 'pressure'
        """
        touchpoints = []
        (x, y, z) = self.readData()
        point = {'x':x, 'y':y, 'pressure':z}
        touchpoints.append(point)
        return touchpoints
    # pylint: enable=unused-variable


    @property
    def getVersion(self):
        "Read the version number from the sensosr"
        v1 = self._read_byte(0)
        v2 = self._read_byte(1)
        version = v1<<8 | v2
        #print("version ",hex(version))
        return version

    @property
    def touched(self):
        "Report if any touches have been detectd"
        touch = self._read_byte(STMPE_TSC_CTRL)&0x80
        return touch == 0x80


    @property
    def bufferSize(self):
        "The amount of touch data in the buffer"
        return self._read_byte(STMPE_FIFO_SIZE)

    @property
    def bufferEmpty(self):
        "Buffer empty status"
        empty = self._read_byte(STMPE_FIFO_STA) & STMPE_FIFO_STA_EMPTY
        return empty != 0



    @property
    def getPoint(self):
        "Read one touch tuple from the buffer"
        return  self.readData()




class Adafruit_STMPE610_I2C(Adafruit_STMPE610):
    def __init__(self, i2c, address=_STMPE_ADDR):
        """Check the STMPE610 was founnd, Default address is 0x41 but another address can be passed in as an argument"""
        import adafruit_bus_device.i2c_device as i2c_device
        self._i2c = i2c_device.I2CDevice(i2c, address)
        super().__init__()

    def _read_register(self, register, length):
        """Low level register reading over I2C, returns a list of values"""
        with self._i2c as i2c:
            i2c.write(bytearray([register & 0xFF]))
            result = bytearray(length)
            i2c.readinto(result)
            #print("$%02X => %s" % (register, [hex(i) for i in result]))
            return result

    def _write_register_byte(self, register, value):
        """Low level register writing over I2C, writes one 8-bit value"""
        with self._i2c as i2c:
            i2c.write(bytes([register & 0xFF, value & 0xFF]))
            #print("$%02X <= 0x%02X" % (register, value))

class Adafruit_STMPE610_SPI(Adafruit_STMPE610):
    def __init__(self, spi, cs, baudrate=100000):
        """Check the STMPE610 was found,Default clock rate is 100000 but can be changed with 'baudrate'"""
        import adafruit_bus_device.spi_device as spi_device
        self._spi = spi_device.SPIDevice(spi, cs, baudrate=baudrate)
        super().__init__()

    def _read_register(self, register, length):
        """Low level register reading over SPI, returns a list of values"""
        register = (register | 0x80) & 0xFF  # Read single, bit 7 high.
        with self._spi as spi:
            spi.write(bytearray([register]))
            result = bytearray(length)
            spi.readinto(result)
#            print("$%02X => %s" % (register, [hex(i) for i in result]))
            return result

    def _write_register_byte(self, register, value):
        """Low level register writing over SPI, writes one 8-bit value"""
        register &= 0x7F  # Write, bit 7 low.
        with self._spi as spi:
            spi.write(bytes([register, value & 0xFF]))


