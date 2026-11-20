# -*- coding: utf-8 -*-
"""
Simple data acquisition from serial port.

"""

import visa

from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.simple_data_interface import SimpleDataInterface


class SimpleAcq(SimpleDataInterface):
    """ Read human readable numbers from serial port.

    Example config for copy-paste:

    simple_data_acq:
        module.Class: 'simple_data_acq.SimpleAcq'
        interface: 'ASRL1::INSTR'
        baudrate: 115200

    """
    resource = ConfigOption('interface', 'ASRL1::INSTR', missing='warn')
    baudrate = ConfigOption('baudrate', 115200, missing='warn')

    def on_activate(self):
        """ Activate module.
        """
        self.rm = visa.ResourceManager()
        self.log.debug('Resources: {0}'.format(self.rm.list_resources()))
        self.my_instrument = self.rm.open_resource(self.resource, baud_rate=self.baudrate)

    def on_deactivate(self):
        """ Deactivate module.
        """
        self.my_instrument.close()
        self.rm.close()

    def getData(self):
        """ Read one value from serial port.

            @return int: vaue form serial port
        """
        try:
            return int(self.my_instrument.read_raw().decode('utf-8').rstrip().split()[1])
        except:
            return 0

    def getChannels(self):
        """ Number of channels.

            @return int: number of channels
        """
        return 1
