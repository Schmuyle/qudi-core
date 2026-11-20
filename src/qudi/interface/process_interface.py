# -*- coding: utf-8 -*-

"""
Interface file to use processes.

"""

from abc import abstractmethod
from qudi.core.module import Base


class ProcessInterface(Base):
    """ A simple interface to measure one or multiple value(s).

    This interface is in fact a very general/universal interface that can be used for a lot of things.
    It can be used to interface any hardware where one to simply read one or multiple process value, like a temperature
    sensor or much coffee there is in the coffee machine.

    """

    @abstractmethod
    def get_process_value(self, channel=None):
        """ Return a measured value

        @param (int) channel: (Optional) The number of the channel
        @return (float): The measured process value
        """
        pass

    @abstractmethod
    def get_process_unit(self, channel=None):
        """ Return the unit that the value is measured in as a tuple of ('abbreviation', 'full unit name')

        @param (int) channel: (Optional) The number of the channel

        @return: The unit as a tuple of ('abbreviation', 'full unit name')

         """
        pass

    def process_supports_multiple_channels(self):
        """ Function to test if hardware support multiple channels

        @return (bool): Whether the hardware supports multiple channels

        This function is not abstract - Thus it is optional and if a hardware do not implement it, the answer is False.
        """
        return False

    def process_get_number_channels(self):
        """ Function to get the number of channels available for measure

        @return (int): The number of channel(s)

        This function is not abstract - Thus it is optional and if a hardware do not implement it, the answer is 1.
        """
        return 1
