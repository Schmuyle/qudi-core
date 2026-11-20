# -*- coding: utf-8 -*-
"""
This file contains the Qudi GUI module base class.

"""
# Test gui (test)

from qudi.core.configoption import ConfigOption
from qudi.gui.guibase import GUIBase
from qtpy import QtWidgets


class TestGui(GUIBase):
    """A class to test gui module loading.

        This class does not implement a show() method to test the
        error thrown by GUIBase when this function is not implemented.
    """

    buttonText = ConfigOption('text', 'No Text configured')
    infoOption = ConfigOption('info', 'Info Option', missing='info')
    warningOption = ConfigOption('warning', 'Warning Option', missing='warn')
    errorOption = ConfigOption('error', missing='error')

    def __init__(self, config, **kwargs):
        """Create a TestWindow object.

          @param dict config: configuration dictionary
          @param dict kwargs: further optional arguments
        """
        super().__init__(config=config, **kwargs)

    def on_activate(self):
        """This creates all the necessary UI elements.
        """
        self._mw = QtWidgets.QMainWindow()
        self._mw.setGeometry(300,300,500,100)
        self._mw.setWindowTitle('TEST')
        self.cwdget = QtWidgets.QWidget()
        self.button = QtWidgets.QPushButton(self.buttonText)
        self.buttonerror = QtWidgets.QPushButton('Giff Error!')
        self.checkbutton = QtWidgets.QPushButton('Status Error')
        self.checkbutton.setCheckable(True)
        self.button.clicked.connect(self.handleButton)
        self.buttonerror.clicked.connect(self.handleButtonError)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.buttonerror)
        self.layout.addWidget(self.checkbutton)
        self.cwdget.setLayout(self.layout)
        self._mw.setCentralWidget(self.cwdget)
        self._mw.show()

    def on_deactivate(self):
        """
        """
        pass

    def handleButton(self):
        """Change style of buttons.
        """
        self.button.setStyleSheet(
            'QPushButton {background-color:'
            ' #A3C1DA; color: red;}')

    def handleButtonError(self):
        """ Produce an exception for testing.
        """
        raise Exception('Сука Блять')

    def getState(self):
        if hasattr(self, 'checkbutton') and self.checkbutton.isChecked():
            raise Exception('Fail.')
        else:
            return super().module_state()
