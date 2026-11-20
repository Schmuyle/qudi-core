""" Logic module for RedPitaya control. Contains methods for all aspects of the RedPitaya instrument, including IQ demodulator, scope control and input selection. """

import time
import numpy as np
from qtpy import QtCore

from qudi.core.module import LogicBase
from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption


class RedPitayaScopeLogic(LogicBase):
    """ Logic module for RedPitaya control. """
    _modclass = 'redpitaya_scope_logic'
    _modtype = 'logic'

    # Connector to RedPitaya hardware
    redpitaya_hw = Connector(interface='SimpleRedPitayaInterface')

    # Query interval in milliseconds - how quickly to query scope data in the readout loop
    queryInterval = ConfigOption('query_interval', 500)

    # Signals for GUI updates
    sigFrequencyChanged = QtCore.Signal(float)
    sigGainChanged = QtCore.Signal(float)
    sigDurationChanged = QtCore.Signal(float)
    sigScopeDataReady = QtCore.Signal(np.ndarray)
    sigScopeInput1Changed = QtCore.Signal(str)
    sigScopeInput2Changed = QtCore.Signal(str)
    sigScopeTriggerSourceChanged = QtCore.Signal(str)
    sigScopeThresholdChanged = QtCore.Signal(float)
    sigScopeSetupApplied = QtCore.Signal()
    
   
# --------------------- Module lifecycle methods ------------------

    def on_activate(self):
        """ Prepare logic module for work. """
        self._hw = self.redpitaya_hw()
        self.stopRequest = False
        self.queryTimer = QtCore.QTimer()
        self.queryTimer.timeout.connect(self.query_data)        


    def on_deactivate(self):
        """ Deactivate module. """
        self.stop_query_loop()
        for i in range(5):
            time.sleep(self.queryInterval / 1000.0)
            QtCore.QCoreApplication.processEvents()

# ------------------ Scope Control Initialisation Methods ----------------------------

    @QtCore.Slot()
    def start_query_loop(self):
        """ Start the readout loop. """
        self.stopRequest = False
        if self.module_state() == 'idle':
            self.module_state.lock()
        # Ensure the timer is started in this object's thread to avoid
        # "QObject::startTimer: Timers cannot be started from another thread" warnings.
        try:
            QtCore.QMetaObject.invokeMethod(self, '_start_timer_impl', QtCore.Qt.QueuedConnection)
        except Exception:
            # fallback: start directly
            self.queryTimer.start(self.queryInterval)

    @QtCore.Slot()
    def stop_query_loop(self):
        """ Stop the readout loop. """
        self.stopRequest = True
        try:
            QtCore.QMetaObject.invokeMethod(self, '_stop_timer_impl', QtCore.Qt.QueuedConnection)
        except Exception:
            self.queryTimer.stop()
        if self.module_state() == 'locked':
            self.module_state.unlock()
        for i in range(10):
            if not self.stopRequest:
                return
            QtCore.QCoreApplication.processEvents()
            time.sleep(self.queryInterval / 1000.0)

    @QtCore.Slot()
    def _start_timer_impl(self):
        """Internal slot to start the query timer in the correct thread."""
        try:
            self.queryTimer.start(self.queryInterval)
        except Exception:
            pass

    @QtCore.Slot()
    def _stop_timer_impl(self):
        """Internal slot to stop the query timer in the correct thread."""
        try:
            self.queryTimer.stop()
        except Exception:
            pass

    @QtCore.Slot()
    def query_data(self):
        """ Query scope data and emit signal. """
        if self.stopRequest:
            self.stopRequest = False
            return

        data = self._hw.get_scope_data()
        if data is not None:
            self.sigScopeDataReady.emit(data)

    @QtCore.Slot(float)
    def set_scope_duration(self, duration):
        """ Set scope acquisition window duration."""
        if self._hw.set_scope_duration(duration):
            self.sigDurationChanged.emit(duration)


# ------------------ Scope Control Get Methods ----------------------------


    @QtCore.Slot()
    def get_scope_duration(self):
        """ Get scope acquisition window duration."""
        duration = self._hw.get_scope_duration()
        if duration is not None:
            self.sigDurationChanged.emit(duration)
            return duration
        return None

    @QtCore.Slot()
    def get_scope_input1(self):
        """ Get scope channel 1 input source."""
        input_source = self._hw.get_scope_input1()
        if input_source is not None:
            self.sigScopeInput1Changed.emit(input_source)
            return input_source
        return None

    @QtCore.Slot()
    def get_scope_input2(self):
        """ Get scope channel 2 input source."""
        input_source = self._hw.get_scope_input2()
        if input_source is not None:
            self.sigScopeInput2Changed.emit(input_source)
            return input_source
        return None

    @QtCore.Slot()
    def get_scope_trigger_sources(self):
        """ Get supported scope trigger sources."""
        trigger_sources = self._hw.get_scope_trigger_sources()
        if trigger_sources is not None:
            return trigger_sources
        return []

    @QtCore.Slot()
    def get_scope_trigger_source(self):
        """ Get currently selected scope trigger source."""
        trigger_source = self._hw.get_scope_trigger_source()
        if trigger_source is not None:
            self.sigScopeTriggerSourceChanged.emit(trigger_source)
            return trigger_source
        return None

    @QtCore.Slot()
    def get_scope_threshold(self):
        """ Get current scope trigger threshold."""
        threshold = self._hw.get_scope_threshold()
        if threshold is not None:
            self.sigScopeThresholdChanged.emit(threshold)
            return threshold
        return None


# ------------------- Scope Control Set Methods ----------------------------


    @QtCore.Slot(str)
    def set_scope_input1(self, input_source):
        """ Set scope channel 1 input source."""
        if self._hw.set_scope_input1(input_source):
            self.sigScopeInput1Changed.emit(input_source)

    @QtCore.Slot(str)
    def set_scope_input2(self, input_source):
        """ Set scope channel 2 input source."""
        if self._hw.set_scope_input2(input_source):
            self.sigScopeInput2Changed.emit(input_source)

    @QtCore.Slot(str)
    def set_scope_trigger_source(self, trigger_source):
        """ Set scope trigger source."""
        if self._hw.set_scope_trigger_source(trigger_source):
            self.sigScopeTriggerSourceChanged.emit(trigger_source)

    @QtCore.Slot(float)
    def set_scope_threshold(self, threshold):
        """ Set scope trigger threshold."""
        if self._hw.set_scope_threshold(threshold):
            self.sigScopeThresholdChanged.emit(threshold)


# ------------------ Scope Control Apply Methods ----------------------------

    @QtCore.Slot()
    def apply_scope_setup(self, **kwargs):
        """Apply scope configuration atomically and restart continuous mode if needed."""
        if self._hw.apply_scope_setup(**kwargs):
            self.sigScopeSetupApplied.emit()

            

