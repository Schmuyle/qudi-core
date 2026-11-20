import pyvisa as visa
import numpy as np
import nidaqmx
from nidaqmx.constants import LineGrouping

from qudi.core.configoption import ConfigOption
from qudi.interface.simple_paultrap_interface import SimplePaulTrapInterface

class PaulTrap(SimplePaulTrapInterface):

    serial_interface = ConfigOption('interface', 'TCPIP0::192.168.68.153::inst0::INSTR', missing='warn')
    #vso = Connector(interface='SimplePaulTrapInterface')

    _modclass = 'smbv100B'
    _modtype = 'hardware'

    def check_digital_channel(self, channel):
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(
                f'Dev1/port0/line{channel}',
                line_grouping=LineGrouping.CHAN_FOR_ALL_LINES
            )
            task.start()
            data = task.read(number_of_samples_per_channel=1, timeout=0.21)

        if isinstance(data, (list, tuple, np.ndarray)):
            return int(data[0])
        return int(data)

    def set_digital_channel(self, channel, setting):
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(
                f'Dev1/port0/line{channel}',
                line_grouping=LineGrouping.CHAN_FOR_ALL_LINES
            )
            task.start()
            task.write([setting], auto_start=False, timeout=0.21)

        return setting


    def on_activate(self):
        """ Activate module. """
        
        self.connect_vso(self.serial_interface)
        
    def on_deactivate(self):
        """ Deactivate module."""
        self.disconnect_vso()
        
    def connect_vso(self, interface):
        """ Connect to Instrument.
            @param str interface: visa interface identifier
            @return bool: connection success   """
        try:
            self.rm = visa.ResourceManager()

            self.inst = self.rm.open_resource(
                interface, read_termination = '\n', write_termination = '\n')
            ipaddr2 = 'TCPIP0::192.168.68.120::INSTR'
            self.rigoldel = self.rm.open_resource(ipaddr2, timeout=2, read_termination = '\n', write_termination = '\n')
                


        except visa.VisaIOError:
            self.log.exception('Communication Failure:')
            return False
        else:
            return True

    def disconnect_vso(self):
        """ Close the connection to the instrument. """
        self.inst.close()
        #self.inst2.close()
        self.rm.close()
  
    def set_voltage(self, voltage):
        
        voltage=str(voltage)
        self.inst.write(':SOUR:LFO1:VOLT '+voltage)
        
    def set_frequency(self, frequency):
        
        frequency=str(frequency)
        self.inst.write(':SOUR:LFO1:FREQ '+frequency)

    def set_strobe_frequency(self, frequency):
        
        setfreq = float(self.get_frequency())+ frequency
        freq=str(setfreq)
        self.rigoldel.write(':SOUR2:FREQ '+ freq)
        
    def enable_HV(self, state):    
        if state:
            self.inst.write(':SOUR:LFO1 1')
        else:
            self.inst.write(':SOUR:LFO1 0')
            
    def get_voltage(self):
        return str(self.inst.query(':SOUR:LFO1:VOLT?')) 

    def get_frequency(self):
        return str(self.inst.query(':SOUR:LFO1:FREQ?'))        

    def get_strobe_frequency(self):
        return str(self.rigoldel.query(':SOUR2:FREQ?'))

    def get_state(self):
        return str(self.inst.query(':SOUR:LFO1?')) 

    def get_safety(self):
        return self.check_digital_channel(1) 
        
    def set_safety(self, state):
        self.set_digital_channel(1, state)       
        
