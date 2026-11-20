# -*- coding: utf-8 -*-
"""
A hardware module for acessing the Measurement Systems TSYS01 temperature
sensor chip via SPI.

"""

from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.process_interface import ProcessInterface
from qudi.util.mutex import Mutex

import spidev
import struct
import time


class TSYS01SPI(ProcessInterface):
    """ Measurement Systems TSYS01 temperature sensor.

    Example config for copy-paste:

    temp_tsys:
        module.Class: 'tsys01_spi.TSYS01SPI'
        bus: 0
        device: 0

    """
    # config opts
    bus = ConfigOption('bus', default=0, missing='warn')
    device = ConfigOption('device', default=0, missing='warn')

    # commands to chip (constants)
    READ_ADC  = 0x00
    RESET     = 0x1E
    START_ADC = 0x48
    READ_ROM0 = 0xA0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #locking for thread safety
        self.threadlock = Mutex()

    def on_activate(self):
        """ Activate module.
        """
        self.rom = []
        self.spi = spidev.SpiDev()
        self.spi.open(self.bus, self.device)
        self.reset()
        self.readROM()

    def on_deactivate(self):
        """ Deactivate module.
        """
        self.spi.close()

    def diag(self):
        """ SPI bus diagnostic output.
        """
        print('==== SPI Diagnostics ====')
        print('Bits per word: {0:>10}'.format(self.spi.bits_per_word))
        print('CS is active high: {0!s:>6}'.format(self.spi.cshigh))
        print('Loopback: {0!s:>15}'.format(self.spi.loop))
        print('LSB first: {0!s:>14}'.format(self.spi.lsbfirst))
        print('Max clock speed: {0:>8}'.format(self.spi.max_speed_hz))
        print('Clock mode: {0:>13}'.format(self.spi.mode))
        print('SI/SO shared: {0!s:>11}'.format(self.spi.threewire))
        print('=========================')

    def reset(self):
        """ Reset the sensor chip.
        """
        rbuf = self.spi.xfer( [self.RESET], 8000, 3000 )
        time.sleep(0.003)

    def readRomAddr(self, addr):
        """ Read a 16bit rom address.

            @param int addr: momory address to read
            @return int: 16bit contents of rom at address
        """
        bytes_to_read = self.READ_ROM0 | 0x0F & ( addr << 1)
        rbuf = self.spi.xfer( [bytes_to_read, 0x00, 0x00] )
        return 2**8*rbuf[1] + rbuf[2]

    def readROM(self):
        """ Read the whole device ROM.

            @return list(int): contents of all 8 ROM registers
        """
        self.rom = []
        for i in range(8):
            self.rom.append(self.readRomAddr(i))

    def startADC(self):
        """ Start the temperature sensor ADC.
        """
        try:
            rbuf = self.spi.xfer([self.START_ADC])
        except OSError:
            pass
        time.sleep(0.010)

    def readADC(self):
        """ Read value from the ADC.

            @return int: raw ADC value
        """
        rbuf = self.spi.xfer([self.READ_ADC, 0x00, 0x00, 0x00] )
        return struct.unpack('>I', b'\0' + bytes(rbuf[1:]))[0]

    def temperatureCelsius(self, adcValue):
        """ Convert ADC value to degrees Celsius.

            @param int adcValue: raw ADC value

            @return float: temperature in degrees Celsius
        """
        if len(self.rom) < 8:
            self.readROM()
        adc16 = adcValue / 2**8
        return (-2.0 * self.rom[1] * 10**-21 * adc16**4
              +  4.0 * self.rom[2] * 10**-16 * adc16**3
              + -2.0 * self.rom[3] * 10**-11 * adc16**2
              +  1.0 * self.rom[4] * 10**-6  * adc16
              + -1.5 * self.rom[5] * 10**-2 )

    def temperatureKelvin(self, adcValue):
        """ Convert ADC value to Kelvin.

            @param int adcValue: raw ADC value

            @return float: temperature in Kelvin
        """
        return 273.15 + self.temperatureCelsius(adcValue)

    def get_process_value(self):
        """ Read ADC and return emperature in Kelvin.

            @return float: current temperature in Kelvin
        """
        with self.threadlock:
            self.startADC()
            return self.temperatureKelvin(self.readADC())

    def get_process_unit(self):
        """ Return Process unit, here Kelvin.

            @return tuple(str, str): short and text form of process unit
        """
        return 'K', 'kelvin'
