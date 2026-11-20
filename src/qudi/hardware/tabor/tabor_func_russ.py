import numpy as np
import visa
import warnings
import matplotlib.pyplot as plt
import h5py
import time
from scipy.interpolate import interp1d




class TaborAWG():
    """TaborAWG:
        module.Class: 'tabor.tabor_func_russ.TaborAWG'
        address: 'TCPIP::192.168.68.176::5025::SOCKET'
    """ 
        
        
    def __init__(self):
        print("Connect to Tabor AWG.")
        rm = visa.ResourceManager()
        # tbname =  'TCPIP::192.168.68.175::5025::SOCKET'
        tbname =  'TCPIP::192.168.68.176::5025::SOCKET'
        self.tawg = rm.open_resource(tbname, read_termination = "\n", write_termination = "\n")
        devstring = self.tawg.query("*IDN?")
        self.tawg.write("*CLS")
        print(devstring)
        
        for cho in [1,2,3,4]:
            self.send_cmd(':INST:CHAN '+str(cho))
            self.tawg.query(":INIT:CONT OFF; *OPC?")
            self.tawg.query(":TRIG:SEL TRG1; *OPC?")
            self.tawg.query(":TRIG:STAT ON; *OPC?")
            # self.tawg.query(":TRIG:STAT OFF; *OPC?")
            self.tawg.query(":TRIG:MODE IMM; *OPC?")
            self.tawg.query(":TRIG:LTJ ON; *OPC?")
            status = self.tawg.query(":TRIG:STAT?")
            
            self.tawg.query(":TRIG:SOUR:ENAB TRG1; *OPC?")
            
            self.tawg.query(":TRIG:LEV 0.5; *OPC?")
            self.tawg.query(":TRIG:WIDT 0E-09; *OPC?")
            self.tawg.query(":TRIG:COUN 1; *OPC?")
            print(status)
        

    def send_cmd(self, cmd_str, paranoia_level=1):

        if paranoia_level == 1:
            ask_str = cmd_str.rstrip()
            if len(ask_str) > 0:
                ask_str += '; *OPC?'
            else:
                ask_str = '*OPC?'
            _ = self.tawg.query(ask_str)

            

        elif paranoia_level >= 2:
            ask_str = cmd_str.rstrip()
            if len(ask_str) > 0:
                ask_str += '; :SYST:ERR?'
            else:
                ask_str = ':SYST:ERR?'
            syst_err = self.tawg.query(ask_str)
            try:
                errnb = int(syst_err.split(',')[0])
            except visa.VisaIOError:
                errnb = -1
            if errnb != 0:
                syst_err = syst_err.rstrip()
                wrn_msg = 'ERR: "{0}" after CMD: "{1}"'.format(syst_err, cmd_str)
                _ = self.tawg.query('*CLS; *OPC?')  # clear the error-list
                if paranoia_level >= 3:
                    raise NameError(wrn_msg)
                else:
                    warnings.warn(wrn_msg)

        else:
            self.tawg.write(cmd_str)
            # vi.visalib.viFlush(vi.session, vc.VI_WRITE_BUF)
    def On(self):
        print("ON called")
        for ch in range(4):
            time.sleep(0.5)
            self.send_cmd(':INST:CHAN '+str(ch+1))
            time.sleep(0.5)
            self.send_cmd('OUTP ON')
            
        
    def set_amplitude(self, channel = 1, amplitude = 0):

        self.send_cmd(':INST:CHAN '+str(channel))
        self.send_cmd(":SOUR:VOLT "+str(amplitude))

    def set_awg_sample_rate(self, awg_sample_rate):
        self.awg_samp_rate = awg_sample_rate
        self.send_cmd(":SOUR:FREQ:RAST {}".format(awg_sample_rate), paranoia_level = 0)
        
    def get_awg_sample_rate(self):

        self.awg_samp_rate = float(self.tawg.query(":SOUR:FREQ:RAST?"))
        return self.awg_samp_rate

    def Off(self):
       print("OFF called")
       for ch in range(4):
        self.send_cmd(':INST:CHAN '+str(ch))
        self.send_cmd('OUTP OFF')
       # signal = np.zeros(192)
       # bitness = 14

       # max_dac = (2 ** bitness - 1)
       # half_dac = max_dac / 2.0
        
       # y = signal + half_dac
       # wav = y.astype(np.uint16)
        
       # cmd1 = ':TRAC:DEF {0}, {1}'.format(1, len(signal))
       # self.send_cmd(cmd1, paranoia_level = 0)
        
       # cmd2 = ':TRAC:SEL {0}'.format(1)
       # self.send_cmd(cmd2, paranoia_level = 0)
        
       # self.tawg.write_binary_values(':TRAC:DATA', wav, 'H')
       # print("All waveforms deleted.")

    def generate_pure_tone(self, f0, pv):     
        self.send_cmd('OUTP OFF')
        self.send_cmd(':TRAC:DEL ALL')
        self.send_cmd(":INIT:CONT:STAT ON")
        self.send_cmd(":TRIG:SEQ:SOUR INT")
        self.send_cmd(":SOUR:FREQ{}".format(f0))
        self.send_cmd(":SOUR:VOLT{}".format(pv))       
         
    def generate_pulse(self, f0, ton, toff, phase = 0):
        sampfreq = int(100*f0)
        
        self.send_cmd('OUTP OFF')
        self.send_cmd(':TRAC:DEL ALL')
       
        self.send_cmd(":SOUR:FUNC:MODE USER")
        
        self.send_cmd(":INIT:CONT:STAT OFF")
        self.send_cmd(":TRIG:SEQ:SOUR EXT")
        self.send_cmd(":TRIG:SEQ:COUN 1")
        self.send_cmd(":SOUR:FREQ:RAST {}".format(sampfreq), paranoia_level = 0)
        
        dt = 1/sampfreq
        n_toff = int(toff/dt)
        sig_off = np.zeros(n_toff)
        tons = np.arange(0, ton, dt)
        sig_on = np.sin(tons * 2*np.pi*f0 + phase)
        signal = np.hstack((sig_off, sig_on, sig_off))
        full_signal = np.hstack((signal, np.zeros(16 - np.mod(len(signal),16))))
        
        # bitness = 14
        bitness = 16

        max_dac = (2 ** bitness - 1)
        half_dac = max_dac / 2.0
        
        y = (full_signal + 1 ) * half_dac
        y = np.round(y)
        y = np.clip(y, -max_dac, max_dac)
        wav = y.astype(np.uint16)
        
        cmd = ':TRAC:DEF {0}, {1}'.format(1, len(full_signal))
        self.send_cmd(cmd, paranoia_level = 0)
        
        cmd = ':TRAC:SEL {0}'.format(1)
        self.send_cmd(cmd, paranoia_level = 0)
        
        self.tawg.write_binary_values(':TRAC:DATA', wav, 'H')

    def generate_rabi(self,tau_start, tau_step, num_of_points, f0, phase = 0):
        sampfreq = int(10*f0)
        dt = 1/sampfreq
        
        laser_time = 3e-6
        wait_time = 1e-6
        buffer_time = 10e-6
        
        self.send_cmd('OUTP OFF')
        #self.send_cmd(':TRAC:DEL ALL')
        
        self.send_cmd(":SOUR:FUNC:MODE USER")
        
        self.send_cmd(":INIT:CONT:STAT OFF")
        self.send_cmd(":TRIG:SEQ:SOUR EXT")
        self.send_cmd(":TRIG:SEQ:COUN 1")
        self.send_cmd(":SOUR:FREQ:RAST {}".format(sampfreq), paranoia_level = 0)
        
        laser_element = np.zeros(int(laser_time/dt))
        wait_element = np.zeros(int(wait_time/dt))
        buffer_element = np.zeros(int(buffer_time/dt))
        
        pulse_times_array = np.arange(tau_start, tau_step * num_of_points, tau_step)
        full_array = []
        
        for tt in pulse_times_array:
            pulse_times = np.arange(tau_start, tt, dt)
            pulse_element = np.sin(pulse_times*2*np.pi*f0 + phase)
            seq_array = np.hstack((laser_element, wait_element, pulse_element, buffer_element))
            
            full_array = np.hstack((full_array,seq_array))
            
        signal_array = np.hstack((full_array, np.zeros(16 - np.mod(len(full_array),16))))
        times_array = np.arange(0,len(signal_array)*dt,dt)
        
        bitness = 14

        max_dac = (2 ** bitness - 1)
        half_dac = max_dac / 2.0
        
        y = (signal_array + 1 ) * half_dac
        y = np.round(y)
        y = np.clip(y, -max_dac, max_dac)
        wav = y.astype(np.uint16)
        
        cmd = ':TRAC:DEF {0}, {1}'.format(1, len(signal_array))
        self.send_cmd(cmd, paranoia_level = 0)
        
        cmd = ':TRAC:SEL {0}'.format(1)
        self.send_cmd(cmd, paranoia_level = 0)
        
        self.tawg.write_binary_values(':TRAC:DATA', wav, 'H')
        
        return times_array, signal_array

    def pulse_to_tabor(self, filename):
        with h5py.File(filename, "r") as f:
            print("Keys: %s" % f.keys())
            a_group_key = list(f.keys())[0]
            data = list(f[a_group_key])
            
        data = np.array([data])
        data = data[0]
        data = np.hstack((data,np.zeros(16 - np.mod(len(data),16))))
        
        amp = max(data)
        
        sampfreq = int(1e9)
        
        self.send_cmd('OUTP OFF')
        self.send_cmd(':TRAC:DEL ALL')
        
        # self.send_cmd(":SOUR:FUNC:MODE USER")
        self.send_cmd(":SOUR:FUNC:MODE USER")
        
        self.send_cmd(":INIT:CONT:STAT OFF")
        self.send_cmd(":TRIG:SEQ:SOUR EXT")
        self.send_cmd(":TRIG:SEQ:COUN 1")
        self.send_cmd(":SOUR:FREQ:RAST {}".format(sampfreq), paranoia_level = 0)
        
        bitness = 16
        # bitness = 14

        max_dac = (2 ** bitness - 1)
        half_dac = max_dac / 2.0
        
        y = (data + amp ) * half_dac
        y = np.round(y)
        y = np.clip(y, -max_dac, max_dac)
        wav = y.astype(np.uint16)
        
        cmd = ':TRAC:DEF {0}, {1}'.format(1, len(data))
        self.send_cmd(cmd, paranoia_level = 0)
        
        cmd = ':TRAC:SEL {0}'.format(1)
        self.send_cmd(cmd, paranoia_level = 0)
        
        self.tawg.write_binary_values(':TRAC:DATA', wav, 'H')

    def analog_samples_tabor(self, analog_samples):
        chan_dic = {"a_ch1":1, "a_ch2":2, "a_ch3":3, "a_ch4":4}
        # with h5py.File('analogchanneltest-r.h5', 'w') as hf:
            # for key in analog_samples:
                # hf.create_dataset(key, data = analog_samples[key])
        wavdic = {}
        for cho in list(analog_samples.keys()):
            data =[analog_samples[cho]]
            print('Number of Original Analog Samples ' + str(len(data[0])))

            streamersampfreq = int(1e9)
            sampfreq = int(self.awg_samp_rate)    
            ratio = int(streamersampfreq/sampfreq)
        
            if ratio >=1:
            
            
                data = np.array(data)
                data = ((data[0])[250:])[::ratio]#this removes the AWG trigger element to ensure sync between the two channels.
                print('Undersampling. New Analog Samples ' + str(len(data)))
            elif ratio <1:
                data = np.array(data)
                data = ((data[0])[250:])
                times = np.arange(0,len(data), 1)#times sampled at 1ns
                f = interp1d(times, data)
                timestep = 1.0e9/sampfreq #in ns
                newtimes = np.arange(0, max(times), timestep)
                newdata = f(newtimes)
                data = newdata
                print('Oversampling. New Analog Samples ' + str(len(data)))
            
        
            data = np.hstack((data,np.zeros(32 - np.mod(len(data),32))))
            # if len(data) >= 512e3:
                # print("Number of samples exceeds AWG memory. Adjust sample freq.")
            amp = max(np.abs(data))    
                
            self.set_amplitude(channel = chan_dic[cho], amplitude = amp)
            # Get the available memory in bytes of wavform-data (per DDR):
            
            self.send_cmd(':INST:CHAN '+str(chan_dic[cho])) # selects channel on AWG for commands below
            print('SELECTING CHANNEL') # selects channel on AWG for commands below
            print(':INST:SEL '+str(chan_dic[cho])) # selects channel on AWG for commands below


        
            # self.send_cmd('OUTP OFF')
            #self.send_cmd(':TRAC:DEL ALL', paranoia_level = 2)
            self.send_cmd(":SOUR:FUNC:MODE ARB")
            self.send_cmd(":SOUR:FUNC:MODE:SEGM "+str(chan_dic[cho]))

            resp = self.tawg.query(":TRACe:FREE?")
            arbmem_capacity = int(resp)
            print("Available memory per DDR: {0:,} wave-bytes".format(arbmem_capacity))

        
            #self.send_cmd(":INIT:CONT:STAT OFF")
            #self.send_cmd(":TRIG:SEQ:SOUR EXT")
            #self.send_cmd(":TRIG:SEQ:COUN 1")
            self.send_cmd(":SOUR:FREQ:RAST {}".format(sampfreq), paranoia_level = 0)
        
            bitness = 16
            max_dac = (2 ** bitness - 1)
            half_dac = max_dac / 2.0
            
            if amp == 0:
                amp = 1
        
            y = (data/amp + 1 ) * half_dac
            y = np.round(y)
            y = np.clip(y, -max_dac, max_dac)
            wav = y.astype(np.uint16)
            wavdic[cho] = wav
            
            # save wav to dict
        
            cmd = ':TRAC:DEF {0}, {1}'.format(chan_dic[cho], len(data))
            self.send_cmd(cmd, paranoia_level = 1)
        
            cmd = ':TRAC:SEL {0}'.format(chan_dic[cho])
            self.send_cmd(cmd, paranoia_level = 1)
            self.tawg.timeout = 10000
            t_write=time.time()
            self.tawg.write_binary_values('*OPC?;:TRAC:DATA', wav, 'H')
            print('time taken to write to awg: '+str(time.time() - t_write)+' seconds')
            status = 0
            while status <1:
                print("Trying...")
                status = int(self.tawg.read())
                print("Done.")
            print("Finished sending samples to AWG.")  

            resp = self.tawg.query(":TRACe:FREE?")
            arbmem_capacity2 = int(resp)
            if arbmem_capacity2 != arbmem_capacity:
                print("Programming successful.")
                print("After prgm:: {0:,} wave-bytes".format(arbmem_capacity2)) 
            else:
                print("WARNING! no change in waveform memory. Ignore if new waveform is identical to old.")
        
        #insert save h5
        with h5py.File('testing_awg_pahses.h5', 'w') as hf:
            for key in wavdic:
                hf.create_dataset(key, data = wavdic[key])
                
        return len(data)
        # def getphases(sequence):
            # phases = []
            # for element in sequence:
                # if element[0] == 'RF':
                    # phases.append(element[-1])
            # return phases      


        # cmd = ':SOUR:FUNC:MODE:USER'
        # send_cmd(tb,cmd, paranoia_level=2)
