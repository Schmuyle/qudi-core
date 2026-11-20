# -*- coding: utf-8 -*-
"""
This file contains the Qudi remote widget class.

"""
from qtpy.QtWidgets import QWidget
from qtpy import uic
import os


class RemoteWidget(QWidget):
    """ This widget shows information about shared or imported remote modules.
    """

    def __init__(self):
        super().__init__()
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_remotewidget.ui')

        # Load it
        uic.loadUi(ui_file, self)
