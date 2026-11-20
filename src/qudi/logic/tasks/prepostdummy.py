# -*- coding: utf-8 -*-
"""
Dummy preposttask

"""
from qudi.logic.generic_task import PrePostTask
import time

class Task(PrePostTask):
    """ Dummy thask that does nothing before and after a different task has run. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('PrePost init task {0}'.format(name))
        print(self.config)

    def preExecute(self):
        """ Do nothing befoer other task runs
        """
        time.sleep(1)
        print('pre action of task {0}'.format(self.name))

    def postExecute(self):
        """ Do more nothing after other task has finished running
        """
        time.sleep(1)
        print('post action of task {0}'.format(self.name))

