import os

from qudi.core.connector import Connector
from qudi.gui.guibase import GUIBase

from qtpy import QtCore
from qtpy import QtWidgets
from qtpy import uic

class PaulWindow(QtWidgets.QMainWindow):
    """ Create the Main Window based on the *.ui file. """

    def __init__(self):
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_paultrap.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

class PaulTrapGUI(GUIBase):
    """ FIXME: Please document """
    _modclass = 'paultrapgui'
    _modtype = 'gui'


    ## declare connectors
    paultrap_logic = Connector(interface='PaulTrapLogic')

    sigSetV = QtCore.Signal(float)
    sigActV = QtCore.Signal(float)
    sigFreq = QtCore.Signal(float)
    sigStrobeFreq = QtCore.Signal(float)

    sigHV = QtCore.Signal(bool)
    sigSafety = QtCore.Signal(bool)


    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        """ Definition and initialisation of the GUI plus staring the measurement.
        """
        self._paultrap_logic = self.paultrap_logic()
        

        #####################
        # Configuring the dock widgets
        # Use the inherited class 'CounterMainWindow' to create the GUI window
        self._mw = PaulWindow()


        # Setup dock widgets
        self._mw.setDockNestingEnabled(True)
        self._mw.actionReset_View.triggered.connect(self.restoreDefaultView)


      
        self._mw.HVradioButton.setStyleSheet("QRadioButton::indicator"
                                        "{"
                                        "width : 60px;"
                                        "height : 60px;"
                                        "}")



        self.sigSetV.connect(self._paultrap_logic.set_setv_voltage)
        self.sigActV.connect(self._paultrap_logic.set_actv_voltage)
        self.sigFreq.connect(self._paultrap_logic.set_frequency)
        self.sigStrobeFreq.connect(self._paultrap_logic.set_strobe_frequency)
    
        self.sigHV.connect(self._paultrap_logic.enable_HV)
        self.sigSafety.connect(self._paultrap_logic.set_safety)

        self._mw.SetVBox.editingFinished.connect(self.updateSetVFromSpinBox)
        self._mw.ActVBox.editingFinished.connect(self.updateActVFromSpinBox)
        self._mw.FreqBox.editingFinished.connect(self.updateFreqFromSpinBox)
        self._mw.StrobeFreqBox.editingFinished.connect(self.updateStrobeFreqFromSpinBox)
        
        self._mw.HVradioButton.clicked.connect(self.HV_on_off_clicked)
        self._mw.SafetycheckBox.clicked.connect(self.Safety_on_off_clicked)
        
        (voltage, frequency, strobefrequency, state, safetystate) = self.get_settings()
        self._mw.SetVBox.setValue(voltage)
        self._mw.ActVBox.setValue(voltage*1000)
        self._mw.FreqBox.setValue(frequency)
        self._mw.StrobeFreqBox.setValue(strobefrequency)
        self._mw.HVradioButton.setChecked(state)
        self._mw.SafetycheckBox.setChecked(safetystate)
        self._mw.HVradioButton.setText('HV ON' if state else 'HV OFF')
        self._mw.HVradioButton.setStyleSheet("color: red;" if state else "color: green;")
      
    def on_deactivate(self):
        """ Deactivate the module properly."""
        self._mw.close()

    def show(self):
        """Make window visible and put it above all other windows. """
        QtWidgets.QMainWindow.show(self._mw)
        self._mw.activateWindow()
        self._mw.raise_()

    def restoreDefaultView(self):
        """ Restore the arrangement of DockWidgets to the default  """
        # Show any hidden dock widgets
        self._mw.adjustDockWidget.show()
        self._mw.plotDockWidget.show()

        # re-dock any floating dock widgets
        self._mw.adjustDockWidget.setFloating(False)
        self._mw.plotDockWidget.setFloating(False)

        # Arrange docks widgets
        self._mw.addDockWidget(QtCore.Qt.DockWidgetArea(1), self._mw.adjustDockWidget)
        self._mw.addDockWidget(QtCore.Qt.DockWidgetArea(2), self._mw.plotDockWidget)

    @QtCore.Slot(bool)
    def HV_on_off_clicked(self, checked):
        """ Manually switch the output on/off. """

        self.sigHV.emit(checked)
        self._mw.HVradioButton.setText('HV ON' if checked else 'HV OFF')
        self._mw.HVradioButton.setStyleSheet("color: red;" if checked else "color: green;")

        return
    @QtCore.Slot(bool)
    def Safety_on_off_clicked(self, checked):
        """ Manually switch the output on/off. """

        self.sigSafety.emit(checked)
        #self._mw.HVradioButton.setText('HV ON' if checked else 'HV OFF')
        #self._mw.HVradioButton.setStyleSheet("color: red;" if checked else "color: green;")
        
        return

    @QtCore.Slot()
    def updateSetVFromSpinBox(self):
        """ The user has changed the spinbox, update all other values from that. """
        val = self._mw.SetVBox.value()
        self.sigSetV.emit(val)
        self._mw.ActVBox.setValue(val*1000)
        
        
    @QtCore.Slot()
    def updateActVFromSpinBox(self):
        """ The user has changed the spinbox, update all other values from that. """

        val = self._mw.ActVBox.value()
        self.sigActV.emit(val)
        self._mw.SetVBox.setValue(val/1000)

    @QtCore.Slot()
    def updateFreqFromSpinBox(self):
        """ The user has changed the spinbox, update all other values from that. """
        self.sigFreq.emit(self._mw.FreqBox.value())
        self.sigStrobeFreq.emit(self._mw.StrobeFreqBox.value())
        
        
    @QtCore.Slot()
    def updateStrobeFreqFromSpinBox(self):
        """ The user has changed the spinbox, update all other values from that. """
        self.sigStrobeFreq.emit(self._mw.StrobeFreqBox.value())
 
    def get_settings(self):
        """ The user has changed the spinbox, update all other values from that. """
        return self._paultrap_logic.get_settings()
        