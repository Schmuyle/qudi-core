# -*- coding: utf-8 -*-

"""
QCheckBox with a callback function for acceptance or denial of state change.

"""

from qtpy.QtWidgets import QCheckBox


class CheckBox(QCheckBox):
    """
    This QCheckBox provides a callback function which is called before
    the state is changed and which can be used to prevent state changes on
    certain conditions.

    The callback function has the following signature:
    bool callback(new_state: bool)
    where new_state is a boolean with the new state if accepted and the return
    value is True for acceptance and False for denial.

    Usage Example:
    checkbox = CheckBox()
    def on_accept_state_change(new_state):
        if (not new_state):
            result = QMessageBox.question(
                    self,
                    'Are you sure you want to disable this?',
                    QMessageBox.StandardButtons(
                        QMessageBox.Yes | QMessageBox.No)
                    )
            return result == QMessageBox.Yes
    checkbox.accept_state_change_callback = on_accept_state_change
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor. See QCheckBox for details.
        """
        super().__init__(*args, **kwargs)
        self._callback = None

    @property
    def accept_state_change_callback(self):
        """
        Returns state changing callback function.

        The callback function has the following signature:
        bool callback(new_state: bool)
        where new_state is a boolean with the new state if accepted and the
        return value is True for acceptance and False for denial.
        """
        return self._callback

    @accept_state_change_callback.setter
    def accept_state_change_callback(self, value):
        """
        Sets state changing callback function.

        The callback function has the following signature:
        bool callback(new_state: bool)
        where new_state is a boolean with the new state if accepted and the
        return value is True for acceptance and False for denial.
        """
        self._callback = value

    def nextCheckState(self):
        """
        Protected functions that calls the callback.
        """
        if self._callback is not None:
            if self._callback(not self.isChecked()):
                super().nextCheckState()
        else:
            super().nextCheckState()
