# -*- coding: utf-8 -*-

"""
Interface file for simple data acquisition.

"""

from abc import abstractmethod
from qudi.core.module import Base


class SimpleDataInterface(Base):
    """ An interface to get read one or multiple values from a device.

    Deprecated : This interface is redundant with process_interface. Please use the other if possible?
    TODO: Remove in future versions ?
    """

    @abstractmethod
    def getData(self):
        """ Return a measured value """
        pass

    @abstractmethod
    def getChannels(self):
        """ Return number of channels for value """
        pass
