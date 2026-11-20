# -*- coding: utf-8 -*-
"""
Interface file for lasers where current and power can be set.

"""

from enum import Enum
from abc import abstractmethod
from qudi.core.module import Base



class SimpleXeryonInterface(Base):
    _modtype = 'SimpleXeryonInterface'
    _modclass = 'interface'
    """ This interface can be used to control a simple laser. It handles power control, control modes and shutter states

    This interface is useful for a standard, fixed wavelength laser that you can find in a lab.
    It handles power control via constant power or constant current mode, a shutter state if the hardware has a shutter
    and a temperature regulation control.

    """

    

        
    
