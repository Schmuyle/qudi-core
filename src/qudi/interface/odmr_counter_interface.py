# -*- coding: utf-8 -*-
"""
This file contains the Qudi Interface file for ODMRCounter.

"""

from abc import abstractmethod
from qudi.core.module import Base


class ODMRCounterInterface(Base):
    """ This is the Interface class supplies the controls for a simple ODMR."""

    @abstractmethod
    def set_up_odmr_clock(self, clock_frequency=None, clock_channel=None):
        """ Configures the hardware clock of the NiDAQ card to give the timing.

        @param float clock_frequency: if defined, this sets the frequency of the
                                      clock
        @param str clock_channel: if defined, this is the physical channel of
                                  the clock

        @return int: error code (0:OK, -1:error)
        """
        pass

    @abstractmethod
    def set_up_odmr(self, counter_channel=None, photon_source=None,
                    clock_channel=None, odmr_trigger_channel=None):
        """ Configures the actual counter with a given clock.

        @param str counter_channel: if defined, this is the physical channel of
                                    the counter
        @param str photon_source: if defined, this is the physical channel where
                                  the photons are to count from
        @param str clock_channel: if defined, this specifies the clock for the
                                  counter
        @param str odmr_trigger_channel: if defined, this specifies the trigger
                                         output for the microwave

        @return int: error code (0:OK, -1:error)
        """
        pass

    @abstractmethod
    def set_odmr_length(self, length=100):
        """Set up the trigger sequence for the ODMR and the triggered microwave.

        @param int length: length of microwave sweep in pixel

        @return int: error code (0:OK, -1:error)
        """
        pass

    @abstractmethod
    def count_odmr(self, length = 100):
        """ Sweeps the microwave and returns the counts on that sweep.

        @param int length: length of microwave sweep in pixel

        @return (bool, float[]): tuple: was there an error, the photon counts per second
        """
        pass

    @abstractmethod
    def close_odmr(self):
        """ Close the odmr and clean up afterwards.

        @return int: error code (0:OK, -1:error)
        """
        pass

    @abstractmethod
    def close_odmr_clock(self):
        """ Close the odmr and clean up afterwards.

        @return int: error code (0:OK, -1:error)
        """
        pass

    @abstractmethod
    def get_odmr_channels(self):
        """ Return a list of channel names.

        @return list(str): channels recorded during ODMR measurement
        """
        pass

    @property
    @abstractmethod
    def oversampling(self):
        pass

    @oversampling.setter
    @abstractmethod
    def oversampling(self, val):
        pass

    @property
    @abstractmethod
    def lock_in_active(self):
        pass

    @lock_in_active.setter
    @abstractmethod
    def lock_in_active(self, val):
        pass
