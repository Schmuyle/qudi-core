# -*- coding: utf-8 -*-

"""
This file contains the Qudi Interface file for control wavemeter hardware.

"""

from abc import abstractmethod
from qudi.core.module import Base


class WavemeterInterface(Base):
    """ Define the controls for a wavemeter hardware.

    Note: This interface is very similar in feature with slow counter
    """

    @abstractmethod
    def start_acqusition(self):
        """ Method to start the wavemeter software.

        @return (int): error code (0:OK, -1:error)

        Also the actual threaded method for getting the current wavemeter
        reading is started.
        """
        pass

    @abstractmethod
    def stop_acqusition(self):
        """ Stops the Wavemeter from measuring and kills the thread that queries the data.

        @return (int): error code (0:OK, -1:error)
        """
        pass

    @abstractmethod
    def get_current_wavelength(self, kind="air"):
        """ This method returns the current wavelength.

        @param (str) kind: can either be "air" or "vac" for the wavelength in air or vacuum, respectively.

        @return (float): wavelength (or negative value for errors)
        """
        pass

    @abstractmethod
    def get_current_wavelength2(self, kind="air"):
        """ This method returns the current wavelength of the second input channel.

        @param (str) kind: can either be "air" or "vac" for the wavelength in air or vacuum, respectively.

        @return float: wavelength (or negative value for errors)
        """
        pass

    @abstractmethod
    def get_timing(self):
        """ Get the timing of the internal measurement thread.

        @return (float): clock length in second
        """
        pass

    @abstractmethod
    def set_timing(self, timing):
        """ Set the timing of the internal measurement thread.

        @param (float) timing: clock length in second

        @return (int): error code (0:OK, -1:error)
        """
        pass
