# -*- coding: utf-8 -*-
""" Interface file for RedPitaya IQ demodulator and scope."""
from abc import abstractmethod
from qudi.core.module import Base

class SimpleRedPitayaInterface(Base):
    """ This interface controls a RedPitaya IQ demodulator and scope. """

# -------- IQ0 get methods --------

    @abstractmethod
    def get_iq0_frequency(self):
        """ Get IQ0 demodulator frequency. """
        pass

    @abstractmethod
    def get_iq0_phase(self):
        """ Get IQ0 demodulator phase. """
        pass

    @abstractmethod
    def get_iq0_amplitude(self):
        """ Get IQ0 demodulator amplitude. """
        pass

    @abstractmethod
    def get_iq0_gain(self):
        """ Get IQ0 demodulator gain. """
        pass

    @abstractmethod
    def get_iq0_input(self):
        """ Get IQ0 demodulator input signal. """
        pass

    @abstractmethod
    def get_iq0_output_signal(self):
        """ Get IQ0 demodulator output signal. """
        pass

    @abstractmethod
    def get_iq0_modulation_at_2f(self):
        """ Get whether IQ0 modulation at 2f is enabled. """
        pass

    @abstractmethod
    def get_iq0_filter_frequency(self):
        """ Get the IQ0 bandpass filter frequency. """
        pass

# -------- IQ0 set methods --------

    @abstractmethod
    def set_iq0_frequency(self, frequency):
        """ Set IQ demodulator frequency. """
        pass

    @abstractmethod
    def set_iq0_phase(self, phase):
        """ Set IQ0 demodulator phase. """
        pass

    @abstractmethod
    def set_iq0_amplitude(self, amplitude):
        """ Set IQ0 demodulator amplitude. """
        pass

    @abstractmethod
    def set_iq0_gain(self, gain):
        """ Set IQ0 demodulator gain. """
        pass

    @abstractmethod
    def set_iq0_input(self, input_signal):
        """ Set IQ0 demodulator input signal. """
        pass

    @abstractmethod
    def set_iq0_modulation_at_2f(self, enabled):
        """ Set whether IQ0 modulation at 2f is enabled. """
        pass

    @abstractmethod
    def set_iq0_filter_frequency(self, frequency):
        """ Set the IQ0 bandpass filter frequency. """
        pass

    @abstractmethod
    def get_iq0_pid_p(self):
        """ Get the proportional gain of the PID connected to IQ0. """
        pass

    @abstractmethod
    def set_iq0_pid_p(self, gain):
        """ Set the proportional gain of the PID connected to IQ0. """
        pass
    
 
# -------- IQ1 get methods --------

    @abstractmethod
    def get_iq1_frequency(self):
        """ Get IQ1 demodulator frequency. """
        pass

    @abstractmethod
    def get_iq1_phase(self):
        """ Get IQ1 demodulator phase. """
        pass

    @abstractmethod
    def get_iq1_amplitude(self):
        """ Get IQ1 demodulator amplitude. """
        pass

    @abstractmethod
    def get_iq1_gain(self):
        """ Get IQ1 demodulator gain. """
        pass

    @abstractmethod
    def get_iq1_input(self):
        """ Get IQ1 demodulator input signal. """
        pass

    @abstractmethod
    def get_iq1_output_signal(self):
        """ Get IQ1 demodulator output signal. """
        pass

    @abstractmethod
    def get_iq1_modulation_at_2f(self):
        """ Get whether IQ1 modulation at 2f is enabled. """
        pass

    @abstractmethod
    def get_iq1_filter_frequency(self):
        """ Get the IQ1 bandpass filter frequency. """
        pass

# -------- IQ1 set methods --------

    @abstractmethod
    def set_iq1_frequency(self, frequency):
        """ Set IQ1 demodulator frequency. """
        pass

    @abstractmethod
    def set_iq1_phase(self, phase):
        """ Set IQ1 demodulator phase. """
        pass

    @abstractmethod
    def set_iq1_amplitude(self, amplitude):
        """ Set IQ1 demodulator amplitude. """
        pass

    @abstractmethod
    def set_iq1_gain(self, gain):
        """ Set IQ1 demodulator gain. """
        pass

    @abstractmethod
    def set_iq1_input(self, input_signal):
        """ Set IQ1 demodulator input signal. """
        pass

    @abstractmethod
    def set_iq1_modulation_at_2f(self, enabled):
        """ Set whether IQ1 modulation at 2f is enabled. """
        pass

    @abstractmethod
    def set_iq1_filter_frequency(self, frequency):
        """ Set the IQ1 bandpass filter frequency. """
        pass

    @abstractmethod
    def get_iq1_pid_p(self):
        """ Get the proportional gain of the PID connected to IQ1. """
        pass

    @abstractmethod
    def set_iq1_pid_p(self, gain):
        """ Set the proportional gain of the PID connected to IQ1. """
        pass
    
# ------ Scope methods --------


    @abstractmethod
    def set_scope_duration(self, duration):
        """ Set scope acquisition window duration. """
        pass

    @abstractmethod
    def get_scope_duration(self):
        """ Get scope acquisition window duration. """
        pass

    @abstractmethod
    def set_scope_input1(self, input_source):
        """ Set scope channel 1 input source. """
        pass

    @abstractmethod
    def get_scope_input1(self):
        """ Get scope channel 1 input source. """
        pass

    @abstractmethod
    def set_scope_input2(self, input_source):
        """ Set scope channel 2 input source. """
        pass

    @abstractmethod
    def get_scope_input2(self):
        """ Get scope channel 2 input source. """
        pass

    @abstractmethod
    def apply_scope_setup(self, **kwargs):
        """Apply scope configuration atomically.
        
        Supported kwargs: duration, input1, input2, trigger_source, threshold, trigger_delay
        """
        pass

    @abstractmethod
    def get_scope_trigger_sources(self):
        """Get supported scope trigger sources."""
        pass

    @abstractmethod
    def get_scope_trigger_source(self):
        """Get currently selected scope trigger source."""
        pass

    @abstractmethod
    def get_scope_threshold(self):
        """Get current scope trigger threshold."""
        pass

    @abstractmethod
    def get_scope_data(self):
        """ Get current scope data. """
        pass

# ------- Make a set of AWG generator settings here -----