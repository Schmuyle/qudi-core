# -*- coding: utf-8 -*-
"""
Interface file for Hameg power supply

"""

from enum import Enum
import abc
from qudi.core.module import Base



class SimplerRigolInterface(Base):
    _modtype = 'SimpleRigolInterface'
    _modclass = 'interface'


 

    @abc.abstractmethod
    def set_ch1_voltage(self, voltage):
        """ Set channel to Vpp voltage
        """
        pass
