# -*- coding: utf-8 -*-
"""
This file contains the Qudi automation GUI.

"""

import os

from qudi.core.connector import Connector
from qudi.gui.guibase import GUIBase
from qtpy import QtCore
from qtpy import QtWidgets
from qtpy import uic


class AutomationGui(GUIBase):
    """ Graphical interface for arranging tasks without using Python code. """

    # declare connectors
    automationlogic = Connector(interface='AutomationLogic')

    sigRunTaskFromList = QtCore.Signal(object)
    sigPauseTaskFromList = QtCore.Signal(object)
    sigStopTaskFromList = QtCore.Signal(object)

    def on_activate(self):
        """Create all UI objects and show the window.
        """
        self._mw = AutomationMainWindow()
        self.restoreWindowPos(self._mw)
        self.logic = self.automationlogic()
        self._mw.autoTreeView.setModel(self.logic.model)
        #self._mw.taskTableView.clicked.connect(self.setRunToolState)
        #self._mw.actionStart_Task.triggered.connect(self.manualStart)
        #self._mw.actionPause_Task.triggered.connect(self.manualPause)
        #self._mw.actionStop_Task.triggered.connect(self.manualStop)
        #self.sigRunTaskFromList.connect(self.logic.startTaskByIndex)
        #self.sigPauseTaskFromList.connect(self.logic.pauseTaskByIndex)
        #self.sigStopTaskFromList.connect(self.logic.stopTaskByIndex)
        #self.logic.model.dataChanged.connect(lambda i1, i2: self.setRunToolState(None, i1))
        self.show()

    def show(self):
        """Make sure that the window is visible and at the top.
        """
        self._mw.show()

    def on_deactivate(self):
        """ Hide window and stop ipython console.
        """
        self.saveWindowPos(self._mw)
        self._mw.close()

class AutomationMainWindow(QtWidgets.QMainWindow):
    """ Helper class for window loaded from UI file.
    """
    def __init__(self):
        """ Create the switch GUI window.
        """
        # Get the path to the *.ui file
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_autogui.ui')

        # Load it
        super().__init__()
        uic.loadUi(ui_file, self)
        self.show()

