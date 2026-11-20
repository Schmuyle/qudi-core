from __future__ import division
import pyvisa as visa
import numpy as np
from qudi.core.configoption import ConfigOption
from qudi.core.module import Base
from qudi.interface.simple_galvo_interface import SimpleGalvoInterface
import PyDAQmx as daq
import time



class NI6733Galvo(SimpleGalvoInterface):

    
    devname = ConfigOption('devname', False, missing='warn')
    xoffset = ConfigOption('xoffset', False, missing='warn')
    yoffset = ConfigOption('yoffset', False, missing='warn')
    _modclass = 'NI6733Galvo'
    _modtype = 'hardware'
    chan_map = {0:'2', 1:'3'}
    RWTimeout = 10


    def on_activate(self):
        """ Activate module.
        """
        
        return 0
        
    def on_deactivate(self):
        """ Deactivate module.
        """
        return 0
        
    def connect_psu(self, interface):
        """ Connect to Instrument.

            @param str interface: visa interface identifier

            @return bool: connection success
        """

        return True

    def disconnect_psu(self):
        """ Close the connection to the instrument.
        """
        return 0


    def set_state(self,chan,state):


        return 0
        
        
    def get_state(self,chan):


        return 0

    

    def get_voltage_setpoint(self, chan):

        return 0
        
    def get_current_setpoint(self, chan):


        return 0
    def get_offsets(self, chan):
        
        ch_dic = {0:0, 1:0, 2: self.xoffset, 3: self.yoffset, 4:0, 5:0}
        return ch_dic[chan]

    def get_voltage(self, channel):
        
            return -1
    def get_current(self, channel):
       
        return current

    def channel_dev(self, chan):
        channel = "/Dev2/ao"+str(chan)
        return channel

    def set_voltage(self, chan, voltage, buff = 100): #every time we set the voltage for one channel, set it to the abs value but set the monitor channel to the signed value.
        self.set_chan_voltage(chan, voltage, buff = 100)#sets voltage driving coil to abs voltage
        #print("setting voltages")
        return voltage
        
    def set_chan_voltage(self, chan, voltage, buff = 100):
        #sets one channel to a given voltage. 
        task = daq.TaskHandle()
        offset = 0#self.get_offsets(chan)
        
        voltage = float(voltage)+offset
        #print("setting V to "+str(voltage))
        channel = "/Dev2/ao"+str(chan)
        
        daq.DAQmxCreateTask('', daq.byref(task))
        
        daq.DAQmxCreateAOVoltageChan(task,channel,"",-10.0,10.0,daq.DAQmx_Val_Volts,None)
       
        daq.DAQmxSetSampTimingType(task, daq.DAQmx_Val_SampClk)
        daq.DAQmxSetAODACRefVal(task, channel, 10.000)
        daq.DAQmxSetAODACRefSrc(task, channel, daq.DAQmx_Val_External)
        v0 = np.array([voltage  for i in range(buff)])
        AONwritten = daq.int32()
        daq.DAQmxWriteAnalogF64(task,buff, False, self.RWTimeout, daq.DAQmx_Val_GroupByChannel, v0, daq.byref(AONwritten),None)
        daq.DAQmxStartTask(task)
        time.sleep(0.05)    
        daq.DAQmxStopTask(task)
        daq.DAQmxClearTask(task)

        return voltage
        
    def do_xyscan(self, xmin, xmax, ymin, ymax, dwell_time, resolution):
    # def do_xyscan(self):
        #force ramp to currents.
        task = daq.TaskHandle()
        
        

        # dwell_time = 0.001
        scanner_clock_frequency =1./dwell_time#min(int(100*frequency_sine), 1e6)#sampling rate
        # xmin = -1
        # xmax = 1
        # ymin = -1
        # ymax = 1
        # resolution = 100
        npoints = resolution
        x_sig = np.linspace(xmin, xmax, resolution)+self.xoffset
        y_sig = np.linspace(ymin, ymax, resolution)+self.yoffset
        vx = np.empty(resolution**2)
        vy = np.empty(resolution**2)
        for i, yv in enumerate(y_sig):
            vx[i*resolution:i*resolution+resolution] = x_sig
            vy[i*resolution:i*resolution+resolution] = np.full(resolution, yv)
        pts = len(vx)
        
        
        
        
        channelx = "/Dev2/ao2"
        channely = "/Dev2/ao3"
        daq.DAQmxCreateTask('', daq.byref(task))
        
        daq.DAQmxCreateAOVoltageChan(task,', '.join([channelx, channely]),"",-10.0,10.0,daq.DAQmx_Val_Volts,None)
        daq.DAQmxSetSampTimingType(task, daq.DAQmx_Val_SampClk)
        daq.DAQmxCfgSampClkTiming(task,
            "OnboardClock",
            scanner_clock_frequency,
            daq.DAQmx_Val_Rising,
            daq.DAQmx_Val_FiniteSamps,
            # daq.DAQmx_Val_ContSamps,
            pts)
        
        AONwritten = daq.int32()
        daq.DAQmxWriteAnalogF64(task,pts, False, self.RWTimeout, daq.DAQmx_Val_GroupByChannel, np.array([vx,vy]), daq.byref(AONwritten),None)
        daq.DAQmxStartTask(task)
        #print("Ramping from "+str(np.round(prev_volt,5))+"V to "+str(np.round(new_volt,5))+"V in "+str(time0)+"s.")
        
        time.sleep(len(vx)*dwell_time+0.5)
        daq.DAQmxStopTask(task)
        daq.DAQmxClearTask(task)

        return 1


    def do_pathrpt(self, path, time_tot):
    # def do_xyscan(self):
        #force ramp to currents.
        task = daq.TaskHandle()
        
        

        # dwell_time = 0.001
        #path is xy coords
        resolution = len(path)*2
        dwell_time = time_tot/resolution
        scanner_clock_frequency =1./dwell_time#min(int(100*frequency_sine), 1e6)#sampling rate
        # xmin = -1
        # xmax = 1
        # ymin = -1
        # ymax = 1
        # resolution = 100
        npoints = resolution
        x_sig = np.hstack((path.T[0], path.T[0][::-1]))
        y_sig = np.hstack((path.T[1], path.T[1][::-1]))
        vx = x_sig + self.xoffset
        vy = y_sig + self.yoffset
        # for i, yv in enumerate(y_sig):
            # vx[i*resolution:i*resolution+resolution] = x_sig
            # vy[i*resolution:i*resolution+resolution] = np.full(resolution, yv)
        pts = len(vx)
        
        
        
        
        channelx = "/Dev2/ao2"
        channely = "/Dev2/ao3"
        daq.DAQmxCreateTask('', daq.byref(task))
        daq.DAQmxCreateAOVoltageChan(task,', '.join([channelx, channely]),"",-10.0,10.0,daq.DAQmx_Val_Volts,None)
        daq.DAQmxSetSampTimingType(task, daq.DAQmx_Val_SampClk)
        daq.DAQmxCfgSampClkTiming(task,
            "OnboardClock",
            scanner_clock_frequency,
            daq.DAQmx_Val_Rising,
            #daq.DAQmx_Val_FiniteSamps,
            daq.DAQmx_Val_ContSamps,
            pts)
        
        AONwritten = daq.int32()
        daq.DAQmxWriteAnalogF64(task,pts, False, self.RWTimeout, daq.DAQmx_Val_GroupByChannel, np.array([vx,vy]), daq.byref(AONwritten),None)
        daq.DAQmxStartTask(task)
        #print("Ramping from "+str(np.round(prev_volt,5))+"V to "+str(np.round(new_volt,5))+"V in "+str(time0)+"s.")
        
        #time.sleep(len(vx)*dwell_time+0.5)
        #daq.DAQmxStopTask(task)
        #daq.DAQmxClearTask(task)

        return task
        
    # def do_ac_hv(self, amp,freq, duration, offset = 0):
    # # def do_xyscan(self):
        # #force ramp to currents.
        # task = daq.TaskHandle()
        
        

        # # dwell_time = 0.001
        # scanner_clock_frequency = 1e6#min(int(100*frequency_sine), 1e6)#sampling rate
        # # xmin = -1
        # tickstep = 1./scanner_clock_frequency
        # period = 1./freq
        # pts = int(duration/tickstep)

        # v0s = np.arange(0,pts,1)
        # if np.mod(len(v0s),2):
            # v0s = v0s[:-1]
        # time0s = tickstep*v0s
        

        # ysig = amp*np.sin(2*np.pi * freq * time0s) + offset
        # ysig = np.hstack((ysig, np.array([0,0])))
        # pts = len(ysig)
        
        
        
        
        # channelV = "/Dev2/ao5"
        
        # daq.DAQmxCreateTask('', daq.byref(task))
        # daq.DAQmxCreateAOVoltageChan(task,channelV,"",-10.0,10.0,daq.DAQmx_Val_Volts,None)
        # daq.DAQmxSetSampTimingType(task, daq.DAQmx_Val_SampClk)
        # print(daq.DAQmx_Val_SampClk)
        # daq.DAQmxCfgSampClkTiming(task,
            # "OnboardClock",
            # scanner_clock_frequency,
            # daq.DAQmx_Val_Rising,
            # daq.DAQmx_Val_FiniteSamps,
            # # daq.DAQmx_Val_ContSamps,
            # pts)
        
        # AONwritten = daq.int32()
        # daq.DAQmxWriteAnalogF64(task,pts, False, self.RWTimeout, daq.DAQmx_Val_GroupByChannel, ysig, daq.byref(AONwritten),None)
        # daq.DAQmxStartTask(task)
        # #print("Ramping from "+str(np.round(prev_volt,5))+"V to "+str(np.round(new_volt,5))+"V in "+str(time0)+"s.")
        
        # time.sleep(duration)
        # daq.DAQmxStopTask(task)
        # daq.DAQmxClearTask(task)

        # return 1

    def do_ac_hv(self, amp,freq, duration, offset = 0, forever = False, etrig=False):
    # def do_xyscan(self):
        #force ramp to currents.
        task = daq.TaskHandle()
        task2 = daq.TaskHandle()
        
        

        # dwell_time = 0.001
        scanner_clock_frequency = 1e6#min(int(100*frequency_sine), 1e6)#sampling rate
        # xmin = -1
        tickstep = 1./scanner_clock_frequency
        #period = 1./freq
        pts = int(duration/tickstep)

        v0s = np.arange(0,pts,1)
        if np.mod(len(v0s),2):
            v0s = v0s[:-1]
        time0s = tickstep*v0s
        

        ysig = amp*np.sin(2*np.pi * freq * time0s) + offset
        ysig = np.hstack((ysig, np.array([0,0])))
        pts = len(ysig)
        
        
        
        
        channelV = "/Dev2/ao5"
        
        daq.DAQmxCreateTask('', daq.byref(task))
        daq.DAQmxCreateTask('', daq.byref(task2))
        daq.DAQmxCreateAOVoltageChan(task,channelV,"",-10.0,10.0,daq.DAQmx_Val_Volts,None)
        
        #daq.DAQmxCreateDIChan(task2,"/Dev2/PFI0","",daq.DAQmx_Val_ChanForAllLines)
        
        daq.DAQmxSetSampTimingType(task, daq.DAQmx_Val_SampClk)
        
        daq.DAQmxCfgSampClkTiming(task,
            "OnboardClock",
            scanner_clock_frequency,
            daq.DAQmx_Val_Rising,
            daq.DAQmx_Val_ContSamps if etrig else daq.DAQmx_Val_FiniteSamps,
            pts)
        daq.DAQmxCfgDigEdgeStartTrig(task, "/Dev2/PFI0", daq.DAQmx_Val_Rising)
        AONwritten = daq.int32()
        daq.DAQmxWriteAnalogF64(task,pts, False, self.RWTimeout, daq.DAQmx_Val_GroupByChannel, ysig, daq.byref(AONwritten),None)
        daq.DAQmxStartTask(task)
        #print("Ramping from "+str(np.round(prev_volt,5))+"V to "+str(np.round(new_volt,5))+"V in "+str(time0)+"s.")
        
        if forever:
            return task
        else:
            time.sleep(duration)
            daq.DAQmxStopTask(task)
            daq.DAQmxClearTask(task)

        return 1
        
    def stopac(self, task):
        daq.DAQmxStopTask(task)
        daq.DAQmxClearTask(task)
        self.set_chan_voltage(5, 0, buff = 100)
    
        