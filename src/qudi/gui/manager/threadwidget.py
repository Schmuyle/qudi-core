# -*- coding: utf-8 -*-
"""
This file contains the Qudi remote widget class.

"""
from qtpy.QtWidgets import QWidget
from qtpy import uic
import os


class ThreadWidget(QWidget):

    def __init__(self):
        super().__init__()
        this_dir = os.path.dirname(__file__)
        ui_file = os.path.join(this_dir, 'ui_threadwidget.ui')

        # Load it
        uic.loadUi(ui_file, self)
