# -*- coding: utf-8 -*-
"""
This file contains the Qudi logic module base class.

"""
from qtpy import QtCore
from qudi.core.module import Base
from qudi.util.mutex import Mutex


class LogicBase(Base):
    """A generic logic interface class.
    """
    _threaded = True

    def __init__(self, **kwargs):
        """ Initialzize a logic module.

          @param dict kwargs: dict of additional arguments
        """
        super().__init__(**kwargs)
        self.taskLock = Mutex()

    @QtCore.Slot(QtCore.QThread)
    def moveToThread(self, thread):
        super().moveToThread(thread)

    def getModuleThread(self):
        """ Get the thread associated to this module.

          @return QThread: thread with qt event loop associated with this module
        """
        return self._manager.tm._threads['mod-logic-' + self._name].thread

    def getTaskRunner(self):
        """ Get a reference to the task runner module registered in the manager.

          @return object: reference to task runner

          If there isno registered task runner, an exception is raised.
        """
        with self._manager.lock:
            if self._manager.tr is not None:
                return self._manager.tr
            else:
                raise Exception('Tried to access task runner without loading one!')
