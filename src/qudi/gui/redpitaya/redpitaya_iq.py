import numpy as np

from qudi.core.connector import Connector
from qudi.util.colordefs import QudiPalettePale as palette
from qudi.gui.guibase import GUIBase

from qtpy import QtCore
from qtpy import QtWidgets

class RedPitayaWindow(QtWidgets.QMainWindow):
    """ Main window for RedPitaya control GUI.  """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('RedPitaya Controller')
        self.setGeometry(0, 0, 250, 550)

        # Central widget with scroll area for many controls
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        central_widget = QtWidgets.QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # ===== IQ channel 0 GROUP =====
        iq0_group = QtWidgets.QGroupBox('IQ channel 0 Demodulator')
        iq0_layout = QtWidgets.QFormLayout(iq0_group)

        # Input Channel
        iq0_layout.addWidget(QtWidgets.QLabel('Input Channel:'))
        self.iq0_input_combo = QtWidgets.QComboBox()
        self.iq0_input_combo.addItems(['in1', 'in2', 'iq0', 'iq1'])
        self.iq0_input_combo.setCurrentText('in1')
        iq0_layout.addRow('Input Channel:', self.iq0_input_combo)

        # Frequency
        self.iq0_freq_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq0_freq_spinbox.setRange(0.1, 50e6)
        self.iq0_freq_spinbox.setDecimals(1)
        self.iq0_freq_spinbox.setValue(1e6)
        self.iq0_freq_spinbox.setSingleStep(1000)
        iq0_layout.addRow('Frequency (Hz):', self.iq0_freq_spinbox)

        # Phase
        self.iq0_phase_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq0_phase_spinbox.setRange(0, 360)
        self.iq0_phase_spinbox.setDecimals(1)
        self.iq0_phase_spinbox.setValue(0)
        self.iq0_phase_spinbox.setSingleStep(1)
        iq0_layout.addRow('Phase (degrees):', self.iq0_phase_spinbox)

        # Amplitude
        self.iq0_amplitude_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq0_amplitude_spinbox.setRange(0.0, 2.0)
        self.iq0_amplitude_spinbox.setDecimals(3)
        self.iq0_amplitude_spinbox.setValue(0.1)
        self.iq0_amplitude_spinbox.setSingleStep(0.01)
        iq0_layout.addRow('Amplitude:', self.iq0_amplitude_spinbox)

        # Gain
        self.iq0_gain_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq0_gain_spinbox.setRange(0.0, 1000)
        self.iq0_gain_spinbox.setDecimals(3)
        self.iq0_gain_spinbox.setValue(1.0)
        self.iq0_gain_spinbox.setSingleStep(0.01)
        iq0_layout.addRow('Gain:', self.iq0_gain_spinbox)

        # AC Bandwidth
        self.iq0_acbandwidth_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq0_acbandwidth_spinbox.setRange(1, 1e6)
        self.iq0_acbandwidth_spinbox.setDecimals(1)
        self.iq0_acbandwidth_spinbox.setValue(1000)
        self.iq0_acbandwidth_spinbox.setSingleStep(10)
        iq0_layout.addRow('AC Bandwidth (Hz):', self.iq0_acbandwidth_spinbox)

        self.iq0_filter_frequency_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq0_filter_frequency_spinbox.setRange(1, 50e6)
        self.iq0_filter_frequency_spinbox.setDecimals(1)
        self.iq0_filter_frequency_spinbox.setValue(300000)
        self.iq0_filter_frequency_spinbox.setSingleStep(1000)
        iq0_layout.addRow('Bandpass Frequency (Hz):', self.iq0_filter_frequency_spinbox)

        self.iq0_modulation_checkbox = QtWidgets.QCheckBox()
        iq0_layout.addRow('Modulation at 2f:', self.iq0_modulation_checkbox)

        self.iq0_pid_p_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq0_pid_p_spinbox.setRange(-1000.0, 1000.0)
        self.iq0_pid_p_spinbox.setDecimals(6)
        self.iq0_pid_p_spinbox.setSingleStep(0.01)
        iq0_layout.addRow('PID P Gain:', self.iq0_pid_p_spinbox)

        main_layout.addWidget(iq0_group)

        # ===== IQ channel 1 GROUP =====
        iq1_group = QtWidgets.QGroupBox('IQ channel 1 Demodulator')
        iq1_layout = QtWidgets.QFormLayout(iq1_group)

        # Input Channel
        iq1_layout.addWidget(QtWidgets.QLabel('Input Channel:'))
        self.iq1_input_combo = QtWidgets.QComboBox()
        self.iq1_input_combo.addItems(['in1', 'in2', 'iq0', 'iq1'])
        self.iq1_input_combo.setCurrentText('in2')
        iq1_layout.addRow('Input Channel:', self.iq1_input_combo)

        # Frequency
        self.iq1_freq_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq1_freq_spinbox.setRange(0.1, 50e6)
        self.iq1_freq_spinbox.setDecimals(1)
        self.iq1_freq_spinbox.setValue(1e6)
        self.iq1_freq_spinbox.setSingleStep(1000)
        iq1_layout.addRow('Frequency (Hz):', self.iq1_freq_spinbox)

        # Phase
        self.iq1_phase_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq1_phase_spinbox.setRange(0, 360)
        self.iq1_phase_spinbox.setDecimals(1)
        self.iq1_phase_spinbox.setValue(0)
        self.iq1_phase_spinbox.setSingleStep(1)
        iq1_layout.addRow('Phase (degrees):', self.iq1_phase_spinbox)

        # Amplitude
        self.iq1_amplitude_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq1_amplitude_spinbox.setRange(0.0, 2.0)
        self.iq1_amplitude_spinbox.setDecimals(3)
        self.iq1_amplitude_spinbox.setValue(0.1)
        self.iq1_amplitude_spinbox.setSingleStep(0.01)
        iq1_layout.addRow('Amplitude:', self.iq1_amplitude_spinbox)

        # Gain
        self.iq1_gain_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq1_gain_spinbox.setRange(0.0, 1000.0)
        self.iq1_gain_spinbox.setDecimals(3)
        self.iq1_gain_spinbox.setValue(1.0)
        self.iq1_gain_spinbox.setSingleStep(0.01)
        iq1_layout.addRow('Gain:', self.iq1_gain_spinbox)

        # AC Bandwidth
        self.iq1_acbandwidth_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq1_acbandwidth_spinbox.setRange(1, 1e6)
        self.iq1_acbandwidth_spinbox.setDecimals(1)
        self.iq1_acbandwidth_spinbox.setValue(1000)
        self.iq1_acbandwidth_spinbox.setSingleStep(10)
        iq1_layout.addRow('AC Bandwidth (Hz):', self.iq1_acbandwidth_spinbox)

        self.iq1_filter_frequency_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq1_filter_frequency_spinbox.setRange(1, 50e6)
        self.iq1_filter_frequency_spinbox.setDecimals(1)
        self.iq1_filter_frequency_spinbox.setValue(300000)
        self.iq1_filter_frequency_spinbox.setSingleStep(1000)
        iq1_layout.addRow('Bandpass Frequency (Hz):', self.iq1_filter_frequency_spinbox)

        self.iq1_modulation_checkbox = QtWidgets.QCheckBox()
        iq1_layout.addRow('Modulation at 2f:', self.iq1_modulation_checkbox)

        self.iq1_pid_p_spinbox = QtWidgets.QDoubleSpinBox()
        self.iq1_pid_p_spinbox.setRange(-1000.0, 1000.0)
        self.iq1_pid_p_spinbox.setDecimals(6)
        self.iq1_pid_p_spinbox.setSingleStep(0.01)
        iq1_layout.addRow('PID P Gain:', self.iq1_pid_p_spinbox)

        main_layout.addWidget(iq1_group)

        self.show()


class RedPitayaIQGUI(GUIBase):
    """ GUI module for RedPitaya control.    """
    _modclass = 'redpitayaIQgui'
    _modtype = 'gui'

    # Connector to logic
    redpitaya_IQ_logic = Connector(interface='RedPitayaIQLogic')

    # IQ channel 0 Signals
    sigSetIQ0Frequency = QtCore.Signal(float)
    sigSetIQ0Phase = QtCore.Signal(float)
    sigSetIQ0Amplitude = QtCore.Signal(float)
    sigSetIQ0Gain = QtCore.Signal(float)
    sigSetIQ0Bandwidth = QtCore.Signal(float)
    sigSetIQ0ACBandwidth = QtCore.Signal(float)
    sigSetIQ0Input = QtCore.Signal(str)
    sigSetIQ0ModulationAt2f = QtCore.Signal(bool)
    sigSetIQ0FilterFrequency = QtCore.Signal(float)
    sigSetIQ0PIDP = QtCore.Signal(float)
    # sigSetIQ0OutputSignal = QtCore.Signal(str)

    # IQ channel 1 Signals
    sigSetIQ1Frequency = QtCore.Signal(float)
    sigSetIQ1Phase = QtCore.Signal(float)
    sigSetIQ1Amplitude = QtCore.Signal(float)
    sigSetIQ1Gain = QtCore.Signal(float)
    sigSetIQ1Bandwidth = QtCore.Signal(float)
    sigSetIQ1ACBandwidth = QtCore.Signal(float)
    sigSetIQ1Input = QtCore.Signal(str)
    sigSetIQ1ModulationAt2f = QtCore.Signal(bool)
    sigSetIQ1FilterFrequency = QtCore.Signal(float)
    sigSetIQ1PIDP = QtCore.Signal(float)
    # sigSetIQ1OutputSignal = QtCore.Signal(str)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        """ Activate the module. """
        self._logic = self.redpitaya_IQ_logic()

        # Create main window
        self._mw = RedPitayaWindow()

        # Connect IQ channel 0 signals to logic
        self.sigSetIQ0Frequency.connect(self._logic.set_iq0_frequency)
        self.sigSetIQ0Phase.connect(self._logic.set_iq0_phase)
        self.sigSetIQ0Amplitude.connect(self._logic.set_iq0_amplitude)
        self.sigSetIQ0Gain.connect(self._logic.set_iq0_gain)
        self.sigSetIQ0ACBandwidth.connect(self._logic.set_iq0_acbandwidth)
        self.sigSetIQ0Input.connect(self._logic.set_iq0_input)
        self.sigSetIQ0ModulationAt2f.connect(self._logic.set_iq0_modulation_at_2f)
        self.sigSetIQ0FilterFrequency.connect(self._logic.set_iq0_filter_frequency)
        self.sigSetIQ0PIDP.connect(self._logic.set_iq0_pid_p)
       
        # Connect IQ channel 1 signals to logic
        self.sigSetIQ1Frequency.connect(self._logic.set_iq1_frequency)
        self.sigSetIQ1Phase.connect(self._logic.set_iq1_phase)
        self.sigSetIQ1Amplitude.connect(self._logic.set_iq1_amplitude)
        self.sigSetIQ1Gain.connect(self._logic.set_iq1_gain)
        self.sigSetIQ1ACBandwidth.connect(self._logic.set_iq1_acbandwidth)
        self.sigSetIQ1Input.connect(self._logic.set_iq1_input)
        self.sigSetIQ1ModulationAt2f.connect(self._logic.set_iq1_modulation_at_2f)
        self.sigSetIQ1FilterFrequency.connect(self._logic.set_iq1_filter_frequency)
        self.sigSetIQ1PIDP.connect(self._logic.set_iq1_pid_p)
        # self.sigSetIQ1OutputSignal.connect(self._logic.set_iq1_output_signal)

        # Connect GUI widgets to signals - IQ channel 0
        self._mw.iq0_input_combo.currentTextChanged.connect(self.on_iq0_input_changed)
        self._mw.iq0_freq_spinbox.editingFinished.connect(self.on_iq0_frequency_changed)
        self._mw.iq0_phase_spinbox.editingFinished.connect(self.on_iq0_phase_changed)
        self._mw.iq0_amplitude_spinbox.editingFinished.connect(self.on_iq0_amplitude_changed)
        self._mw.iq0_gain_spinbox.editingFinished.connect(self.on_iq0_gain_changed)
        self._mw.iq0_acbandwidth_spinbox.editingFinished.connect(self.on_iq0_acbandwidth_changed)
        self._mw.iq0_filter_frequency_spinbox.editingFinished.connect(self.on_iq0_filter_frequency_changed)
        self._mw.iq0_modulation_checkbox.toggled.connect(self.on_iq0_modulation_at_2f_changed)
        self._mw.iq0_pid_p_spinbox.editingFinished.connect(self.on_iq0_pid_p_changed)

        # Connect GUI widgets to signals - IQ channel 1
        self._mw.iq1_input_combo.currentTextChanged.connect(self.on_iq1_input_changed)
        self._mw.iq1_freq_spinbox.editingFinished.connect(self.on_iq1_frequency_changed)
        self._mw.iq1_phase_spinbox.editingFinished.connect(self.on_iq1_phase_changed)
        self._mw.iq1_amplitude_spinbox.editingFinished.connect(self.on_iq1_amplitude_changed)
        self._mw.iq1_gain_spinbox.editingFinished.connect(self.on_iq1_gain_changed)
        self._mw.iq1_acbandwidth_spinbox.editingFinished.connect(self.on_iq1_acbandwidth_changed)
        self._mw.iq1_filter_frequency_spinbox.editingFinished.connect(self.on_iq1_filter_frequency_changed)
        self._mw.iq1_modulation_checkbox.toggled.connect(self.on_iq1_modulation_at_2f_changed)
        self._mw.iq1_pid_p_spinbox.editingFinished.connect(self.on_iq1_pid_p_changed)

        # Initialize values from hardware
        self._initialize_iq0_values()
        self._initialize_iq1_values()

    def on_deactivate(self):
        """ Deactivate the module.        """
        self._mw.close()

    def show(self):
        """ Show the window.        """
        QtWidgets.QMainWindow.show(self._mw)
        self._mw.activateWindow()
        self._mw.raise_()

    def _initialize_iq0_values(self):
        """Initialize IQ channel 0 values from hardware."""
        freq = self._logic.get_iq0_frequency()
        if freq is not None:
            self._mw.iq0_freq_spinbox.setValue(freq)

        phase = self._logic.get_iq0_phase()
        if phase is not None:
            self._mw.iq0_phase_spinbox.setValue(phase)

        amplitude = self._logic.get_iq0_amplitude()
        if amplitude is not None:
            self._mw.iq0_amplitude_spinbox.setValue(amplitude)

        gain = self._logic.get_iq0_gain()
        if gain is not None:
            self._mw.iq0_gain_spinbox.setValue(gain)

        acbandwidth = self._logic.get_iq0_acbandwidth()
        if acbandwidth is not None:
            self._mw.iq0_acbandwidth_spinbox.setValue(acbandwidth)

        input_channel = self._logic.get_iq0_input()
        if input_channel is not None:
            self._mw.iq0_input_combo.setCurrentText(input_channel)

        modulation_enabled = self._logic.get_iq0_modulation_at_2f()
        if modulation_enabled is not None:
            self._mw.iq0_modulation_checkbox.setChecked(modulation_enabled)

        filter_frequency = self._logic.get_iq0_filter_frequency()
        if filter_frequency is not None:
            self._mw.iq0_filter_frequency_spinbox.setValue(filter_frequency)

        pid_p = self._logic.get_iq0_pid_p()
        if pid_p is not None:
            self._mw.iq0_pid_p_spinbox.setValue(pid_p)


    def _initialize_iq1_values(self):
        """Initialize IQ channel 1 values from hardware."""
        freq = self._logic.get_iq1_frequency()
        if freq is not None:
            self._mw.iq1_freq_spinbox.setValue(freq)

        phase = self._logic.get_iq1_phase()
        if phase is not None:
            self._mw.iq1_phase_spinbox.setValue(phase)

        amplitude = self._logic.get_iq1_amplitude()
        if amplitude is not None:
            self._mw.iq1_amplitude_spinbox.setValue(amplitude)

        gain = self._logic.get_iq1_gain()
        if gain is not None:
            self._mw.iq1_gain_spinbox.setValue(gain)

        acbandwidth = self._logic.get_iq1_acbandwidth()
        if acbandwidth is not None:
            self._mw.iq1_acbandwidth_spinbox.setValue(acbandwidth)

        input_channel = self._logic.get_iq1_input()
        if input_channel is not None:
            self._mw.iq1_input_combo.setCurrentText(input_channel)

        modulation_enabled = self._logic.get_iq1_modulation_at_2f()
        if modulation_enabled is not None:
            self._mw.iq1_modulation_checkbox.setChecked(modulation_enabled)

        filter_frequency = self._logic.get_iq1_filter_frequency()
        if filter_frequency is not None:
            self._mw.iq1_filter_frequency_spinbox.setValue(filter_frequency)

        pid_p = self._logic.get_iq1_pid_p()
        if pid_p is not None:
            self._mw.iq1_pid_p_spinbox.setValue(pid_p)


    # ===== IQ channel 0 Slots =====
    @QtCore.Slot(str)
    def on_iq0_input_changed(self, value):
        """Emit IQ0 input channel change signal."""
        self.sigSetIQ0Input.emit(value)


    @QtCore.Slot()
    def on_iq0_frequency_changed(self):
        """Emit IQ0 frequency change signal."""
        freq = self._mw.iq0_freq_spinbox.value()
        self.sigSetIQ0Frequency.emit(freq)

    @QtCore.Slot()
    def on_iq0_phase_changed(self):
        """Emit IQ0 phase change signal."""
        phase = self._mw.iq0_phase_spinbox.value()
        self.sigSetIQ0Phase.emit(phase)

    @QtCore.Slot()
    def on_iq0_amplitude_changed(self):
        """Emit IQ0 amplitude change signal."""
        amplitude = self._mw.iq0_amplitude_spinbox.value()
        self.sigSetIQ0Amplitude.emit(amplitude)

    @QtCore.Slot()
    def on_iq0_gain_changed(self):
        """Emit IQ0 gain change signal."""
        gain = self._mw.iq0_gain_spinbox.value()
        self.sigSetIQ0Gain.emit(gain)

    @QtCore.Slot()
    def on_iq0_acbandwidth_changed(self):
        """Emit IQ0 AC bandwidth change signal."""
        acbandwidth = self._mw.iq0_acbandwidth_spinbox.value()
        self.sigSetIQ0ACBandwidth.emit(acbandwidth)

    @QtCore.Slot(bool)
    def on_iq0_modulation_at_2f_changed(self, value):
        """Emit IQ0 modulation-at-2f change signal."""
        self.sigSetIQ0ModulationAt2f.emit(value)

    @QtCore.Slot()
    def on_iq0_filter_frequency_changed(self):
        """Emit IQ0 bandpass filter frequency change signal."""
        frequency = self._mw.iq0_filter_frequency_spinbox.value()
        self.sigSetIQ0FilterFrequency.emit(frequency)

    @QtCore.Slot()
    def on_iq0_pid_p_changed(self):
        """Emit IQ0 PID proportional gain change signal."""
        self.sigSetIQ0PIDP.emit(self._mw.iq0_pid_p_spinbox.value())

    # ===== IQ channel 1 Slots =====
    @QtCore.Slot(str)
    def on_iq1_input_changed(self, value):
        """Emit IQ1 input channel change signal."""
        self.sigSetIQ1Input.emit(value)

    @QtCore.Slot()
    def on_iq1_frequency_changed(self):
        """Emit IQ1 frequency change signal."""
        freq = self._mw.iq1_freq_spinbox.value()
        self.sigSetIQ1Frequency.emit(freq)

    @QtCore.Slot()
    def on_iq1_phase_changed(self):
        """Emit IQ1 phase change signal."""
        phase = self._mw.iq1_phase_spinbox.value()
        self.sigSetIQ1Phase.emit(phase)

    @QtCore.Slot()
    def on_iq1_amplitude_changed(self):
        """Emit IQ1 amplitude change signal."""
        amplitude = self._mw.iq1_amplitude_spinbox.value()
        self.sigSetIQ1Amplitude.emit(amplitude)

    @QtCore.Slot()
    def on_iq1_gain_changed(self):
        """Emit IQ1 gain change signal."""
        gain = self._mw.iq1_gain_spinbox.value()
        self.sigSetIQ1Gain.emit(gain)

    @QtCore.Slot()
    def on_iq1_acbandwidth_changed(self):
        """Emit IQ1 AC bandwidth change signal."""
        acbandwidth = self._mw.iq1_acbandwidth_spinbox.value()
        self.sigSetIQ1ACBandwidth.emit(acbandwidth)

    @QtCore.Slot(bool)
    def on_iq1_modulation_at_2f_changed(self, value):
        """Emit IQ1 modulation-at-2f change signal."""
        self.sigSetIQ1ModulationAt2f.emit(value)

    @QtCore.Slot()
    def on_iq1_filter_frequency_changed(self):
        """Emit IQ1 bandpass filter frequency change signal."""
        frequency = self._mw.iq1_filter_frequency_spinbox.value()
        self.sigSetIQ1FilterFrequency.emit(frequency)

    @QtCore.Slot()
    def on_iq1_pid_p_changed(self):
        """Emit IQ1 PID proportional gain change signal."""
        self.sigSetIQ1PIDP.emit(self._mw.iq1_pid_p_spinbox.value())
