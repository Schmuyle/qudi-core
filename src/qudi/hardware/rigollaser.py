from __future__ import division
import pyvisa as visa
import numpy as np
import time
from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.simpler_rigol_interface import SimplerRigolInterface

class Rigol4000(SimplerRigolInterface):


    serial_interface = ConfigOption('interface', 'TCPIP0::192.168.68.136::INSTR', missing='warn')
    serial_interface_2 = ConfigOption('interface', 'TCPIP0::192.168.68.136::INSTR', missing='warn')

    _modclass = 'rigol_4162'
    _modtype = 'hardware'




    def on_activate(self):
        """ Activate module.
        """
        
        self.connect_rigol(self.serial_interface)
        
    def on_deactivate(self):
        """ Deactivate module.
        """
        self.disconnect_rigol()
        
    def connect_rigol(self, interface, interface2 = None):
        """ Connect to Instrument.

            @param str interface: visa interface identifier

            @return bool: connection success
        """
        try:
            self.rm = visa.ResourceManager()

            self.inst = self.rm.open_resource(
                interface, read_termination = '\n', write_termination = '\n')
                
            #self.inst2 = self.rm.open_resource(
            #    interface2, read_termination = '\n', write_termination = '\n')
            # give laser 2 seconds maximum to reply
            self.inst.timeout = 2000
            self.inst.write(':SOUR1:APPL:USER 1')
            self.inst.write(':SOUR2:APPL:USER 1')
            #self.inst2.write(':SOUR1:APPL:USER 1')
            
            #self.inst.write('OUTP1:IMP 50')
            #self.inst.write('OUTP2:IMP 50')
            self.inst.write('OUTP1:IMP INFINITY')
            self.inst.write('OUTP2:IMP INFINITY')
            #self.inst2.write('OUTP1 OFF')
            self.inst.write('OUTP1 OFF')
            self.inst.write('OUTP2 OFF')

        except visa.VisaIOError:
            self.log.exception('Communication Failure:')
            return False
        else:
            return True

    def disconnect_rigol(self):
        """ Close the connection to the instrument.
        """
        self.inst.close()
        #self.inst2.close()
        self.rm.close()




  
    def set_ch1_voltage(self, voltage):
        
        voltage=str(voltage)
        self.inst.write(':SOUR1:VOLT:OFFS '+voltage)
        
    def set_ch1_state(self, state):    
        if state:
            self.inst.write(':OUTP1 ON')
        else:
            self.inst.write(':OUTP1 OFF')
            
            
    def set_ch2_voltage(self, voltage):
        
        voltage=str(voltage)
        self.inst.write(':SOUR2:VOLT:OFFS '+voltage)
        
    def set_ch2_state(self, state):    
        if state:
            self.inst.write(':OUTP2 ON')
        else:
            self.inst.write(':OUTP2 OFF')
            
    # def set_ch3_voltage(self):
        
        # dBm=str(3.3)
        # self.inst2.write(':SOUR1:VOLT '+dBm)
        
    # def set_ch3_state(self, state):    
        # if state:
            # self.inst2.write(':OUTP1 ON')
        # else:
            # self.inst2.write(':OUTP1 OFF')
            

    # def config_pulse_mode(self, chan, tpulse, volts):
        # if chan <= 2:
            # self.inst.write(':SOUR'+str(chan)+':APPL:PULS')
            # self.inst.write(':SOUR'+str(chan)+':VOLT:HIGH '+str(volts))
            # self.inst.write(':SOUR'+str(chan)+':VOLT:LOW 0')
            # print("i should go here")
            # self.inst.write(':SOUR'+str(chan)+':FREQ '+str(1))
            # self.inst.write(':SOUR'+str(chan)+':PULS:WIDT '+str(tpulse))
            # self.inst.write(':SOUR'+str(chan)+':BURS ON')
            # self.inst.write(':SOUR'+str(chan)+':BURS:NCYC 1')
            # self.inst.write(':SOUR'+str(chan)+':BURS:TRIG:SOUR MAN')
        # else:
            # self.inst2.write(':SOUR'+str(1)+':APPL:PULS')
            # self.inst2.write(':SOUR'+str(1)+':VOLT:HIGH '+str(3.3))
            # self.inst2.write(':SOUR'+str(1)+':VOLT:LOW 0')

            # self.inst2.write(':SOUR'+str(1)+':FREQ '+str(1))
            # self.inst2.write(':SOUR'+str(1)+':PULS:WIDT '+str(tpulse))
            # self.inst2.write(':SOUR'+str(1)+':BURS ON')
            # self.inst2.write(':SOUR'+str(1)+':BURS:MODE TRIG')
            # self.inst2.write(':SOUR'+str(1)+':BURS:NCYC 1')
            # self.inst2.write(':SOUR'+str(1)+':BURS:TRIG:SOUR MAN')
    def config_dc_mode(self,chan, vol):
        if chan <= 2:
            self.inst.write(':SOUR'+str(chan)+':APPL:USER 1')   
            self.inst.write(':SOUR'+str(chan)+':VOLT:OFFS '+str(vol))
        else:
            print("no")
            #self.inst2.write(':SOUR'+str(1)+':APPL:USER 1')   
            #self.inst2.write(':SOUR'+str(1)+':VOLT:OFFS '+str(5))
            
    def trig_pulse(self):
        self.inst.write('*TRG')
        
    # def trig_pulse2(self, time0):
        # self.inst2.write('*TRG')
