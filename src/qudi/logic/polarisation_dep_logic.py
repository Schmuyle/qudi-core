# -*- coding: utf-8 -*-
"""
This file contains the Qudi logic class for performing polarisation dependence measurements.

"""

from qudi.core.connector import Connector
from qudi.core.module import LogicBase
from qtpy import QtCore


class PolarisationDepLogic(LogicBase):
    """This logic module rotates polarisation and records signal as a function of angle.

    """

    # declare connectors
    counterlogic = Connector(interface='CounterLogic')
    savelogic = Connector(interface='SaveLogic')
    motor = Connector(interface='MotorInterface')

    signal_rotation_finished = QtCore.Signal()
    signal_start_rotation = QtCore.Signal()

    def on_activate(self):
        """ Initialisation performed during activation of the module.
        """

        self._counter_logic = self.counterlogic()
#        print("Counting device is", self._counting_device)

        self._save_logic = self.savelogic()

        self._hwpmotor = self.motor()

        # Initialise measurement parameters
        self.scan_length = 360
        self.scan_speed = 10 #not yet used

        # Connect signals
        self.signal_rotation_finished.connect(self.finish_scan, QtCore.Qt.QueuedConnection)
        self.signal_start_rotation.connect(self.rotate_polarisation, QtCore.Qt.QueuedConnection)


    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        return

    def measure_polarisation_dependence(self):
        """Do a simple pol dep measurement.
        """

        # Set up measurement
        self._hwpmotor.move_abs(0)

        # configure the countergui


        self._counter_logic.start_saving()
        self.signal_start_rotation.emit()

    def rotate_polarisation(self):
        self._hwpmotor.move_rel(self.scan_length)
        self.log.info('rotation finished, saving data')
        self.signal_rotation_finished.emit()

    def finish_scan(self):
        self._counter_logic.save_data()
#        self._counter_logic.stopCount()
