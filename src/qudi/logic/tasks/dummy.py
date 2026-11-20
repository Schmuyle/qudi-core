# -*- coding: utf-8 -*-
"""
Dummy task for taskrunner.

"""
from qudi.logic.generic_task import InterruptableTask
import time

class Task(InterruptableTask):
    """ Dummy task, does nothing. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('Task {0} added!'.format(self.name))
        self.ctr = 0

    def startTask(self):
        """ Dummy start """
        print('Start')
        self.ctr = 0

    def runTaskStep(self):
        """ Dummy step """
        time.sleep(0.1)
        print('one task step', self.ctr)
        self.ctr += 1
        self._result = '{0} lines printed!'.format(self.ctr)
        return self.ctr < 50

    def pauseTask(self):
        """ Dummy pause """
        time.sleep(1)
        print('paused task')

    def resumeTask(self):
        """ Dummy resume """
        time.sleep(1)
        print('resumed task')

    def cleanupTask(self):
        """ Dummy cleanup """
        print(self._result)
        print('task cleaned up')

    def checkExtraStartPrerequisites(self):
        """ Check extra start prerequisites, there are none """
        print('things needed for task to start')
        return True

    def checkExtraPausePrerequisites(self):
        """ Check extra pause prerequisites, there are none """
        print('things needed for task to pause')
        return True

