# -*- coding: utf-8 -*-
"""
Interface file for vacuum turbopumps with prepumps and pressure sensors.

"""

from abc import abstractmethod
from qudi.core.module import Base


class VacuumPumpInterface(Base):
    """ This interface can be used to control a vacuum pump.

    This interface, while functional, is not used by any hardware nor logic at the moment.
    Also it has no dummy associated with it.

    TODO: Improve documentation - Some methods are not crystal clear and no hardwre/logic to infer from.

    """

    @abstractmethod
    def get_extra_info(self):
        """ Present extra information about pump controller/device.

          @return str: arbitrary information about pump, like model nr, hardware version, firmware version
        """
        pass

    @abstractmethod
    def get_pressures(self):
        """All available pressures in Pascal.

          @return dict: dict of gauge name and pressure
        """
        pass

    @abstractmethod
    def get_pump_speeds(self):
        pass

    @abstractmethod
    def get_pump_powers(self):
        """ All available pump powers in watts.

          @return dict: dict of pump name and pump power
        """
        pass

    @abstractmethod
    def get_pump_states(self):
        """All available pump states.

          @return dict: dict of pump name and pump state
        """
        pass

    @abstractmethod
    def set_pump_states(self, states):
        """Control the pump state.
          @param dict states: dict of pump name and desired state
        """
        pass

    @abstractmethod
    def get_system_state(self):
        """Get overall system state.
        """
        pass

    @abstractmethod
    def set_system_state(self, state):
        """Control the system state.
        """
        pass

