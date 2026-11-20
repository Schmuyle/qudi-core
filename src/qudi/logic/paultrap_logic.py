
import time
from qtpy import QtCore


from qudi.core.module import LogicBase
from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption

class PaulTrapLogic(LogicBase):

    box_gain = 1.18 # 1.1/1.35 # gain on unmodulated signal from the mixing box
    amplifier_gain = 1000 # HV amplifier gain
    smbv_fudge_factor = 0.5 # conversion factor between SMBV set voltage and (p2p) voltage on scope.
    conversion = box_gain * smbv_fudge_factor

    _modclass = 'Paultrap'
    _modtype = 'logic'

    # waiting time between queries im milliseconds
    vso = Connector(interface='SimplePaulTrapInterface')

    queryInterval = ConfigOption('query_interval', 100)

    sigUpdate = QtCore.Signal()

    def on_activate(self):
        """ Prepare logic module for work. """
        self._vso = self.vso()

    def on_deactivate(self):
        """ Deactivate modeule.
        """
        self.stop_query_loop()
        for i in range(5):
            time.sleep(self.queryInterval / 1000)
            QtCore.QCoreApplication.processEvents()

    @QtCore.Slot()
    def start_query_loop(self):
        """ Start the readout loop. """
        self.module_state.run()
        self.queryTimer.start(self.queryInterval)

    @QtCore.Slot()
    def stop_query_loop(self):
        """ Stop the readout loop. """
        self.stopRequest = True
        for i in range(10):
            if not self.stopRequest:
                return
            QtCore.QCoreApplication.processEvents()
            time.sleep(self.queryInterval/1000)

    @QtCore.Slot(float)
    def set_setv_voltage(self, voltage):
        """ Set SMBV voltage. """
        self._vso.set_voltage(self.conversion*voltage)

    @QtCore.Slot(float)
    def set_actv_voltage(self, voltage):
        """ Set paul trap channel voltage. """
        self._vso.set_voltage(self.conversion*voltage/self.amplifier_gain)
        
    @QtCore.Slot(float)
    def set_frequency(self, frequency):
        """ Set trap frequency. """
        self._vso.set_frequency(frequency)
        
    @QtCore.Slot(float)
    def set_strobe_frequency(self, frequency):
        """ Set Rigol strobe frequency. """
        self._vso.set_strobe_frequency(frequency)
        
    @QtCore.Slot(bool)
    def enable_HV(self, state):
        """ Enable HV on the amplifier """
        self.HV = state
        self._vso.enable_HV(state)

    @QtCore.Slot(bool)   
    def set_safety(self, state):
        """ Set safety. """
        self.safety = state
        self._vso.set_safety(state)
        
    @QtCore.Slot(float)
    def get_voltage(self):
        """ measured SMBV channel voltage."""
        time.sleep(0.1)
        return float(self._vso.get_voltage()/self.conversion)

    @QtCore.Slot(float)
    def get_frequency(self):
        """ measured trap frequency. """
        time.sleep(0.1)
        return float(self._vso.get_frequency())
        
    @QtCore.Slot(float)
    def get_strobe_frequency(self):
        """ measure the rigol strobe frquency. """
        time.sleep(0.1)
        return float(self._vso.get_strobe_frequency())
        
        
    @QtCore.Slot(bool)
    def get_state(self):
        """ get state. """
        time.sleep(0.1)
        return bool(self._vso.get_state())
        
    def get_safety(self):
        """ get sasfety switch state. """
        time.sleep(0.1)
        return bool(self._vso.get_safety())
        
    def get_settings(self):
        """ Retrieve all paul trap UI settings. """
        time.sleep(0.1)
        voltage = float(self._vso.get_voltage())/self.conversion
        frequency = float(self._vso.get_frequency())
        strobefrequency = float(self._vso.get_strobe_frequency())-frequency
        state = bool(self._vso.get_state())
        safety = bool(self._vso.get_safety())
        return (voltage, frequency, strobefrequency, state, safety)