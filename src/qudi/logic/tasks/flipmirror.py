# -*- coding: utf-8 -*-
"""
Flipmirror preposttask

"""

from qudi.logic.generic_task import PrePostTask

class Task(PrePostTask):
    """ A task to flip a switch/mirror/etc before and after another task
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('Task {0} added!'.format(self.name))

    def preExecute(self):
        """ Flip in one direction before the other task executes
        """
        if ('switchlogic' in self.ref
            and 'sequence' in self.config):
                logic = self.ref['switchlogic']
                for element in self.config['sequence']:
                    if element[2]:
                        logic.switches[element[0]][element[1]].switchOn(element[1])
                    else:
                        logic.switches[element[0]][element[1]].switchOff(element[1])
        else:
            self.log.error('No switching sequence configured for pre/post '
                    'task {}'.format(self.name))


    def postExecute(self):
        """ Flip in the other direction after the other task has finished
        """
        if ('switchlogic' in self.ref
            and 'sequence' in self.config):
                logic = self.ref['switchlogic']
                for element in reversed(self.config['sequence']):
                    if element[2]:
                        logic.switches[element[0]][element[1]].switchOff(element[1])
                    else:
                        logic.switches[element[0]][element[1]].switchOn(element[1])
        else:
            self.log.error('No switching sequence configured for pre/post '
                    'task {}'.format(self.name))


