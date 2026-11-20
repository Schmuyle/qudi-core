""" Logic module for RedPitaya control. Contains methods for all aspects of the RedPitaya instrument, including IQ demodulator, scope control and input selection. """

import time
import numpy as np
from qtpy import QtCore

from qudi.core.module import LogicBase

from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption


class RedPitayaIQLogic(LogicBase):
    """ Logic module for RedPitaya control. """
    _modclass = 'redpitaya_IQ_logic'
    _modtype = 'logic'

    # Connector to RedPitaya hardware
    redpitaya_hw = Connector(interface='SimpleRedPitayaInterface')
        
    # Signals for IQ Channel 1
    sigIQ1FrequencyChanged = QtCore.Signal(float)
    sigIQ1PhaseChanged = QtCore.Signal(float)
    sigIQ1AmplitudeChanged = QtCore.Signal(float)
    sigIQ1GainChanged = QtCore.Signal(float)
    #sigIQ1BandwidthChanged = QtCore.Signal(float)
    sigIQ1ACBandwidthChanged = QtCore.Signal(float)
    sigIQ1InputChanged = QtCore.Signal(str)
    sigIQ1OutputSignalChanged = QtCore.Signal(str)
    sigIQ1ModulationAt2fChanged = QtCore.Signal(bool)
    sigIQ1FilterFrequencyChanged = QtCore.Signal(float)
    sigIQ1PIDPChanged = QtCore.Signal(float)
    
    # Signals for IQ Channel 0
    sigIQ0FrequencyChanged = QtCore.Signal(float)
    sigIQ0PhaseChanged = QtCore.Signal(float)
    sigIQ0AmplitudeChanged = QtCore.Signal(float)
    sigIQ0GainChanged = QtCore.Signal(float)
    #sigIQ0BandwidthChanged = QtCore.Signal(float)
    sigIQ0ACBandwidthChanged = QtCore.Signal(float)
    sigIQ0InputChanged = QtCore.Signal(str)
    sigIQ0OutputSignalChanged = QtCore.Signal(str)
    sigIQ0ModulationAt2fChanged = QtCore.Signal(bool)
    sigIQ0FilterFrequencyChanged = QtCore.Signal(float)
    sigIQ0PIDPChanged = QtCore.Signal(float)

# --------------------- Module lifecycle methods ------------------

    def on_activate(self):
        """ Prepare logic module for work. """
        self._hw = self.redpitaya_hw()
        #self.stopRequest = False
        #self.queryTimer = QtCore.QTimer()
        #self.queryTimer.timeout.connect(self.query_data)
        # State tracking for scope acquisition
        #self.is_acquiring = False
        #self.is_paused = False
        #self.continuous_mode = False

    def on_deactivate(self):
        """ Deactivate module. """


 
# ------------------ IQ Channel 0 get Methods ----------------------------

    @QtCore.Slot()
    def get_iq0_frequency(self):
        """ Get IQ0 demodulator frequency."""
        freq = self._hw.get_iq0_frequency()
        if freq is not None:
            self.sigIQ0FrequencyChanged.emit(freq)
            return freq
        return None

    @QtCore.Slot()
    def get_iq0_phase(self):
        """ Get IQ0 demodulator phase."""
        phase = self._hw.get_iq0_phase()
        if phase is not None:
            self.sigIQ0PhaseChanged.emit(phase)
            return phase
        return None

    @QtCore.Slot()
    def get_iq0_amplitude(self):
        """ Get IQ0 demodulator amplitude."""
        amplitude = self._hw.get_iq0_amplitude()
        if amplitude is not None:
            self.sigIQ0AmplitudeChanged.emit(amplitude)
            return amplitude
        return None

    @QtCore.Slot()
    def get_iq0_gain(self):
        """ Get IQ0 demodulator gain."""
        gain = self._hw.get_iq0_gain()
        if gain is not None:
            self.sigIQ0GainChanged.emit(gain)
            return gain
        return None

    # @QtCore.Slot()
    # def get_iq0_bandwidth(self):
    #     """ Get IQ0 demodulator bandwidth."""
    #     bandwidth = self._hw.get_iq0_bandwidth()
    #     if bandwidth is not None:
    #         self.sigIQ0BandwidthChanged.emit(bandwidth)
    #         return bandwidth
    #     return None

    @QtCore.Slot()
    def get_iq0_acbandwidth(self):
        """ Get IQ0 demodulator AC bandwidth."""
        acbandwidth = self._hw.get_iq0_acbandwidth()
        if acbandwidth is not None:
            self.sigIQ0ACBandwidthChanged.emit(acbandwidth)
            return acbandwidth
        return None

    @QtCore.Slot()
    def get_iq0_input(self):
        """ Get IQ0 input channel."""
        input_channel = self._hw.get_iq0_input()
        if input_channel is not None:
            self.sigIQ0InputChanged.emit(input_channel)
            return input_channel
        return None

    @QtCore.Slot()
    def get_iq0_modulation_at_2f(self):
        """ Get whether IQ0 modulation at 2f is enabled."""
        enabled = self._hw.get_iq0_modulation_at_2f()
        if enabled is not None:
            self.sigIQ0ModulationAt2fChanged.emit(enabled)
            return enabled
        return None

    @QtCore.Slot()
    def get_iq0_filter_frequency(self):
        """ Get the IQ0 bandpass filter frequency."""
        frequency = self._hw.get_iq0_filter_frequency()
        if frequency is not None:
            self.sigIQ0FilterFrequencyChanged.emit(frequency)
            return frequency
        return None


# ------------------ IQ Channel 0 set Methods ----------------------------

    @QtCore.Slot(float)
    def set_iq0_frequency(self, frequency):
        """ Set IQ0 demodulator frequency."""
        if self._hw.set_iq0_frequency(frequency):
            self.sigIQ0FrequencyChanged.emit(frequency)

    @QtCore.Slot(float)
    def set_iq0_phase(self, phase):
        """ Set IQ0 demodulator phase."""
        if self._hw.set_iq0_phase(phase):
            self.sigIQ0PhaseChanged.emit(phase)

    @QtCore.Slot(float)
    def set_iq0_amplitude(self, amplitude):
        """ Set IQ0 demodulator amplitude."""
        if self._hw.set_iq0_amplitude(amplitude):
            self.sigIQ0AmplitudeChanged.emit(amplitude)

    @QtCore.Slot(float)
    def set_iq0_gain(self, gain):
        """ Set IQ0 demodulator gain."""
        if self._hw.set_iq0_gain(gain):
            self.sigIQ0GainChanged.emit(gain)

    # @QtCore.Slot(float)
    # def set_iq0_bandwidth(self, bandwidth):
    #     """ Set IQ0 demodulator bandwidth."""
    #     if self._hw.set_iq0_bandwidth(bandwidth):
    #         self.sigIQ0BandwidthChanged.emit(bandwidth)

    @QtCore.Slot(float)
    def set_iq0_acbandwidth(self, acbandwidth):
        """ Set IQ0 demodulator AC bandwidth."""
        if self._hw.set_iq0_acbandwidth(acbandwidth):
            self.sigIQ0ACBandwidthChanged.emit(acbandwidth)

    @QtCore.Slot(str)
    def set_iq0_input(self, input_channel):
        """ Set IQ0 input channel."""
        if self._hw.set_iq0_input(input_channel):
            self.sigIQ0InputChanged.emit(input_channel)

    @QtCore.Slot(bool)
    def set_iq0_modulation_at_2f(self, enabled):
        """ Set whether IQ0 modulation at 2f is enabled."""
        if self._hw.set_iq0_modulation_at_2f(enabled):
            self.sigIQ0ModulationAt2fChanged.emit(enabled)

    @QtCore.Slot(float)
    def set_iq0_filter_frequency(self, frequency):
        """ Set the IQ0 bandpass filter frequency."""
        if self._hw.set_iq0_filter_frequency(frequency):
            self.sigIQ0FilterFrequencyChanged.emit(frequency)

    @QtCore.Slot()
    def get_iq0_pid_p(self):
        """Get the proportional gain of the PID connected to IQ0."""
        gain = self._hw.get_iq0_pid_p()
        if gain is not None:
            self.sigIQ0PIDPChanged.emit(gain)
        return gain

    @QtCore.Slot(float)
    def set_iq0_pid_p(self, gain):
        """Set the proportional gain of the PID connected to IQ0."""
        if self._hw.set_iq0_pid_p(gain):
            self.sigIQ0PIDPChanged.emit(gain)

    
# ------------------ IQ Channel 1 Get Methods ----------------------------




    @QtCore.Slot()
    def get_iq1_frequency(self):
        """ Get IQ1 demodulator frequency."""
        freq = self._hw.get_iq1_frequency()
        if freq is not None:
            self.sigIQ1FrequencyChanged.emit(freq)
            return freq
        return None    

    @QtCore.Slot()
    def get_iq1_phase(self):
        """ Get IQ1 demodulator phase."""
        phase = self._hw.get_iq1_phase()
        if phase is not None:
            self.sigIQ1PhaseChanged.emit(phase)
            return phase
        return None    

    @QtCore.Slot()
    def get_iq1_amplitude(self):
        """ Get IQ1 demodulator amplitude."""
        amplitude = self._hw.get_iq1_amplitude()
        if amplitude is not None:
            self.sigIQ1AmplitudeChanged.emit(amplitude)
            return amplitude
        return None

    @QtCore.Slot()
    def get_iq1_gain(self):
        """ Get IQ1 demodulator gain."""
        gain = self._hw.get_iq1_gain()
        if gain is not None:
            self.sigIQ1GainChanged.emit(gain)
            return gain
        return None

    # @QtCore.Slot()
    # def get_iq1_bandwidth(self):
    #     """ Get IQ1 demodulator bandwidth."""
    #     bandwidth = self._hw.get_iq1_bandwidth()
    #     if bandwidth is not None:
    #         self.sigIQ1BandwidthChanged.emit(bandwidth)
    #         return bandwidth
    #     return None

    @QtCore.Slot()
    def get_iq1_acbandwidth(self):
        """ Get IQ1 demodulator AC bandwidth."""
        acbandwidth = self._hw.get_iq1_acbandwidth()
        if acbandwidth is not None:
            self.sigIQ1ACBandwidthChanged.emit(acbandwidth)
            return acbandwidth
        return None

    @QtCore.Slot()
    def get_iq1_input(self):
        """ Get IQ1 input channel."""
        input_channel = self._hw.get_iq1_input()
        if input_channel is not None:
            self.sigIQ1InputChanged.emit(input_channel)
            return input_channel
        return None

    @QtCore.Slot()
    def get_iq1_modulation_at_2f(self):
        """ Get whether IQ1 modulation at 2f is enabled."""
        enabled = self._hw.get_iq1_modulation_at_2f()
        if enabled is not None:
            self.sigIQ1ModulationAt2fChanged.emit(enabled)
            return enabled
        return None

    @QtCore.Slot()
    def get_iq1_filter_frequency(self):
        """ Get the IQ1 bandpass filter frequency."""
        frequency = self._hw.get_iq1_filter_frequency()
        if frequency is not None:
            self.sigIQ1FilterFrequencyChanged.emit(frequency)
            return frequency
        return None
  
  

# ------------------ IQ Channel 1 Set Methods ----------------------------


    @QtCore.Slot(float)
    def set_iq1_frequency(self, frequency):
        """ Set IQ1 demodulator frequency."""
        if self._hw.set_iq1_frequency(frequency):
            self.sigIQ1FrequencyChanged.emit(frequency)

    @QtCore.Slot(float)
    def set_iq1_phase(self, phase):
        """ Set IQ1 demodulator phase."""
        if self._hw.set_iq1_phase(phase):
            self.sigIQ1PhaseChanged.emit(phase)

    @QtCore.Slot(float)
    def set_iq1_amplitude(self, amplitude):
        """ Set IQ1 demodulator amplitude."""
        if self._hw.set_iq1_amplitude(amplitude):
            self.sigIQ1AmplitudeChanged.emit(amplitude)

    @QtCore.Slot(bool)
    def set_iq1_modulation_at_2f(self, enabled):
        """ Set whether IQ1 modulation at 2f is enabled."""
        if self._hw.set_iq1_modulation_at_2f(enabled):
            self.sigIQ1ModulationAt2fChanged.emit(enabled)

    @QtCore.Slot(float)
    def set_iq1_filter_frequency(self, frequency):
        """ Set the IQ1 bandpass filter frequency."""
        if self._hw.set_iq1_filter_frequency(frequency):
            self.sigIQ1FilterFrequencyChanged.emit(frequency)

    @QtCore.Slot(float)
    def set_iq1_gain(self, gain):
        """ Set IQ1 demodulator gain."""
        if self._hw.set_iq1_gain(gain):
            self.sigIQ1GainChanged.emit(gain)

    # @QtCore.Slot(float)
    # def set_iq1_bandwidth(self, bandwidth):
    #     """ Set IQ1 demodulator bandwidth."""
    #     if self._hw.set_iq1_bandwidth(bandwidth):
    #         self.sigIQ1BandwidthChanged.emit(bandwidth)

    @QtCore.Slot(float)
    def set_iq1_acbandwidth(self, acbandwidth):
        """ Set IQ1 demodulator AC bandwidth."""
        if self._hw.set_iq1_acbandwidth(acbandwidth):
            self.sigIQ1ACBandwidthChanged.emit(acbandwidth)

    @QtCore.Slot(str)
    def set_iq1_input(self, input_channel):
        """ Set IQ1 input channel."""
        if self._hw.set_iq1_input(input_channel):
            self.sigIQ1InputChanged.emit(input_channel)

    @QtCore.Slot()
    def get_iq1_pid_p(self):
        """Get the proportional gain of the PID connected to IQ1."""
        gain = self._hw.get_iq1_pid_p()
        if gain is not None:
            self.sigIQ1PIDPChanged.emit(gain)
        return gain

    @QtCore.Slot(float)
    def set_iq1_pid_p(self, gain):
        """Set the proportional gain of the PID connected to IQ1."""
        if self._hw.set_iq1_pid_p(gain):
            self.sigIQ1PIDPChanged.emit(gain)


    