from __future__ import division
import hardware.xeryon.Xeryon as xy
import pyvisa as visa
import numpy as np
from qudi.core.configoption import ConfigOption
from qudi.core.module import Base
from qudi.interface.simple_xeryon_interface import SimpleXeryonInterface
import PyDAQmx as daq
import time



class Xeryon(SimpleXeryonInterface):

    
    _cominterface = ConfigOption('cominterface', 'COM3', missing='warn')

    _modclass = 'Xeryon'
    _modtype = 'hardware'

    RWTimeout = 10


    def on_activate(self):
        """ Activate module.
        """
        self.connectXeryon(self._cominterface)
        #set axis units
        self.axisX.setUnits(xy.Units.mu)
        self.axisY.setUnits(xy.Units.mu)
        self.axisZ.setUnits(xy.Units.mu)
        #set default encoder pos
        # self.axisX.step(-0.1)
        # self.axisY.step(-0.1)
        # self.axisZ.step(-0.1)
        
        # self.axisX.step(0.1)
        # self.axisY.step(0.1)
        # self.axisZ.step(0.1)
        
        return 0
        
    def on_deactivate(self):
        """ Deactivate module.
        """
        self.controller.stop()
        return 0
        
    def connectXeryon(self, interface):
        """ Connect to Instrument.

            @param str interface: visa interface identifier

            @return bool: connection success
        """
        self.controller = xy.Xeryon(interface, 115200)

        self.axisX = self.controller.addAxis(xy.Stage.XLS_5_3N, "X")
        self.axisY = self.controller.addAxis(xy.Stage.XLS_5_3N, "Y")
        self.axisZ = self.controller.addAxis(xy.Stage.XLS_5_3N, "Z")
        
        self.controller.start()
        
        
        
        return True




    def set_x(self, xval):
        self.axisX.setDPOS(xval)
        val = self.axisX.getEPOS()
        return val
        
    def set_y(self, yval):
        self.axisY.setDPOS(yval)
        val = self.axisY.getEPOS()
        return val
        
    def set_z(self, zval):
        self.axisZ.setDPOS(zval)
        val = self.axisZ.getEPOS()
        return val
        
        
    def get_x(self):
        val = self.axisX.getEPOS()
        return val
        
    def get_y(self):
        val = self.axisY.getEPOS()
        return val
        
    def get_z(self):
        val = self.axisZ.getEPOS()
        return val
        
    def step_x(self, step):
        self.axisX.step(step)
        
    def step_y(self, step):
        self.axisY.step(step)
        
    def step_z(self, step):
        self.axisZ.step(step)
        
    def halt(self):
        self.controller.stopMovements()

    
        