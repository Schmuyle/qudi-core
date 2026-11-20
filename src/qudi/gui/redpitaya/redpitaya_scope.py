import numpy as np
import pyqtgraph as pg

from qudi.core.connector import Connector
from qudi.util.colordefs import QudiPalettePale as palette
from qudi.gui.guibase import GUIBase

from qtpy import QtCore
from qtpy import QtWidgets


class RedPitayaScopeWindow(QtWidgets.QMainWindow):
    """ Scope monitoring window for RedPitaya. """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('RedPitaya Scope Monitor')
        self.setGeometry(100, 100, 800, 800)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # ===== SCOPE CONTROL GROUP =====
        control_group = QtWidgets.QGroupBox('Scope Controls')
        control_layout = QtWidgets.QFormLayout(control_group)

        # Duration control
        self.duration_label = QtWidgets.QLabel('Duration (s):')
        self.duration_spinbox = QtWidgets.QDoubleSpinBox()
        self.duration_spinbox.setRange(1e-6, 1.0)
        self.duration_spinbox.setDecimals(6)
        self.duration_spinbox.setValue(0.01)
        self.duration_spinbox.setSingleStep(1e-4)
        control_layout.addRow(self.duration_label, self.duration_spinbox)


        layout.addWidget(control_group)

        # ===== CHANNEL 1 GROUP =====
        ch1_group = QtWidgets.QGroupBox('Channel 1')
        ch1_layout = QtWidgets.QVBoxLayout(ch1_group)

        # Source selector for Channel 1
        ch1_source_layout = QtWidgets.QHBoxLayout()
        ch1_source_layout.addWidget(QtWidgets.QLabel('Source:'))
        self.ch1_source_combo = QtWidgets.QComboBox()
        self.ch1_source_combo.addItems(['in1', 'in2', 'out1', 'out2', 'asg0', 'asg1', 'iq0', 'iq1'])
        self.ch1_source_combo.setCurrentText('in1')
        ch1_source_layout.addWidget(self.ch1_source_combo)
        ch1_layout.addLayout(ch1_source_layout)

        # Plot for Channel 1
        self.plot_ch1 = pg.PlotWidget(title='Channel 1')
        self.plot_ch1.setLabel('bottom', 'Time', units='s')
        self.plot_ch1.setLabel('left', 'Voltage', units='V')
        self.plot_ch1.showGrid(True, True)
        self.curve_ch1 = self.plot_ch1.plot(pen=pg.mkPen('r', width=2))
        ch1_layout.addWidget(self.plot_ch1)

        layout.addWidget(ch1_group, stretch=1)

        # ===== CHANNEL 2 GROUP =====
        ch2_group = QtWidgets.QGroupBox('Channel 2')
        ch2_layout = QtWidgets.QVBoxLayout(ch2_group)

        # Source selector for Channel 2
        ch2_source_layout = QtWidgets.QHBoxLayout()
        ch2_source_layout.addWidget(QtWidgets.QLabel('Source:'))
        self.ch2_source_combo = QtWidgets.QComboBox()
        self.ch2_source_combo.addItems(['in1', 'in2', 'out1', 'out2', 'asg0', 'asg1', 'iq0', 'iq1'])
        self.ch2_source_combo.setCurrentText('in2')
        ch2_source_layout.addWidget(self.ch2_source_combo)
        ch2_layout.addLayout(ch2_source_layout)

        # Plot for Channel 2
        self.plot_ch2 = pg.PlotWidget(title='Channel 2')
        self.plot_ch2.setLabel('bottom', 'Time', units='s')
        self.plot_ch2.setLabel('left', 'Voltage', units='V')
        self.plot_ch2.showGrid(True, True)
        self.curve_ch2 = self.plot_ch2.plot(pen=pg.mkPen('b', width=2))
        ch2_layout.addWidget(self.plot_ch2)

        layout.addWidget(ch2_group, stretch=1)

        self.show()


class RedPitayaScopeGUI(GUIBase):
    """ Scope monitoring GUI module for RedPitaya control. """
    _modclass = 'redpitayascopegui'
    _modtype = 'gui'

    # Connector to logic
    redpitaya_scope_logic = Connector(interface='RedPitayaScopeLogic')

    # Signals
    sigApplyScopeSetup = QtCore.Signal(dict)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        """ Activate the module. """
        self._logic = self.redpitaya_scope_logic()

        # Create main scope window
        self._mw = RedPitayaScopeWindow()

        # State tracking - ADDED for ScopeMonitor pattern
        self.is_acquiring = False
        self.is_paused = False
        self._duration = 0.01

        # Connect signals to logic
        self.sigApplyScopeSetup.connect(self._apply_scope_setup_slot)


        # Create local query timer in GUI thread to avoid QTimer thread warnings
        self._queryTimer = QtCore.QTimer(self._mw)
        self._queryTimer.setInterval(int(self._logic.queryInterval))
        self._queryTimer.timeout.connect(self._query_scope_data)

        # Initialize duration early so the plot timebase is correct
        duration = self._logic.get_scope_duration()
        self._duration = duration if duration is not None else self._mw.duration_spinbox.value()
        if duration is not None:
            self._mw.duration_spinbox.setValue(duration)

        # Connect GUI widgets to signals - using _apply_scope_setup pattern
        self._mw.duration_spinbox.editingFinished.connect(self.on_duration_changed)
        self._mw.ch1_source_combo.currentTextChanged.connect(self.on_ch1_source_changed)
        self._mw.ch2_source_combo.currentTextChanged.connect(self.on_ch2_source_changed)

        # self._mw.start_button.clicked.connect(self.on_start_clicked)
        # self._mw.stop_button.clicked.connect(self.on_stop_clicked)

        # Connect logic signals to GUI
        self._logic.sigScopeDataReady.connect(self.on_scope_data_ready)

        # Initialize monitor sources
        input1 = self._logic.get_scope_input1()
        if input1:
            prev = self._mw.ch1_source_combo.blockSignals(True)
            self._mw.ch1_source_combo.setCurrentText(input1)
            self._mw.ch1_source_combo.blockSignals(prev)
        input2 = self._logic.get_scope_input2()
        if input2:
            prev = self._mw.ch2_source_combo.blockSignals(True)
            self._mw.ch2_source_combo.setCurrentText(input2)
            self._mw.ch2_source_combo.blockSignals(prev)

        # Just start Aquisition
        self.on_start_clicked()

    def on_deactivate(self):
        """ Deactivate the module. """
        self._mw.close()

    def show(self):
        """ Show the window. """
        QtWidgets.QMainWindow.show(self._mw)
        self._mw.activateWindow()
        self._mw.raise_()

    @QtCore.Slot()
    def _apply_scope_setup_slot(self, kwargs):
        """Apply scope setup from dictionary."""
        self._logic.apply_scope_setup(**kwargs)

    @QtCore.Slot()
    def _query_scope_data(self):
        """Query scope data with state protection."""
        if not self.is_acquiring:
            self.is_acquiring = True
            self._logic.query_data()
        else:
            # Prevent concurrent queries
            pass

    @QtCore.Slot()
    def on_duration_changed(self):
        """ Apply duration change. """
        duration = self._mw.duration_spinbox.value()
        self._duration = duration
        setup_dict = {'duration': duration}
        self.sigApplyScopeSetup.emit(setup_dict)
        # Update plot X ranges immediately to match new duration
        try:
            self._mw.plot_ch1.setXRange(0, self._duration, padding=0)
            self._mw.plot_ch2.setXRange(0, self._duration, padding=0)
        except Exception:
            pass

    @QtCore.Slot()
    def on_start_clicked(self):
        """ Start acquisition. """
        self._logic.stopRequest = False
        self.is_acquiring = False
        # ensure X axis matches current duration
        try:
            self._mw.plot_ch1.setXRange(0, self._duration, padding=0)
            self._mw.plot_ch2.setXRange(0, self._duration, padding=0)
        except Exception:
            pass
        self._queryTimer.start()

    # @QtCore.Slot()
    # def on_stop_clicked(self):
    #     """ Stop acquisition. """
    #     self._logic.stopRequest = True
    #     self.is_acquiring = False
    #     self._queryTimer.stop()

    @QtCore.Slot(str)
    def on_ch1_source_changed(self, value):
        """Apply channel 1 source change."""
        setup_dict = {'input1': value}
        self.sigApplyScopeSetup.emit(setup_dict)

    @QtCore.Slot(str)
    def on_ch2_source_changed(self, value):
        """Apply channel 2 source change."""
        setup_dict = {'input2': value}
        self.sigApplyScopeSetup.emit(setup_dict)

    @QtCore.Slot(np.ndarray)
    def on_scope_data_ready(self, data):
        """ Update plots with scope data. """
        self.is_acquiring = False  # Mark acquisition as complete
        
        if data is not None and len(data) >= 2:
            ch1 = np.asarray(data[0])
            ch2 = np.asarray(data[1])

            if len(ch1) > 0:
                duration = self._duration if hasattr(self, '_duration') else self._mw.duration_spinbox.value()
                t = np.linspace(0, duration, len(ch1))
                self._mw.curve_ch1.setData(t, ch1)
                self._mw.curve_ch2.setData(t, ch2)
                # keep X axis fixed to duration and autoscale Y to data
                try:
                    self._mw.plot_ch1.setXRange(0, duration, padding=0)
                    self._mw.plot_ch2.setXRange(0, duration, padding=0)
                    # autoscale Y only
                    #self._mw.plot_ch1.plotItem.vb.enableAutoRange(axis=pg.ViewBox.YAxis)
                    #self._mw.plot_ch2.plotItem.vb.enableAutoRange(axis=pg.ViewBox.YAxis)
                except Exception:
                    pass
