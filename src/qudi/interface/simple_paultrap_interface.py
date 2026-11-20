from abc import abstractmethod
from qudi.core.module import Base

class SimplePaulTrapInterface(Base):
    @property
    @abstractmethod
    def set_voltage(self, voltage):
        """ Set power supply channel voltage. """
        pass

    @abstractmethod
    def set_voltage(self, voltage):
        """ Set power supply channel voltage. """
        pass
        
        
    @abstractmethod
    def set_frequency(self, freq):
        """ Set power supply channel voltage. """
        pass
        
    @abstractmethod
    def enable_HV(self, state):
        """ Set power supply channel voltage. """
        pass

        
    @abstractmethod
    def get_voltage(self):
        """ measured channel voltage. """
        pass

    @abstractmethod
    def get_frequency(self):
        """ measured channel voltage. """
        pass
        
        
    @abstractmethod
    def get_state(self):
        """ measured channel voltage. """
        pass
        

