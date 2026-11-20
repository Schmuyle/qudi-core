# -*- coding: utf-8 -*-

"""
This file contains the Qudi hardware dummy for pulsing devices.

"""

import time
from collections import OrderedDict
import numpy as np
import h5py
import sys

# ip_hostname='192.168.68.132' # edit this line to use a specific Pulse Streamer IP address
from qudi.core.module import Base
from qudi.hardware.swabian_instruments.pulse_streamer_jrpc import PulseStreamer # import Pulse Streamer wrapper class

from qudi.hardware.swabian_instruments.pulse_streamer_jrpc import Start, Mode# import enum types  

from qudi.hardware.swabian_instruments.Sequence import Sequence

from qudi.hardware.tabor.tabor_func_russ import TaborAWG

from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption
from qudi.core.statusvariable import StatusVar
from qudi.interface.pulser_interface import PulserInterface, PulserConstraints


class PulseStreamerAWG(PulserInterface):
    """ e

    Be careful in adjusting the method names in that class, since some of them
    are also connected to the mwsourceinterface (to give the AWG the possibility
    to act like a microwave source).

    Example config for copy-paste:

    pulser_dummy:
        module.Class: 'pulser_dummy.PulserDummy'

    """
    _modclass = 'PulseStreamerAWG'
    _modtype = 'hardware'
    _pulsestreamer_ip = ConfigOption('pulsestreamer_ip', '192.168.68.132', missing='warn')
    _awg_ip = ConfigOption('taborawg_ip', '192.168.68.1XX', missing='warn')

    activation_config = StatusVar(default=None)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

        

        self.connected = False
        self.sample_rate = 1e9

        # Deactivate all channels at first:
        # self.channel_states = {'d_ch1': False, 'd_ch2': False, 'd_ch3': False, 'd_ch4': False,
                               # 'd_ch5': False, 'd_ch6': False, 'd_ch7': False, 'd_ch8': False, 'a_ch1': False, 'a_ch2': False}
        self.channel_states = {'d_ch1': False, 'd_ch2': False, 'd_ch3': False, 'd_ch4': False,
                               'd_ch5': False, 'd_ch6': False, 'd_ch7': False, 'd_ch8': False, 'a_ch1': False, 'a_ch2': False,'a_ch3': False, 'a_ch4': False}

        # for each analog channel one value
        # self.amplitude_dict = {'a_ch1': 1.0, 'a_ch2': 1.0}
        # self.offset_dict = {'a_ch1': 0.0, 'a_ch2': 0.0}
        self.amplitude_dict = {'a_ch1': 1.0, 'a_ch2': 1.0, 'a_ch3': 1.0, 'a_ch4': 1.0}
        self.offset_dict = {'a_ch1': 0.0, 'a_ch2': 0.0, 'a_ch3': 0.0, 'a_ch4': 0.0}

        # for each digital channel one value
        self.digital_high_dict = {'d_ch1': 3.3, 'd_ch2': 3.3, 'd_ch3': 3.3, 'd_ch4': 3.3,
                                  'd_ch5': 3.3, 'd_ch6': 3.3, 'd_ch7': 3.3, 'd_ch8': 3.3}
        self.digital_low_dict = {'d_ch1': 0.0, 'd_ch2': 0.0, 'd_ch3': 0.0, 'd_ch4': 0.0,
                                 'd_ch5': 0.0, 'd_ch6': 0.0, 'd_ch7': 0.0, 'd_ch8': 0.0}

        self.waveform_set = set()
        self.sequence_dict = dict()

        self.current_loaded_assets = dict()

        self.use_sequencer = False
        self.interleave = False


        self.pulser = PulseStreamer(self._pulsestreamer_ip)
        self.tawg = TaborAWG()#initialise and connect to AWG

        start = Start.HARDWARE_RISING

        mode = Mode.NORMAL

        self.pulser.setTrigger(start=start, mode=mode)


        self.current_status = 0    # that means off, not running.

    def on_activate(self):
        """ Initialisation performed during activation of the module.
        """
        self.connected = True


        self.pulser_off() #also turns awg off


        self.current_status = 0
        if self.activation_config is None:
            self.activation_config = self.get_constraints().activation_config['config0']

    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        self.connected = False

    def get_constraints(self):
        """
        Retrieve the hardware constrains from the Pulsing device.

        @return constraints object: object with pulser constraints as attributes.

        Provides all the constraints (e.g. sample_rate, amplitude, total_length_bins,
        channel_config, ...) related to the pulse generator hardware to the caller.

            SEE PulserConstraints CLASS IN pulser_interface.py FOR AVAILABLE CONSTRAINTS!!!

        If you are not sure about the meaning, look in other hardware files to get an impression.
        If still additional constraints are needed, then they have to be added to the
        PulserConstraints class.

        Each scalar parameter is an ScalarConstraints object defined in cor.util.interfaces.
        Essentially it contains min/max values as well as min step size, default value and unit of
        the parameter.

        PulserConstraints.activation_config differs, since it contain the channel
        configuration/activation information of the form:
            {<descriptor_str>: <channel_set>,
             <descriptor_str>: <channel_set>,
             ...}

        If the constraints cannot be set in the pulsing hardware (e.g. because it might have no
        sequence mode) just leave it out so that the default is used (only zeros).
        """
        constraints = PulserConstraints()

        if self.interleave:
            constraints.sample_rate.min = 12.0e9
            constraints.sample_rate.max = 24.0e9
            constraints.sample_rate.step = 4.0e8
            constraints.sample_rate.default = 24.0e9
        else:
            constraints.sample_rate.min = 1e9
            constraints.sample_rate.max = 1e9
            constraints.sample_rate.step = 0
            constraints.sample_rate.default = 1e9

        constraints.a_ch_amplitude.min = 0.02
        constraints.a_ch_amplitude.max = 2.0
        constraints.a_ch_amplitude.step = 0.001
        constraints.a_ch_amplitude.default = 2.0

        constraints.a_ch_offset.min = -1.0
        constraints.a_ch_offset.max = 1.0
        constraints.a_ch_offset.step = 0.001
        constraints.a_ch_offset.default = 0.0

        constraints.d_ch_low.min = 0.0
        constraints.d_ch_low.max = 0.0
        constraints.d_ch_low.step = 0.0
        constraints.d_ch_low.default = 0.0

        constraints.d_ch_high.min = 3.3
        constraints.d_ch_high.max = 3.3
        constraints.d_ch_high.step = 0.0
        constraints.d_ch_high.default = 3.3

        constraints.waveform_length.min = 1
        constraints.waveform_length.max = 134217728
        constraints.waveform_length.step = 1
        constraints.waveform_length.default = 1



        activation_config = OrderedDict()
        # activation_config['config0'] = {'d_ch1', 'd_ch2', 'd_ch3', 'd_ch4', 'd_ch5', 'd_ch6', 'd_ch7','d_ch8','a_ch1', 'a_ch2'}
        activation_config['config0'] = {'d_ch1', 'd_ch2', 'd_ch3', 'd_ch4', 'd_ch5', 'd_ch6', 'd_ch7','d_ch8','a_ch1', 'a_ch2','a_ch3', 'a_ch4'}
       
        constraints.activation_config = activation_config

        return constraints

    def pulser_on(self):
        """ Switches the pulsing device on.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 0:
            self.current_status = 1
            self.log.info('Pulser: Switch on the Output.')

            
            start = Start.SOFTWARE #SW trigger
            mode = Mode.SINGLE #1 trigger executes whole seq

            
            self.pulser.setTrigger(start=start, mode=mode)
            self.pulser.stream(self.sequence_to_run, 'INFINITE',(0,[],0,0))

            self.pulser.startNow()
            self.tawg.On() #here we do AWG on. The AWG trigger is emitted from the streamer to turn it on.
            
            return 0
        else:
            return -1
			
			
			
    def pulser_on_hwt(self):
        """ Hardware triggered operation

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 0:
            self.current_status = 1
            self.log.info('Pulser: Switch on the Output. Hardware trigger engaged.')

            
            start = Start.HARDWARE_RISING_AND_FALLING
            # mode = Mode.SINGLE
            mode = Mode.NORMAL
            
            self.pulser.setTrigger(start=start, mode=mode)
            self.pulser.stream(self.sequence_to_run, 1,(0,[],0,0))
            self.pulser.startNow()#starts awg in the same way
            
            return 0
        else:
            return -1
            
            
            
            
    def laser_on(self):
        """ Switches the pulsing device on.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 0:
            self.current_status = 1
            self.log.info('Pulser: Switch on the laser, mw.')

            self.pulser.constant((0,[0,1],0.0,0)) 
            self.pulser.startNow()
            return 0
        else:
            return -1
            
    def laser_off(self):
        """ Switches the pulsing device on.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 1:
            self.current_status = 0
            self.log.info('Pulser: Switch off the laser, mw')
            self.pulser.reset()
            self.pulser.constant((0,[],0,0)) 
            self.log.info('Pulser: Channel 1 and 2 ON.')
            return 0
        else:
            return -1

    def pulser_off(self):
        """ Switches the pulsing device off.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 1:
            self.current_status = 0
            self.pulser.reset()
            self.tawg.Off()

            #set constant state of the device
            self.pulser.constant((0,[],0,0)) 

            self.log.info('Pulser: Channel 1 and 2 OFF.')
        return 0



    def write_waveform(self, name, analog_samples, digital_samples, is_first_chunk, is_last_chunk,
                       total_number_of_samples, fold_sequence = False, fold_channel = 'd_ch5'):
        """
        Write a new waveform or append samples to an already existing waveform on the device memory.
        The flags is_first_chunk and is_last_chunk can be used as indicator if a new waveform should
        be created or if the write process to a waveform should be terminated.

        NOTE: All sample arrays in analog_samples and digital_samples must be of equal length!

        @param str name: the name of the waveform to be created/append to
        @param dict analog_samples: keys are the generic analog channel names (i.e. 'a_ch1') and
                                    values are 1D numpy arrays of type float32 containing the
                                    voltage samples.
        @param dict digital_samples: keys are the generic digital channel names (i.e. 'd_ch1') and
                                     values are 1D numpy arrays of type bool containing the marker
                                     states.
        @param bool is_first_chunk: Flag indicating if it is the first chunk to write.
                                    If True this method will create a new empty wavveform.
                                    If False the samples are appended to the existing waveform.
        @param bool is_last_chunk:  Flag indicating if it is the last chunk to write.
                                    Some devices may need to know when to close the appending wfm.
        @param int total_number_of_samples: The number of sample points for the entire waveform
                                            (not only the currently written chunk)

        @return (int, list): Number of samples written (-1 indicates failed process) and list of
                             created waveform names
        """
        waveforms = list()

        if len(analog_samples) > 0:
            number_of_samples = len(analog_samples[list(analog_samples)[0]])
        elif len(digital_samples) > 0:
            number_of_samples = len(digital_samples[list(digital_samples)[0]])
        else:
            self.log.error('No analog or digital samples passed to write_waveform method in dummy '
                           'pulser.')
            return -1, waveforms

        for chnl, samples in analog_samples.items():
            if len(samples) != number_of_samples:
                self.log.error('Unequal length of sample arrays for different channels in dummy '
                               'pulser.')
                return -1, waveforms
        for chnl, samples in digital_samples.items():
            if len(samples) != number_of_samples:
                self.log.error('Unequal length of sample arrays for different channels in dummy '
                               'pulser.')
                return -1, waveforms

        # Determine if only digital samples are active. In that case each channel will get a
        # waveform. Otherwise only the analog channels will have a waveform with digital channel
        # samples included (as it is the case in Tektronix and Keysight AWGs).
        # Simulate a 1Gbit/s transfer speed. Assume each analog waveform sample is 5 bytes large
        # (4 byte float and 1 byte marker bitmask). Assume each digital waveform sample is 1 byte.
        if len(analog_samples) > 0:
            for chnl in analog_samples:
                waveforms.append(name + chnl[1:])
                
        else:
            for chnl in digital_samples:
                waveforms.append(name + chnl[1:])
                

        self.waveform_set.update(waveforms)
        

        chan = list(digital_samples) #PB stuff
        chan.sort() #PB stuff
        chunk_length = len(digital_samples[chan[0]]) #PB stuff
        self._current_activation_config = chan #PB stuff
        t_gen = time.time()
        print('____________________________________')
        print('starting gen_streamer_sequence')
        self._current_ps_waveform = self._gen_streamer_seq(digital_samples, analog_samples)
        print('generating streamer sequence duration: '+str(time.time() - t_gen)+' seconds')
        print("Sequence sampled. Programming instruments.")
        self._current_ps_waveform_name = name
        seq = Sequence()# this is purely a Pulsestreamer thing and can be ignored for the AWG
        count_analog_runs = 0
        for key, seq_ps in self._current_ps_waveform.items():
            if key.startswith('d'):
                channel_ps = int(key.split('d_ch')[1])-1
                seq.setDigitalChannel(channel_ps, seq_ps)
                count_analog_runs = 0
            if key.startswith('a'):
                if count_analog_runs == 0:
                    channel_ps = int(key.split('a_ch')[1])-1
                    numsamps = self.tawg.analog_samples_tabor(analog_samples)
                    if numsamps >= 4e9:
                        self.log.error('N = '+str(numsamps)+' Analog samples exceeds AWG memory. Adjust sample freq. to ensure N <512e3')
                    count_analog_runs = 1
        self.sequence_to_run = seq.getSequence()
        self.log.info('Waveforms with nametag "{0}" written on pulsestreamer.'.format(name))
        return number_of_samples, waveforms,
        


    def get_waveform_names(self):
        """ Retrieve the names of all uploaded waveforms on the device.

        @return list: List of all uploaded waveform name strings in the device workspace.
        """
        return list(self.waveform_set)



    def delete_waveform(self, waveform_name):
        """ Delete the waveform with name "waveform_name" from the device memory.

        @param str waveform_name: The name of the waveform to be deleted
                                  Optionally a list of waveform names can be passed.

        @return list: a list of deleted waveform names.
        """
        if isinstance(waveform_name, str):
            waveform_name = [waveform_name]

        deleted_waveforms = list()
        for waveform in waveform_name:
            if waveform in self.waveform_set:
                self.waveform_set.remove(waveform)
                deleted_waveforms.append(waveform)

        return deleted_waveforms



    def load_waveform(self, load_dict):
        """ Loads a waveform to the specified channel of the pulsing device.
        For devices that have a workspace (i.e. AWG) this will load the waveform from the device
        workspace into the channel.
        For a device without mass memory this will make the waveform/pattern that has been
        previously written with self.write_waveform ready to play.

        @param load_dict:  dict|list, a dictionary with keys being one of the available channel
                                      index and values being the name of the already written
                                      waveform to load into the channel.
                                      Examples:   {1: rabi_ch1, 2: rabi_ch2} or
                                                  {1: rabi_ch2, 2: rabi_ch1}
                                      If just a list of waveform names if given, the channel
                                      association will be invoked from the channel
                                      suffix '_ch1', '_ch2' etc.

        @return (dict, str): Dictionary with keys being the channel number and values being the
                             respective asset loaded into the channel, string describing the asset
                             type ('waveform' or 'sequence')
        """
        if isinstance(load_dict, list):
            new_dict = dict()
            for waveform in load_dict:
                channel = int(waveform.rsplit('_ch', 1)[1])
                new_dict[channel] = waveform
            load_dict = new_dict
        print('start loading waveform')
        # Determine if the device is purely digital and get all active channels
        analog_channels = [chnl for chnl in self.activation_config if chnl.startswith('a')]
        digital_channels = [chnl for chnl in self.activation_config if chnl.startswith('d')]
        pure_digital = len(analog_channels) == 0

        # Check if waveforms are present in virtual dummy device memory and specified channels are
        # active. Create new load dict.
        new_loaded_assets = dict()
        for channel, waveform in load_dict.items():
            if waveform not in self.waveform_set:
                self.log.error('Loading failed. Waveform "{0}" not found on device memory.'
                               ''.format(waveform))
                return self.current_loaded_assets
            if pure_digital:
                if 'd_ch{0:d}'.format(channel) not in digital_channels:
                    self.log.error('Loading failed. Digital channel {0:d} not active.'
                                   ''.format(channel))
                    return self.current_loaded_assets
            else:
                if 'a_ch{0:d}'.format(channel) not in analog_channels:
                    self.log.error('Loading failed. Analog channel {0:d} not active.'
                                   ''.format(channel))
                    return self.current_loaded_assets
            new_loaded_assets[channel] = waveform
        self.current_loaded_assets = new_loaded_assets
        # str_channels = [int
        
        
        
        
        
        
        print('end loading waveform')
        return self.get_loaded_assets()



    def get_loaded_assets(self):
        """
        Retrieve the currently loaded asset names for each active channel of the device.
        The returned dictionary will have the channel numbers as keys.
        In case of loaded waveforms the dictionary values will be the waveform names.
        In case of a loaded sequence the values will be the sequence name appended by a suffix
        representing the track loaded to the respective channel (i.e. '<sequence_name>_1').

        @return (dict, str): Dictionary with keys being the channel number and values being the
                             respective asset loaded into the channel,
                             string describing the asset type ('waveform' or 'sequence')
        """
        # Determine if it's a waveform or a sequence
        asset_type = None
        for asset_name in self.current_loaded_assets.values():
            if 'ch' in asset_name.rsplit('_', 1)[1]:
                current_type = 'waveform'
            else:
                current_type = 'sequence'

            if asset_type is None or asset_type == current_type:
                asset_type = current_type
            else:
                self.log.error('Unable to determine loaded asset type. Mixed naming convention '
                               'assets loaded (waveform and sequence tracks).')
                return dict(), ''

        return self.current_loaded_assets, asset_type

    def clear_all(self):
        """ Clears all loaded waveform from the pulse generators RAM.

        @return int: error code (0:OK, -1:error)

        Unused for digital pulse generators without storage capability
        (PulseBlaster, FPGA).
        """
        self.current_loaded_assets = dict()
        self.waveform_set = set()
        self.sequence_dict = dict()
        return 0

    def get_status(self):
        """ Retrieves the status of the pulsing hardware

        @return (int, dict): inter value of the current status with the
                             corresponding dictionary containing status
                             description for all the possible status variables
                             of the pulse generator hardware
        """
        status_dic = {-1: 'Failed Request or Communication', 0: 'Device has stopped, but can receive commands.',
                      1: 'Device is active and running.'}
        # All the other status messages should have higher integer values
        # then 1.
        return self.current_status, status_dic

    def get_sample_rate(self):
        """ Get the sample rate of the pulse generator hardware

        @return float: The current sample rate of the device (in Hz)

        Do not return a saved sample rate in a class variable, but instead
        retrieve the current sample rate directly from the device.
        """

        return self.sample_rate
        
    def get_awg_sample_rate(self):
        """ Get the sample rate of the pulse generator hardware

        @return float: The current sample rate of the device (in Hz)

        Do not return a saved sample rate in a class variable, but instead
        retrieve the current sample rate directly from the device.
        """
        self.awg_sample_rate = self.tawg.get_awg_sample_rate()
        return self.awg_sample_rate

    def set_sample_rate(self, sample_rate):
        """ Set the sample rate of the pulse generator hardware

        @param float sample_rate: The sampling rate to be set (in Hz)

        @return float: the sample rate returned from the device.

        Note: After setting the sampling rate of the device, retrieve it again
              for obtaining the actual set value and use that information for
              further processing.
        """
        constraint = self.get_constraints().sample_rate
        if sample_rate > constraint.max:
            self.sample_rate = constraint.max
        elif sample_rate < constraint.min:
            self.sample_rate = constraint.min
        else:
            self.sample_rate = sample_rate
        return self.sample_rate

    def set_awg_sample_rate(self, sample_rate):
        """ Set the sample rate of the pulse generator hardware

        @param float sample_rate: The sampling rate to be set (in Hz)

        @return float: the sample rate returned from the device.

        Note: After setting the sampling rate of the device, retrieve it again
              for obtaining the actual set value and use that information for
              further processing.
        """
        self.tawg.set_awg_sample_rate(sample_rate)
        self.awg_sample_rate = self.get_awg_sample_rate()
        return self.awg_sample_rate

    def get_analog_level(self, amplitude=None, offset=None):
        """ Retrieve the analog amplitude and offset of the provided channels.

        @param list amplitude: optional, if the amplitude value (in Volt peak to
                               peak, i.e. the full amplitude) of a specific
                               channel is desired.
        @param list offset: optional, if the offset value (in Volt) of a
                            specific channel is desired.

        @return: (dict, dict): tuple of two dicts, with keys being the channel
                               descriptor string (i.e. 'a_ch1') and items being
                               the values for those channels. Amplitude is
                               always denoted in Volt-peak-to-peak and Offset
                               in volts.

        Note: Do not return a saved amplitude and/or offset value but instead
              retrieve the current amplitude and/or offset directly from the
              device.

        If nothing (or None) is passed then the levels of all channels will be
        returned. If no analog channels are present in the device, return just
        empty dicts.

        Example of a possible input:

            amplitude = ['a_ch1', 'a_ch4'], offset = None

        to obtain the amplitude of channel 1 and 4 and the offset of all
        channels

            {'a_ch1': -0.5, 'a_ch4': 2.0}
            {'a_ch1': 0.0, 'a_ch2': 0.0, 'a_ch3': 1.0, 'a_ch4': 0.0}

        """
        # d1 = {'a_ch1': 1, 'a_ch2': 1}
        d1 = {'a_ch1': 1, 'a_ch2': 1, 'a_ch3': 1, 'a_ch4': 1}
        return d1, dict()

    def set_analog_level(self, amplitude=None, offset=None):
        """ Set amplitude and/or offset value of the provided analog channel(s).

        @param dict amplitude: dictionary, with key being the channel descriptor
                               string (i.e. 'a_ch1', 'a_ch2') and items being
                               the amplitude values (in Volt peak to peak, i.e.
                               the full amplitude) for the desired channel.
        @param dict offset: dictionary, with key being the channel descriptor
                            string (i.e. 'a_ch1', 'a_ch2') and items being the
                            offset values (in absolute volt) for the desired
                            channel.

        @return (dict, dict): tuple of two dicts with the actual set values for
                              amplitude and offset for ALL channels.

        If nothing is passed then the command will return the current
        amplitudes/offsets.

        Note: After setting the amplitude and/or offset values of the device,
              use the actual set return values for further processing.
        """
        return {}, {}

    def get_digital_level(self, low=None, high=None):
        """ Retrieve the digital low and high level of the provided channels.

        @param list low: optional, if a specific low value (in Volt) of a
                         channel is desired.
        @param list high: optional, if a specific high value (in Volt) of a
                          channel is desired.

        @return: (dict, dict): tuple of two dicts, with keys being the channel
                               number and items being the values for those
                               channels. Both low and high value of a channel is
                               denoted in (absolute) Voltage.

        Note: Do not return a saved low and/or high value but instead retrieve
              the current low and/or high value directly from the device.

        If no entries provided then the levels of all channels where simply
        returned. If no digital channels provided, return just an empty dict.

        Example of a possible input:
            low = ['d_ch1', 'd_ch4']
        to obtain the low voltage values of digital channel 1 an 4. A possible
        answer might be
            {'d_ch1': -0.5, 'd_ch4': 2.0} {}
        since no high request was performed.

        The major difference to analog signals is that digital signals are
        either ON or OFF, whereas analog channels have a varying amplitude
        range. In contrast to analog output levels, digital output levels are
        defined by a voltage, which corresponds to the ON status and a voltage
        which corresponds to the OFF status (both denoted in (absolute) voltage)

        In general there is no bijective correspondence between
        (amplitude, offset) and (value high, value low)!
        """
        if low is None:
            low = []
        if high is None:
            high = []

        if not low and not high:
            low_val = self.digital_low_dict
            high_val = self.digital_high_dict
        else:
            low_val = dict()
            high_val = dict()
            for d_ch in low:
                low_val[d_ch] = self.digital_low_dict[d_ch]
            for d_ch in high:
                high_val[d_ch] = self.digital_high_dict[d_ch]

        return low_val, high_val

    def set_digital_level(self, low=None, high=None):
        """ Set low and/or high value of the provided digital channel.

        @param dict low: dictionary, with key being the channel and items being
                         the low values (in volt) for the desired channel.
        @param dict high: dictionary, with key being the channel and items being
                         the high values (in volt) for the desired channel.

        @return (dict, dict): tuple of two dicts where first dict denotes the
                              current low value and the second dict the high
                              value.

        If nothing is passed then the command will return two empty dicts.

        Note: After setting the high and/or low values of the device, retrieve
              them again for obtaining the actual set value(s) and use that
              information for further processing.

        The major difference to analog signals is that digital signals are
        either ON or OFF, whereas analog channels have a varying amplitude
        range. In contrast to analog output levels, digital output levels are
        defined by a voltage, which corresponds to the ON status and a voltage
        which corresponds to the OFF status (both denoted in (absolute) voltage)

        In general there is no bijective correspondence between
        (amplitude, offset) and (value high, value low)!
        """
        if low is None:
            low = {}
        if high is None:
            high = {}
        self.log.warning('PulseStreamer logic level cannot be adjusted!')
        return 0

    def get_active_channels(self, ch=None):
        """ Get the active channels of the pulse generator hardware.

        @param list ch: optional, if specific analog or digital channels are
                        needed to be asked without obtaining all the channels.

        @return dict:  where keys denoting the channel number and items boolean
                       expressions whether channel are active or not.

        Example for an possible input (order is not important):
            ch = ['a_ch2', 'd_ch2', 'a_ch1', 'd_ch5', 'd_ch1']
        then the output might look like
            {'a_ch2': True, 'd_ch2': False, 'a_ch1': False, 'd_ch5': True, 'd_ch1': False}

        If no parameters are passed to this method all channels will be asked
        for their setting.
        """
        if ch is None:
            ch = []

        active_ch = {}

        if not ch:
            active_ch = self.channel_states

        else:
            for channel in ch:
                active_ch[channel] = self.channel_states[channel]

        return active_ch

    def set_active_channels(self, ch=None):
        """
        Set the active/inactive channels for the pulse generator hardware.
        The state of ALL available analog and digital channels will be returned
        (True: active, False: inactive).
        The actually set and returned channel activation must be part of the available
        activation_configs in the constraints.
        You can also activate/deactivate subsets of available channels but the resulting
        activation_config must still be valid according to the constraints.
        If the resulting set of active channels can not be found in the available
        activation_configs, the channel states must remain unchanged.

        @param dict ch: dictionary with keys being the analog or digital string generic names for
                        the channels (i.e. 'd_ch1', 'a_ch2') with items being a boolean value.
                        True: Activate channel, False: Deactivate channel

        @return dict: with the actual set values for ALL active analog and digital channels

        If nothing is passed then the command will simply return the unchanged current state.

        Note: After setting the active channels of the device, use the returned dict for further
              processing.

        Example for possible input:
            ch={'a_ch2': True, 'd_ch1': False, 'd_ch3': True, 'd_ch4': True}
        to activate analog channel 2 digital channel 3 and 4 and to deactivate
        digital channel 1. All other available channels will remain unchanged.
        """
        if ch is None:
            ch = {}
        old_activation = self.channel_states.copy()
        for channel in ch:
            self.channel_states[channel] = ch[channel]

        active_channel_set = {chnl for chnl, is_active in self.channel_states.items() if is_active}
        if active_channel_set not in self.get_constraints().activation_config.values():
            self.log.error('Channel activation to be set not found in constraints.\n'
                           'Channel activation unchanged.')
            self.channel_states = old_activation
        else:
            self.activation_config = active_channel_set

        return self.get_active_channels(ch=list(ch))



    def reset(self):
        """ Reset the device.

        @return int: error code (0:OK, -1:error)
        """
        self.__init__()
        self.connected = True
        self.pulser.reset()
        self.log.info('reset!')
        return 0

    def has_sequence_mode(self):
        """ Asks the pulse generator whether sequence mode exists.

        @return: bool, True for yes, False for no.
        """
        return False

    def _gen_streamer_seq(self, digital_samples, analog_samples):
        """ Converts sampled sequence to array of tuples for pulsestreamer

        returns dictionary, {'channel': seq}
        """
        channelsetd = [key for key in digital_samples.keys() if digital_samples[key].any()]
        channelseta = [key for key in analog_samples.keys() if analog_samples[key].any()]
        # print("channelsets")


        channelset = channelsetd + channelseta
        print('CHANNELS')
        seq_dict = {}
        LOW = 0
        HIGH = 1
        for channel in channelset:
            if channel.startswith('d'):
                print('I am doing '+str(channel))
                d = digital_samples[channel]

                zrs = np.zeros(100)#always buffer the start of every sequence with 100ns of off
                d = np.insert(d,0,zrs)#takes into account if channel on at t = 0
                d = np.append(d,zrs)#takes into account if channel ends on off
                aa = [x+1 for x, i in enumerate(np.diff(d)) if i != 0]

                dead_init = aa[0] #initial off time (always present due to zrs buffering)
                ontimes =np.diff(aa)[::2] #every second element starting at 0 of the diffed aa
                deadtimes = np.insert(np.diff(aa)[1::2],0,dead_init) #every second element starting at 1 of the diffed aa puls the initial dead time at the start.
                final_dead = len(d)-aa[-1]
                deadtimes = np.append(deadtimes,final_dead)

                # define sequences
                seq_mw     = []

                ontimes = np.append(ontimes,0) 
                for i in range(len(ontimes)):
                    seq_mw  += [(deadtimes[i], LOW), (ontimes[i], HIGH)]
            
                seq_mw += [(100,LOW)]
                seq_dict[channel] = seq_mw
            else:
                print("all analog programming done by Tabor AWG")  
                a = analog_samples[channel]#This is an array of 1 ns intervals. 
                #
                seq_dict[channel] = a

                # ontimes = np.append(ontimes,0)  
                # uniqueamps = np.append(uniqueamps,0)  
 
                # for i in range(len(ontimes)):
                    # seq_mw  += [(deadtimes[i], LOW), (ontimes[i], uniqueamps[i])]
            
                # seq_mw += [(100,LOW)]
                # seq_dict[channel] = seq_mw
                # print(seq_mw)
            # print(seq_dict.keys())
        return seq_dict
#UNUSED        
        
    def write_sequence(self, name, sequence_parameter_list):
        """
        Write a new sequence on the device memory.

        @param name: str, the name of the waveform to be created/append to
        @param sequence_parameter_list: list, contains the parameters for each sequence step and
                                        the according waveform names.

        @return: int, number of sequence steps written (-1 indicates failed process)
        """
        # Check if all waveforms are present on virtual device memory
        for waveform_tuple, param_dict in sequence_parameter_list:
            for waveform in waveform_tuple:
                if waveform not in self.waveform_set:
                    self.log.error('Failed to create sequence "{0}" due to waveform "{1}" not '
                                   'present in device memory.'.format(name, waveform))
                    return -1

        if name in self.sequence_dict:
            del self.sequence_dict[name]


        # Fill in sequence information
        for step, (wfm_tuple, seq_step) in enumerate(sequence_parameter_list, 1):
            self.log.debug('flag_trigger: {}'.format(seq_step.flag_trigger))
            self.log.debug('flag_high: {}'.format(seq_step.flag_high))

        self.sequence_dict[name] = len(sequence_parameter_list[0][0])
        time.sleep(1)
        

        self.log.info('Sequence with name "{0}" directly written on dummy pulser.'.format(name))
        return len(sequence_parameter_list)

    def get_interleave(self):
        """ Check whether Interleave is ON or OFF in AWG.

        @return bool: True: ON, False: OFF

        Unused for pulse generator hardware other than an AWG.
        """

        return self.interleave

    def set_interleave(self, state=False):
        """ Turns the interleave of an AWG on or off.

        @param bool state: The state the interleave should be set to
                           (True: ON, False: OFF)

        @return bool: actual interleave status (True: ON, False: OFF)

        Note: After setting the interleave of the device, retrieve the
              interleave again and use that information for further processing.

        Unused for pulse generator hardware other than an AWG.
        """

        self.interleave = state
        return self.get_interleave()

    def write(self, command):
        """ Sends a command string to the device.

        @param string command: string containing the command

        @return int: error code (0:OK, -1:error)
        """

        self.log.info('It is so nice that you talk to me and told me "{0}"; '
                      'as a dummy it is very dull out here! :) '.format(command))
        return 0

    def query(self, question):
        """ Asks the device a 'question' and receive and return an answer from it.

        @param string question: string containing the command

        @return string: the answer of the device to the 'question' in a string
        """

        self.log.info('Dude, I\'m a dummy! Your question \'{0}\' is way too '
                      'complicated for me :D !'.format(question))
        return 'I am a dummy!'
        
    def load_sequence(self, sequence_name):
        """ Loads a sequence to the channels of the device in order to be ready for playback.
        For devices that have a workspace (i.e. AWG) this will load the sequence from the device
        workspace into the channels.

        @param sequence_name:  str, name of the sequence to load

        @return (dict, str): Dictionary with keys being the channel number and values being the
                             respective asset loaded into the channel, string describing the asset
                             type ('waveform' or 'sequence')
        """
        if sequence_name not in self.sequence_dict:
            self.log.error('Sequence loading failed. No sequence with name "{0}" found on device '
                           'memory.'.format(sequence_name))
            return self.get_loaded_assets()

        # Determine if the device is purely digital and get all active channels
        analog_channels = sorted(chnl for chnl in self.activation_config if chnl.startswith('a'))
        digital_channels = sorted(chnl for chnl in self.activation_config if chnl.startswith('d'))
        pure_digital = len(analog_channels) == 0

        if pure_digital and len(digital_channels) != self.sequence_dict[sequence_name]:
            self.log.error('Sequence loading failed. Number of active digital channels ({0:d}) does'
                           ' not match the number of tracks in the sequence ({1:d}).'
                           ''.format(len(digital_channels), self.sequence_dict[sequence_name]))
            return self.get_loaded_assets()
        if not pure_digital and len(analog_channels) != self.sequence_dict[sequence_name]:
            self.log.error('Sequence loading failed. Number of active analog channels ({0:d}) does'
                           ' not match the number of tracks in the sequence ({1:d}).'
                           ''.format(len(analog_channels), self.sequence_dict[sequence_name]))
            return self.get_loaded_assets()

        new_loaded_assets = dict()
        if pure_digital:
            for track_index, chnl in enumerate(digital_channels):
                chnl_num = int(chnl.split('ch')[1])
                new_loaded_assets[chnl_num] = '{0}_{1:d}'.format(sequence_name, track_index)
        else:
            for track_index, chnl in enumerate(analog_channels):
                chnl_num = int(chnl.split('ch')[1])
                new_loaded_assets[chnl_num] = '{0}_{1:d}'.format(sequence_name, track_index)

        self.current_loaded_assets = new_loaded_assets
        return self.get_loaded_assets()
    def get_sequence_names(self):
        """ Retrieve the names of all uploaded sequence on the device.

        @return list: List of all uploaded sequence name strings in the device workspace.
        """
        return list(self.sequence_dict)
        
    def delete_sequence(self, sequence_name):
        """ Delete the sequence with name "sequence_name" from the device memory.

        @param str sequence_name: The name of the sequence to be deleted
                                  Optionally a list of sequence names can be passed.

        @return list: a list of deleted sequence names.
        """
        if isinstance(sequence_name, str):
            sequence_name = [sequence_name]

        deleted_sequences = list()
        for sequence in sequence_name:
            if sequence in self.sequence_dict:
                del self.sequence_dict[sequence]
                deleted_sequences.append(sequence)

        return deleted_sequences
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
# -*- coding: utf-8 -*-

"""
This file contains the Qudi hardware dummy for pulsing devices.

"""

import time
from collections import OrderedDict
import numpy as np
import h5py
import sys

# ip_hostname='192.168.68.132' # edit this line to use a specific Pulse Streamer IP address
from qudi.core.module import Base
from qudi.hardware.swabian_instruments.pulse_streamer_jrpc import PulseStreamer # import Pulse Streamer wrapper class

from qudi.hardware.swabian_instruments.pulse_streamer_jrpc import Start, Mode# import enum types  

from qudi.hardware.swabian_instruments.Sequence import Sequence

from qudi.hardware.tabor.tabor_func_russ import TaborAWG

from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption
from qudi.core.statusvariable import StatusVar
from qudi.interface.pulser_interface import PulserInterface, PulserConstraints


class PulseStreamerAWG(PulserInterface):
    """ e

    Be careful in adjusting the method names in that class, since some of them
    are also connected to the mwsourceinterface (to give the AWG the possibility
    to act like a microwave source).

    Example config for copy-paste:

    pulser_dummy:
        module.Class: 'pulser_dummy.PulserDummy'

    """
    _modclass = 'PulseStreamerAWG'
    _modtype = 'hardware'
    _pulsestreamer_ip = ConfigOption('pulsestreamer_ip', '192.168.68.132', missing='warn')
    _awg_ip = ConfigOption('taborawg_ip', '192.168.68.1XX', missing='warn')

    activation_config = StatusVar(default=None)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

        

        self.connected = False
        self.sample_rate = 1e9

        # Deactivate all channels at first:
        # self.channel_states = {'d_ch1': False, 'd_ch2': False, 'd_ch3': False, 'd_ch4': False,
                               # 'd_ch5': False, 'd_ch6': False, 'd_ch7': False, 'd_ch8': False, 'a_ch1': False, 'a_ch2': False}
        self.channel_states = {'d_ch1': False, 'd_ch2': False, 'd_ch3': False, 'd_ch4': False,
                               'd_ch5': False, 'd_ch6': False, 'd_ch7': False, 'd_ch8': False, 'a_ch1': False, 'a_ch2': False,'a_ch3': False, 'a_ch4': False}

        # for each analog channel one value
        # self.amplitude_dict = {'a_ch1': 1.0, 'a_ch2': 1.0}
        # self.offset_dict = {'a_ch1': 0.0, 'a_ch2': 0.0}
        self.amplitude_dict = {'a_ch1': 1.0, 'a_ch2': 1.0, 'a_ch3': 1.0, 'a_ch4': 1.0}
        self.offset_dict = {'a_ch1': 0.0, 'a_ch2': 0.0, 'a_ch3': 0.0, 'a_ch4': 0.0}

        # for each digital channel one value
        self.digital_high_dict = {'d_ch1': 3.3, 'd_ch2': 3.3, 'd_ch3': 3.3, 'd_ch4': 3.3,
                                  'd_ch5': 3.3, 'd_ch6': 3.3, 'd_ch7': 3.3, 'd_ch8': 3.3}
        self.digital_low_dict = {'d_ch1': 0.0, 'd_ch2': 0.0, 'd_ch3': 0.0, 'd_ch4': 0.0,
                                 'd_ch5': 0.0, 'd_ch6': 0.0, 'd_ch7': 0.0, 'd_ch8': 0.0}

        self.waveform_set = set()
        self.sequence_dict = dict()

        self.current_loaded_assets = dict()

        self.use_sequencer = False
        self.interleave = False


        self.pulser = PulseStreamer(self._pulsestreamer_ip)
        self.tawg = TaborAWG()#initialise and connect to AWG

        start = Start.HARDWARE_RISING

        mode = Mode.NORMAL

        self.pulser.setTrigger(start=start, mode=mode)


        self.current_status = 0    # that means off, not running.

    def on_activate(self):
        """ Initialisation performed during activation of the module.
        """
        self.connected = True


        self.pulser_off() #also turns awg off


        self.current_status = 0
        if self.activation_config is None:
            self.activation_config = self.get_constraints().activation_config['config0']

    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        self.connected = False

    def get_constraints(self):
        """
        Retrieve the hardware constrains from the Pulsing device.

        @return constraints object: object with pulser constraints as attributes.

        Provides all the constraints (e.g. sample_rate, amplitude, total_length_bins,
        channel_config, ...) related to the pulse generator hardware to the caller.

            SEE PulserConstraints CLASS IN pulser_interface.py FOR AVAILABLE CONSTRAINTS!!!

        If you are not sure about the meaning, look in other hardware files to get an impression.
        If still additional constraints are needed, then they have to be added to the
        PulserConstraints class.

        Each scalar parameter is an ScalarConstraints object defined in cor.util.interfaces.
        Essentially it contains min/max values as well as min step size, default value and unit of
        the parameter.

        PulserConstraints.activation_config differs, since it contain the channel
        configuration/activation information of the form:
            {<descriptor_str>: <channel_set>,
             <descriptor_str>: <channel_set>,
             ...}

        If the constraints cannot be set in the pulsing hardware (e.g. because it might have no
        sequence mode) just leave it out so that the default is used (only zeros).
        """
        constraints = PulserConstraints()

        if self.interleave:
            constraints.sample_rate.min = 12.0e9
            constraints.sample_rate.max = 24.0e9
            constraints.sample_rate.step = 4.0e8
            constraints.sample_rate.default = 24.0e9
        else:
            constraints.sample_rate.min = 1e9
            constraints.sample_rate.max = 1e9
            constraints.sample_rate.step = 0
            constraints.sample_rate.default = 1e9

        constraints.a_ch_amplitude.min = 0.02
        constraints.a_ch_amplitude.max = 2.0
        constraints.a_ch_amplitude.step = 0.001
        constraints.a_ch_amplitude.default = 2.0

        constraints.a_ch_offset.min = -1.0
        constraints.a_ch_offset.max = 1.0
        constraints.a_ch_offset.step = 0.001
        constraints.a_ch_offset.default = 0.0

        constraints.d_ch_low.min = 0.0
        constraints.d_ch_low.max = 0.0
        constraints.d_ch_low.step = 0.0
        constraints.d_ch_low.default = 0.0

        constraints.d_ch_high.min = 3.3
        constraints.d_ch_high.max = 3.3
        constraints.d_ch_high.step = 0.0
        constraints.d_ch_high.default = 3.3

        constraints.waveform_length.min = 1
        constraints.waveform_length.max = 134217728
        constraints.waveform_length.step = 1
        constraints.waveform_length.default = 1



        activation_config = OrderedDict()
        # activation_config['config0'] = {'d_ch1', 'd_ch2', 'd_ch3', 'd_ch4', 'd_ch5', 'd_ch6', 'd_ch7','d_ch8','a_ch1', 'a_ch2'}
        activation_config['config0'] = {'d_ch1', 'd_ch2', 'd_ch3', 'd_ch4', 'd_ch5', 'd_ch6', 'd_ch7','d_ch8','a_ch1', 'a_ch2','a_ch3', 'a_ch4'}
       
        constraints.activation_config = activation_config

        return constraints

    def pulser_on(self):
        """ Switches the pulsing device on.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 0:
            self.current_status = 1
            self.log.info('Pulser: Switch on the Output.')

            
            start = Start.SOFTWARE #SW trigger
            mode = Mode.SINGLE #1 trigger executes whole seq

            
            self.pulser.setTrigger(start=start, mode=mode)
            self.pulser.stream(self.sequence_to_run, 'INFINITE',(0,[],0,0))

            self.pulser.startNow()
            self.tawg.On() #here we do AWG on. The AWG trigger is emitted from the streamer to turn it on.
            
            return 0
        else:
            return -1
			
			
			
    def pulser_on_hwt(self):
        """ Hardware triggered operation

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 0:
            self.current_status = 1
            self.log.info('Pulser: Switch on the Output. Hardware trigger engaged.')

            
            start = Start.HARDWARE_RISING_AND_FALLING
            # mode = Mode.SINGLE
            mode = Mode.NORMAL
            
            self.pulser.setTrigger(start=start, mode=mode)
            self.pulser.stream(self.sequence_to_run, 1,(0,[],0,0))
            self.pulser.startNow()#starts awg in the same way
            
            return 0
        else:
            return -1
            
            
            
            
    def laser_on(self):
        """ Switches the pulsing device on.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 0:
            self.current_status = 1
            self.log.info('Pulser: Switch on the laser, mw.')

            self.pulser.constant((0,[0,1],0.0,0)) 
            self.pulser.startNow()
            return 0
        else:
            return -1
            
    def laser_off(self):
        """ Switches the pulsing device on.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 1:
            self.current_status = 0
            self.log.info('Pulser: Switch off the laser, mw')
            self.pulser.reset()
            self.pulser.constant((0,[],0,0)) 
            self.log.info('Pulser: Channel 1 and 2 ON.')
            return 0
        else:
            return -1

    def pulser_off(self):
        """ Switches the pulsing device off.

        @return int: error code (0:stopped, -1:error, 1:running)
        """
        if self.current_status == 1:
            self.current_status = 0
            self.pulser.reset()
            self.tawg.Off()

            #set constant state of the device
            self.pulser.constant((0,[],0,0)) 

            self.log.info('Pulser: Channel 1 and 2 OFF.')
        return 0



    def write_waveform(self, name, analog_samples, digital_samples, is_first_chunk, is_last_chunk,
                       total_number_of_samples, fold_sequence = False, fold_channel = 'd_ch5'):
        """
        Write a new waveform or append samples to an already existing waveform on the device memory.
        The flags is_first_chunk and is_last_chunk can be used as indicator if a new waveform should
        be created or if the write process to a waveform should be terminated.

        NOTE: All sample arrays in analog_samples and digital_samples must be of equal length!

        @param str name: the name of the waveform to be created/append to
        @param dict analog_samples: keys are the generic analog channel names (i.e. 'a_ch1') and
                                    values are 1D numpy arrays of type float32 containing the
                                    voltage samples.
        @param dict digital_samples: keys are the generic digital channel names (i.e. 'd_ch1') and
                                     values are 1D numpy arrays of type bool containing the marker
                                     states.
        @param bool is_first_chunk: Flag indicating if it is the first chunk to write.
                                    If True this method will create a new empty wavveform.
                                    If False the samples are appended to the existing waveform.
        @param bool is_last_chunk:  Flag indicating if it is the last chunk to write.
                                    Some devices may need to know when to close the appending wfm.
        @param int total_number_of_samples: The number of sample points for the entire waveform
                                            (not only the currently written chunk)

        @return (int, list): Number of samples written (-1 indicates failed process) and list of
                             created waveform names
        """
        waveforms = list()
        print(digital_samples.items())
        if len(analog_samples) > 0:
            number_of_samples = len(analog_samples[list(analog_samples)[0]])
        elif len(digital_samples) > 0:
            number_of_samples = len(digital_samples[list(digital_samples)[0]])
        else:
            self.log.error('No analog or digital samples passed to write_waveform method in dummy '
                           'pulser.')
            return -1, waveforms

        for chnl, samples in analog_samples.items():
            if len(samples) != number_of_samples:
                self.log.error('Unequal length of sample arrays for different channels in dummy '
                               'pulser.')
                return -1, waveforms
        for chnl, samples in digital_samples.items():
            if len(samples) != number_of_samples:
                self.log.error('Unequal length of sample arrays for different channels in dummy '
                               'pulser.')
                return -1, waveforms

        # Determine if only digital samples are active. In that case each channel will get a
        # waveform. Otherwise only the analog channels will have a waveform with digital channel
        # samples included (as it is the case in Tektronix and Keysight AWGs).
        # Simulate a 1Gbit/s transfer speed. Assume each analog waveform sample is 5 bytes large
        # (4 byte float and 1 byte marker bitmask). Assume each digital waveform sample is 1 byte.
        if len(analog_samples) > 0:
            for chnl in analog_samples:
                waveforms.append(name + chnl[1:])
                
        else:
            for chnl in digital_samples:
                waveforms.append(name + chnl[1:])
                

        self.waveform_set.update(waveforms)
        

        chan = list(digital_samples) #PB stuff
        chan.sort() #PB stuff
        chunk_length = len(digital_samples[chan[0]]) #PB stuff
        self._current_activation_config = chan #PB stuff
        
        
        
        # t_gen = time.time()
        # print('____________________________________')
        # print('starting gen_streamer_sequence')
        # self._current_ps_waveform = self._gen_streamer_seq(digital_samples, analog_samples)
        # print('generating streamer sequence duration: '+str(time.time() - t_gen)+' seconds')
        # print("Sequence sampled. Programming instruments.")
        
        if is_first_chunk:
            self.__current_ps_waveform_name = name
            self.__samples_written = 0
            # initialise to a dict of list that describe pulse pattern in swabian language
            self.__current_ps_waveform = {key:[] for key in digital_samples.keys()}
            
        for channel_number, samples in digital_samples.items():
            new_channel_indices = np.where(samples[:-1] != samples[1:])[0]
            new_channel_indices = np.unique(new_channel_indices)

            # add in indices for the start and end of the sequence to simplify iteration
            new_channel_indices = np.insert(new_channel_indices, 0, [-1])
            new_channel_indices = np.insert(new_channel_indices, new_channel_indices.size, [samples.shape[0] - 1])
            pulses = []
            for new_channel_index in range(1, new_channel_indices.size):
                pulse = [new_channel_indices[new_channel_index] - new_channel_indices[new_channel_index - 1],
                         samples[new_channel_indices[new_channel_index - 1] + 1].astype(np.byte)]
                pulses.append(pulse)

            # extend (as opposed to rewrite) for chunky business
            # print(pulses)
            self.__current_ps_waveform[channel_number].extend(pulses)
        
        
        #self._current_ps_waveform_name = name
        seq = Sequence()# this is purely a Pulsestreamer thing and can be ignored for the AWG
        # count_analog_runs = 0
        
        for key, seq_ps in self.__current_ps_waveform.items():
            print(key)
            seq.setDigitalChannel(key, seq_ps)


        numsamps = self.tawg.analog_samples_tabor(analog_samples)
        if numsamps >= 4e9:
            self.log.error('N = '+str(numsamps)+' Analog samples exceeds AWG memory. Adjust sample freq. to ensure N <512e3')

        self.sequence_to_run = seq.getSequence()
        self.log.info('Waveforms with nametag "{0}" written on pulsestreamer.'.format(name))
        return number_of_samples, waveforms,
        


    def get_waveform_names(self):
        """ Retrieve the names of all uploaded waveforms on the device.

        @return list: List of all uploaded waveform name strings in the device workspace.
        """
        return list(self.waveform_set)



    def delete_waveform(self, waveform_name):
        """ Delete the waveform with name "waveform_name" from the device memory.

        @param str waveform_name: The name of the waveform to be deleted
                                  Optionally a list of waveform names can be passed.

        @return list: a list of deleted waveform names.
        """
        if isinstance(waveform_name, str):
            waveform_name = [waveform_name]

        deleted_waveforms = list()
        for waveform in waveform_name:
            if waveform in self.waveform_set:
                self.waveform_set.remove(waveform)
                deleted_waveforms.append(waveform)

        return deleted_waveforms



    def load_waveform(self, load_dict):
        """ Loads a waveform to the specified channel of the pulsing device.
        For devices that have a workspace (i.e. AWG) this will load the waveform from the device
        workspace into the channel.
        For a device without mass memory this will make the waveform/pattern that has been
        previously written with self.write_waveform ready to play.

        @param load_dict:  dict|list, a dictionary with keys being one of the available channel
                                      index and values being the name of the already written
                                      waveform to load into the channel.
                                      Examples:   {1: rabi_ch1, 2: rabi_ch2} or
                                                  {1: rabi_ch2, 2: rabi_ch1}
                                      If just a list of waveform names if given, the channel
                                      association will be invoked from the channel
                                      suffix '_ch1', '_ch2' etc.

        @return (dict, str): Dictionary with keys being the channel number and values being the
                             respective asset loaded into the channel, string describing the asset
                             type ('waveform' or 'sequence')
        """
        if isinstance(load_dict, list):
            new_dict = dict()
            for waveform in load_dict:
                channel = int(waveform.rsplit('_ch', 1)[1])
                new_dict[channel] = waveform
            load_dict = new_dict
        print('start loading waveform')
        # Determine if the device is purely digital and get all active channels
        analog_channels = [chnl for chnl in self.activation_config if chnl.startswith('a')]
        digital_channels = [chnl for chnl in self.activation_config if chnl.startswith('d')]
        pure_digital = len(analog_channels) == 0

        # Check if waveforms are present in virtual dummy device memory and specified channels are
        # active. Create new load dict.
        new_loaded_assets = dict()
        for channel, waveform in load_dict.items():
            if waveform not in self.waveform_set:
                self.log.error('Loading failed. Waveform "{0}" not found on device memory.'
                               ''.format(waveform))
                return self.current_loaded_assets
            if pure_digital:
                if 'd_ch{0:d}'.format(channel) not in digital_channels:
                    self.log.error('Loading failed. Digital channel {0:d} not active.'
                                   ''.format(channel))
                    return self.current_loaded_assets
            else:
                if 'a_ch{0:d}'.format(channel) not in analog_channels:
                    self.log.error('Loading failed. Analog channel {0:d} not active.'
                                   ''.format(channel))
                    return self.current_loaded_assets
            new_loaded_assets[channel] = waveform
        self.current_loaded_assets = new_loaded_assets
        # str_channels = [int
        
        
        
        
        
        
        print('end loading waveform')
        return self.get_loaded_assets()



    def get_loaded_assets(self):
        """
        Retrieve the currently loaded asset names for each active channel of the device.
        The returned dictionary will have the channel numbers as keys.
        In case of loaded waveforms the dictionary values will be the waveform names.
        In case of a loaded sequence the values will be the sequence name appended by a suffix
        representing the track loaded to the respective channel (i.e. '<sequence_name>_1').

        @return (dict, str): Dictionary with keys being the channel number and values being the
                             respective asset loaded into the channel,
                             string describing the asset type ('waveform' or 'sequence')
        """
        # Determine if it's a waveform or a sequence
        asset_type = None
        for asset_name in self.current_loaded_assets.values():
            if 'ch' in asset_name.rsplit('_', 1)[1]:
                current_type = 'waveform'
            else:
                current_type = 'sequence'

            if asset_type is None or asset_type == current_type:
                asset_type = current_type
            else:
                self.log.error('Unable to determine loaded asset type. Mixed naming convention '
                               'assets loaded (waveform and sequence tracks).')
                return dict(), ''

        return self.current_loaded_assets, asset_type

    def clear_all(self):
        """ Clears all loaded waveform from the pulse generators RAM.

        @return int: error code (0:OK, -1:error)

        Unused for digital pulse generators without storage capability
        (PulseBlaster, FPGA).
        """
        self.current_loaded_assets = dict()
        self.waveform_set = set()
        self.sequence_dict = dict()
        return 0

    def get_status(self):
        """ Retrieves the status of the pulsing hardware

        @return (int, dict): inter value of the current status with the
                             corresponding dictionary containing status
                             description for all the possible status variables
                             of the pulse generator hardware
        """
        status_dic = {-1: 'Failed Request or Communication', 0: 'Device has stopped, but can receive commands.',
                      1: 'Device is active and running.'}
        # All the other status messages should have higher integer values
        # then 1.
        return self.current_status, status_dic

    def get_sample_rate(self):
        """ Get the sample rate of the pulse generator hardware

        @return float: The current sample rate of the device (in Hz)

        Do not return a saved sample rate in a class variable, but instead
        retrieve the current sample rate directly from the device.
        """

        return self.sample_rate
        
    def get_awg_sample_rate(self):
        """ Get the sample rate of the pulse generator hardware

        @return float: The current sample rate of the device (in Hz)

        Do not return a saved sample rate in a class variable, but instead
        retrieve the current sample rate directly from the device.
        """
        self.awg_sample_rate = self.tawg.get_awg_sample_rate()
        return self.awg_sample_rate

    def set_sample_rate(self, sample_rate):
        """ Set the sample rate of the pulse generator hardware

        @param float sample_rate: The sampling rate to be set (in Hz)

        @return float: the sample rate returned from the device.

        Note: After setting the sampling rate of the device, retrieve it again
              for obtaining the actual set value and use that information for
              further processing.
        """
        constraint = self.get_constraints().sample_rate
        if sample_rate > constraint.max:
            self.sample_rate = constraint.max
        elif sample_rate < constraint.min:
            self.sample_rate = constraint.min
        else:
            self.sample_rate = sample_rate
        return self.sample_rate

    def set_awg_sample_rate(self, sample_rate):
        """ Set the sample rate of the pulse generator hardware

        @param float sample_rate: The sampling rate to be set (in Hz)

        @return float: the sample rate returned from the device.

        Note: After setting the sampling rate of the device, retrieve it again
              for obtaining the actual set value and use that information for
              further processing.
        """
        self.tawg.set_awg_sample_rate(sample_rate)
        self.awg_sample_rate = self.get_awg_sample_rate()
        return self.awg_sample_rate

    def get_analog_level(self, amplitude=None, offset=None):
        """ Retrieve the analog amplitude and offset of the provided channels.

        @param list amplitude: optional, if the amplitude value (in Volt peak to
                               peak, i.e. the full amplitude) of a specific
                               channel is desired.
        @param list offset: optional, if the offset value (in Volt) of a
                            specific channel is desired.

        @return: (dict, dict): tuple of two dicts, with keys being the channel
                               descriptor string (i.e. 'a_ch1') and items being
                               the values for those channels. Amplitude is
                               always denoted in Volt-peak-to-peak and Offset
                               in volts.

        Note: Do not return a saved amplitude and/or offset value but instead
              retrieve the current amplitude and/or offset directly from the
              device.

        If nothing (or None) is passed then the levels of all channels will be
        returned. If no analog channels are present in the device, return just
        empty dicts.

        Example of a possible input:

            amplitude = ['a_ch1', 'a_ch4'], offset = None

        to obtain the amplitude of channel 1 and 4 and the offset of all
        channels

            {'a_ch1': -0.5, 'a_ch4': 2.0}
            {'a_ch1': 0.0, 'a_ch2': 0.0, 'a_ch3': 1.0, 'a_ch4': 0.0}

        """
        # d1 = {'a_ch1': 1, 'a_ch2': 1}
        d1 = {'a_ch1': 1, 'a_ch2': 1, 'a_ch3': 1, 'a_ch4': 1}
        return d1, dict()

    def set_analog_level(self, amplitude=None, offset=None):
        """ Set amplitude and/or offset value of the provided analog channel(s).

        @param dict amplitude: dictionary, with key being the channel descriptor
                               string (i.e. 'a_ch1', 'a_ch2') and items being
                               the amplitude values (in Volt peak to peak, i.e.
                               the full amplitude) for the desired channel.
        @param dict offset: dictionary, with key being the channel descriptor
                            string (i.e. 'a_ch1', 'a_ch2') and items being the
                            offset values (in absolute volt) for the desired
                            channel.

        @return (dict, dict): tuple of two dicts with the actual set values for
                              amplitude and offset for ALL channels.

        If nothing is passed then the command will return the current
        amplitudes/offsets.

        Note: After setting the amplitude and/or offset values of the device,
              use the actual set return values for further processing.
        """
        return {}, {}

    def get_digital_level(self, low=None, high=None):
        """ Retrieve the digital low and high level of the provided channels.

        @param list low: optional, if a specific low value (in Volt) of a
                         channel is desired.
        @param list high: optional, if a specific high value (in Volt) of a
                          channel is desired.

        @return: (dict, dict): tuple of two dicts, with keys being the channel
                               number and items being the values for those
                               channels. Both low and high value of a channel is
                               denoted in (absolute) Voltage.

        Note: Do not return a saved low and/or high value but instead retrieve
              the current low and/or high value directly from the device.

        If no entries provided then the levels of all channels where simply
        returned. If no digital channels provided, return just an empty dict.

        Example of a possible input:
            low = ['d_ch1', 'd_ch4']
        to obtain the low voltage values of digital channel 1 an 4. A possible
        answer might be
            {'d_ch1': -0.5, 'd_ch4': 2.0} {}
        since no high request was performed.

        The major difference to analog signals is that digital signals are
        either ON or OFF, whereas analog channels have a varying amplitude
        range. In contrast to analog output levels, digital output levels are
        defined by a voltage, which corresponds to the ON status and a voltage
        which corresponds to the OFF status (both denoted in (absolute) voltage)

        In general there is no bijective correspondence between
        (amplitude, offset) and (value high, value low)!
        """
        if low is None:
            low = []
        if high is None:
            high = []

        if not low and not high:
            low_val = self.digital_low_dict
            high_val = self.digital_high_dict
        else:
            low_val = dict()
            high_val = dict()
            for d_ch in low:
                low_val[d_ch] = self.digital_low_dict[d_ch]
            for d_ch in high:
                high_val[d_ch] = self.digital_high_dict[d_ch]

        return low_val, high_val

    def set_digital_level(self, low=None, high=None):
        """ Set low and/or high value of the provided digital channel.

        @param dict low: dictionary, with key being the channel and items being
                         the low values (in volt) for the desired channel.
        @param dict high: dictionary, with key being the channel and items being
                         the high values (in volt) for the desired channel.

        @return (dict, dict): tuple of two dicts where first dict denotes the
                              current low value and the second dict the high
                              value.

        If nothing is passed then the command will return two empty dicts.

        Note: After setting the high and/or low values of the device, retrieve
              them again for obtaining the actual set value(s) and use that
              information for further processing.

        The major difference to analog signals is that digital signals are
        either ON or OFF, whereas analog channels have a varying amplitude
        range. In contrast to analog output levels, digital output levels are
        defined by a voltage, which corresponds to the ON status and a voltage
        which corresponds to the OFF status (both denoted in (absolute) voltage)

        In general there is no bijective correspondence between
        (amplitude, offset) and (value high, value low)!
        """
        if low is None:
            low = {}
        if high is None:
            high = {}
        self.log.warning('PulseStreamer logic level cannot be adjusted!')
        return 0

    def get_active_channels(self, ch=None):
        """ Get the active channels of the pulse generator hardware.

        @param list ch: optional, if specific analog or digital channels are
                        needed to be asked without obtaining all the channels.

        @return dict:  where keys denoting the channel number and items boolean
                       expressions whether channel are active or not.

        Example for an possible input (order is not important):
            ch = ['a_ch2', 'd_ch2', 'a_ch1', 'd_ch5', 'd_ch1']
        then the output might look like
            {'a_ch2': True, 'd_ch2': False, 'a_ch1': False, 'd_ch5': True, 'd_ch1': False}

        If no parameters are passed to this method all channels will be asked
        for their setting.
        """
        if ch is None:
            ch = []

        active_ch = {}

        if not ch:
            active_ch = self.channel_states

        else:
            for channel in ch:
                active_ch[channel] = self.channel_states[channel]

        return active_ch

    def set_active_channels(self, ch=None):
        """
        Set the active/inactive channels for the pulse generator hardware.
        The state of ALL available analog and digital channels will be returned
        (True: active, False: inactive).
        The actually set and returned channel activation must be part of the available
        activation_configs in the constraints.
        You can also activate/deactivate subsets of available channels but the resulting
        activation_config must still be valid according to the constraints.
        If the resulting set of active channels can not be found in the available
        activation_configs, the channel states must remain unchanged.

        @param dict ch: dictionary with keys being the analog or digital string generic names for
                        the channels (i.e. 'd_ch1', 'a_ch2') with items being a boolean value.
                        True: Activate channel, False: Deactivate channel

        @return dict: with the actual set values for ALL active analog and digital channels

        If nothing is passed then the command will simply return the unchanged current state.

        Note: After setting the active channels of the device, use the returned dict for further
              processing.

        Example for possible input:
            ch={'a_ch2': True, 'd_ch1': False, 'd_ch3': True, 'd_ch4': True}
        to activate analog channel 2 digital channel 3 and 4 and to deactivate
        digital channel 1. All other available channels will remain unchanged.
        """
        if ch is None:
            ch = {}
        old_activation = self.channel_states.copy()
        for channel in ch:
            self.channel_states[channel] = ch[channel]

        active_channel_set = {chnl for chnl, is_active in self.channel_states.items() if is_active}
        if active_channel_set not in self.get_constraints().activation_config.values():
            self.log.error('Channel activation to be set not found in constraints.\n'
                           'Channel activation unchanged.')
            self.channel_states = old_activation
        else:
            self.activation_config = active_channel_set

        return self.get_active_channels(ch=list(ch))



    def reset(self):
        """ Reset the device.

        @return int: error code (0:OK, -1:error)
        """
        self.__init__()
        self.connected = True
        self.pulser.reset()
        self.log.info('reset!')
        return 0

    def has_sequence_mode(self):
        """ Asks the pulse generator whether sequence mode exists.

        @return: bool, True for yes, False for no.
        """
        return False

    def _gen_streamer_seq(self, digital_samples, analog_samples):
        """ Converts sampled sequence to array of tuples for pulsestreamer

        returns dictionary, {'channel': seq}
        """
        channelsetd = [key for key in digital_samples.keys() if digital_samples[key].any()]
        channelseta = [key for key in analog_samples.keys() if analog_samples[key].any()]


        channelset = channelsetd + channelseta
        print('CHANNELS')
        seq_dict = {}
        LOW = 0
        HIGH = 1
        for channel in channelset:
            if channel.startswith('d'):
                print('I am doing '+str(channel))
                d = digital_samples[channel]

                zrs = np.zeros(100)#always buffer the start of every sequence with 100ns of off
                d = np.insert(d,0,zrs)#takes into account if channel on at t = 0
                d = np.append(d,zrs)#takes into account if channel ends on off
                aa = [x+1 for x, i in enumerate(np.diff(d)) if i != 0]

                dead_init = aa[0] #initial off time (always present due to zrs buffering)
                ontimes =np.diff(aa)[::2] #every second element starting at 0 of the diffed aa
                deadtimes = np.insert(np.diff(aa)[1::2],0,dead_init) #every second element starting at 1 of the diffed aa puls the initial dead time at the start.
                final_dead = len(d)-aa[-1]
                deadtimes = np.append(deadtimes,final_dead)

                # define sequences
                seq_mw     = []

                ontimes = np.append(ontimes,0) 
                for i in range(len(ontimes)):
                    seq_mw  += [(deadtimes[i], LOW), (ontimes[i], HIGH)]
            
                seq_mw += [(100,LOW)]
                seq_dict[channel] = seq_mw
            else:
                print("all analog programming done by Tabor AWG")  
                a = analog_samples[channel]#This is an array of 1 ns intervals. 
                #
                seq_dict[channel] = a

                # ontimes = np.append(ontimes,0)  
                # uniqueamps = np.append(uniqueamps,0)  
 
                # for i in range(len(ontimes)):
                    # seq_mw  += [(deadtimes[i], LOW), (ontimes[i], uniqueamps[i])]
            
                # seq_mw += [(100,LOW)]
                # seq_dict[channel] = seq_mw
                # print(seq_mw)
            # print(seq_dict.keys())
        return seq_dict
#UNUSED        
        
    def write_sequence(self, name, sequence_parameter_list):
        """
        Write a new sequence on the device memory.

        @param name: str, the name of the waveform to be created/append to
        @param sequence_parameter_list: list, contains the parameters for each sequence step and
                                        the according waveform names.

        @return: int, number of sequence steps written (-1 indicates failed process)
        """
        # Check if all waveforms are present on virtual device memory
        for waveform_tuple, param_dict in sequence_parameter_list:
            for waveform in waveform_tuple:
                if waveform not in self.waveform_set:
                    self.log.error('Failed to create sequence "{0}" due to waveform "{1}" not '
                                   'present in device memory.'.format(name, waveform))
                    return -1

        if name in self.sequence_dict:
            del self.sequence_dict[name]


        # Fill in sequence information
        for step, (wfm_tuple, seq_step) in enumerate(sequence_parameter_list, 1):
            self.log.debug('flag_trigger: {}'.format(seq_step.flag_trigger))
            self.log.debug('flag_high: {}'.format(seq_step.flag_high))

        self.sequence_dict[name] = len(sequence_parameter_list[0][0])
        time.sleep(1)
        

        self.log.info('Sequence with name "{0}" directly written on dummy pulser.'.format(name))
        return len(sequence_parameter_list)

    def get_interleave(self):
        """ Check whether Interleave is ON or OFF in AWG.

        @return bool: True: ON, False: OFF

        Unused for pulse generator hardware other than an AWG.
        """

        return self.interleave

    def set_interleave(self, state=False):
        """ Turns the interleave of an AWG on or off.

        @param bool state: The state the interleave should be set to
                           (True: ON, False: OFF)

        @return bool: actual interleave status (True: ON, False: OFF)

        Note: After setting the interleave of the device, retrieve the
              interleave again and use that information for further processing.

        Unused for pulse generator hardware other than an AWG.
        """

        self.interleave = state
        return self.get_interleave()

    def write(self, command):
        """ Sends a command string to the device.

        @param string command: string containing the command

        @return int: error code (0:OK, -1:error)
        """

        self.log.info('It is so nice that you talk to me and told me "{0}"; '
                      'as a dummy it is very dull out here! :) '.format(command))
        return 0

    def query(self, question):
        """ Asks the device a 'question' and receive and return an answer from it.

        @param string question: string containing the command

        @return string: the answer of the device to the 'question' in a string
        """

        self.log.info('Dude, I\'m a dummy! Your question \'{0}\' is way too '
                      'complicated for me :D !'.format(question))
        return 'I am a dummy!'
        
    def load_sequence(self, sequence_name):
        """ Loads a sequence to the channels of the device in order to be ready for playback.
        For devices that have a workspace (i.e. AWG) this will load the sequence from the device
        workspace into the channels.

        @param sequence_name:  str, name of the sequence to load

        @return (dict, str): Dictionary with keys being the channel number and values being the
                             respective asset loaded into the channel, string describing the asset
                             type ('waveform' or 'sequence')
        """
        if sequence_name not in self.sequence_dict:
            self.log.error('Sequence loading failed. No sequence with name "{0}" found on device '
                           'memory.'.format(sequence_name))
            return self.get_loaded_assets()

        # Determine if the device is purely digital and get all active channels
        analog_channels = sorted(chnl for chnl in self.activation_config if chnl.startswith('a'))
        digital_channels = sorted(chnl for chnl in self.activation_config if chnl.startswith('d'))
        pure_digital = len(analog_channels) == 0

        if pure_digital and len(digital_channels) != self.sequence_dict[sequence_name]:
            self.log.error('Sequence loading failed. Number of active digital channels ({0:d}) does'
                           ' not match the number of tracks in the sequence ({1:d}).'
                           ''.format(len(digital_channels), self.sequence_dict[sequence_name]))
            return self.get_loaded_assets()
        if not pure_digital and len(analog_channels) != self.sequence_dict[sequence_name]:
            self.log.error('Sequence loading failed. Number of active analog channels ({0:d}) does'
                           ' not match the number of tracks in the sequence ({1:d}).'
                           ''.format(len(analog_channels), self.sequence_dict[sequence_name]))
            return self.get_loaded_assets()

        new_loaded_assets = dict()
        if pure_digital:
            for track_index, chnl in enumerate(digital_channels):
                chnl_num = int(chnl.split('ch')[1])
                new_loaded_assets[chnl_num] = '{0}_{1:d}'.format(sequence_name, track_index)
        else:
            for track_index, chnl in enumerate(analog_channels):
                chnl_num = int(chnl.split('ch')[1])
                new_loaded_assets[chnl_num] = '{0}_{1:d}'.format(sequence_name, track_index)

        self.current_loaded_assets = new_loaded_assets
        return self.get_loaded_assets()
    def get_sequence_names(self):
        """ Retrieve the names of all uploaded sequence on the device.

        @return list: List of all uploaded sequence name strings in the device workspace.
        """
        return list(self.sequence_dict)
        
    def delete_sequence(self, sequence_name):
        """ Delete the sequence with name "sequence_name" from the device memory.

        @param str sequence_name: The name of the sequence to be deleted
                                  Optionally a list of sequence names can be passed.

        @return list: a list of deleted sequence names.
        """
        if isinstance(sequence_name, str):
            sequence_name = [sequence_name]

        deleted_sequences = list()
        for sequence in sequence_name:
            if sequence in self.sequence_dict:
                del self.sequence_dict[sequence]
                deleted_sequences.append(sequence)

        return deleted_sequences