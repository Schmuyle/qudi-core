# -*- coding: utf-8 -*-
"""
Interface for logging small amounts of time series data to some place.
First use case is Influxdb.

"""

from abc import abstractmethod
from qudi.core.module import Base


class DataLoggerInterface(Base):
    """

    TODO: This interface has no documentation nor dummy module or logic :'(
    """

    @abstractmethod
    def get_log_channels(self):
        pass

    @abstractmethod
    def set_log_channels(self, channelspec):
        pass

    @abstractmethod
    def log_to_channel(self, channel, value):
        pass

