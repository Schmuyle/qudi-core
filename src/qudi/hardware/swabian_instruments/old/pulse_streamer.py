# -*- coding: utf-8 -*-
"""
Use Swabian Instruments PulseStreamer8/2 as a pulse generator.

Protobuf (pb2) and grpc files generated from pulse_streamer.proto
file available at https://www.swabianinstruments.com/static/documentation/PulseStreamer/sections/interface.html#grpc-interface.

Regenerate files for an update proto file using the following:
python3 -m grpc_tools.protoc -I=./ --python_out=. --grpc_python_out=. ./pulse_streamer.proto

"""

from qudi.core.module import Base, StatusVar, ConfigOption
from qudi.util.paths import get_home_dir
from qudi.interface.pulser_interface import PulserInterface, PulserConstraints
from collections import OrderedDict

import grpc
import os
import hardware.swabian_instruments.pulse_streamer_pb2 as pulse_streamer_pb2
import dill

class PulseStreamer(PulserInterface):
    """ Methods to control PulseStreamer.

    Example config for copy-paste:

    pulse_streamer:
        module.Class: 'swabian_instruments.pulse_streamer.PulseStreamer'
        pulsestreamer_ip: '192.168.1.100'
        laser_channel: 0
        uw_x_channel: 2

    """
    _modclass = 'PulserInterface'
    _modtype = 'hardware'

    _pulsestreamer_ip = ConfigOption('pulsestreamer_ip', '192.168.68.132', missing='warn')
    _laser_channel = ConfigOption('laser_channel', 0, missing='warn')
    _uw_x_channel = ConfigOption('uw_x_channel', 2, missing='warn')

    activation_config = StatusVar(default=None)

    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)

        if 'pulsed_file_dir' in config.keys():
            self.pulsed_file_dir = config['pulsed_file_dir']

            if not os.path.exists(self.pulsed_file_dir):
                homedir = get_home_dir()
                self.pulsed_file_dir = os.path.join(homedir, 'pulsed_files')
                self.log.warning('The directory defined in parameter '
                            '"pulsed_file_dir" in the config for '
                            'PulseStreamer does not exist!\n'
                            'The default home directory\n{0}\n will be taken '
                            'instead.'.format(self.pulsed_file_dir))
        else:
            homedir = get_home_dir()
            self.pulsed_file_dir = os.path.join(homedir, 'pulsed_files')
            self.log.warning('No parameter "pulsed_file_dir" was specified in the config for '
                             'PulseStreamer as directory for the pulsed files!\nThe default home '
                             'directory\n{0}\nwill be taken instead.'.format(self.pulsed_file_dir))

        self.host_waveform_directory = self._get_dir_for_name('sampled_hardware_files')

        self.current_status = -1
        print('init for the PS cunt')
        self.sample_rate = 1e9
        self._current_loaded_assets = dict()

        self._channel = grpc.insecure_channel(self._pulsestreamer_ip + ':50051')

    def on_activate(self):
        """ Establish connection to pulse streamer and tell it to cancel all operations """
        self.pulse_streamer = pulse_streamer_pb2.PulseStreamerStub(self._channel)
        self.pulser_off()
        print('on activate')
        print(self.activation_config)
        self.current_status = 0
        if self.activation_config is None:
            self.activation_config = self.get_constraints().activation_config['all']

    def on_deactivate(self):
        del self.pulse_streamer

    def get_constraints(self):
        """ Retrieve the hardware constrains from the Pulsing device.

        @return dict: dict with constraints for the sequence generation and GUI

        Provides all the constraints (e.g. sample_rate, amplitude,
        total_length_bins, channel_config, ...) related to the pulse generator
        hardware to the caller.
        The keys of the returned dictionary are the str name for the constraints
        (which are set in this method). No other keys should be invented. If you
        are not sure about the meaning, look in other hardware files to get an
        impression. If still additional constraints are needed, then they have
        to be add to all files containing this interface.
        The items of the keys are again dictionaries which have the generic
        dictionary form:
            {'min': <value>,
             'max': <value>,
             'step': <value>,
             'unit': '<value>'}

        Only the keys 'activation_config' and differs, since it contain the
        channel configuration/activation information.

        If the constraints cannot be set in the pulsing hardware (because it
        might e.g. has no sequence mode) then write just zero to each generic
        dict. Note that there is a difference between float input (0.0) and
        integer input (0).
        ALL THE PRESENT KEYS OF THE CONSTRAINTS DICT MUST BE ASSIGNED!
        """
        constraints = PulserConstraints()

        # The file formats are hardware specific.
        constraints.waveform_format = ['pstream']
        constraints.sequence_format = []

        constraints.sample_rate.min = 1e9
        constraints.sample_rate.max = 1e9
        constraints.sample_rate.step = 0
        constraints.sample_rate.default = 1e9

        constraints.d_ch_low.min = 0.0
        constraints.d_ch_low.max = 0.0
        constraints.d_ch_low.step = 0.0
        constraints.d_ch_low.default = 0.0

        constraints.d_ch_high.min = 3.3
        constraints.d_ch_high.max = 3.3
        constraints.d_ch_high.step = 0.0
        constraints.d_ch_high.default = 3.3

        # sample file length max is not well-defined for PulseStreamer, which collates sequential identical pulses into
        # one. Total number of not-sequentially-identical pulses which can be stored: 1 M.
        constraints.waveform_length.min = 1
        constraints.waveform_length.max = 134217728
        constraints.waveform_length.step = 1
        constraints.waveform_length.default = 1

        # the name a_ch<num> and d_ch<num> are generic names, which describe UNAMBIGUOUSLY the
        # channels. Here all possible channel configurations are stated, where only the generic
        # names should be used. The names for the different configurations can be customary chosen.
        activation_config = OrderedDict()
        activation_config['all'] = {'d_ch1', 'd_ch2', 'd_ch3', 'd_ch4', 'd_ch5', 'd_ch6', 'd_ch7',
                                    'd_ch8'}
        constraints.activation_config = activation_config
        print('get constraints')

        return constraints

    def pulser_on(self):
        """ Switches the pulsing device on.

        @return int: error code (0:OK, -1:error)
        """
        # start the pulse sequence
        self.pulse_streamer.stream(self._sequence)
        self.log.info('Asset uploaded to PulseStreamer')
        self.pulse_streamer.startNow(pulse_streamer_pb2.VoidMessage())
        self.current_status = 1
        return 0

    def pulser_off(self):
        """ Switches the pulsing device off.

        @return int: error code (0:OK, -1:error)
        """
        # stop the pulse sequence
        print('pulser_off')
        channels = self._convert_to_bitmask([self._laser_channel, self._uw_x_channel])
        self.pulse_streamer.constant(pulse_streamer_pb2.PulseMessage(ticks=0, digi=channels, ao0=0, ao1=0))
        self.current_status = 0
        return 0

    def upload_asset(self, asset_name=None):
        """ Upload an already hardware conform file to the device.
            Does NOT load it into channels.

        @param name: string, name of the ensemble/seqeunce to be uploaded

        @return int: error code (0:OK, -1:error)
        """
        self.log.debug('PulseStreamer has no own storage capability.\n"upload_asset" call ignored.')
        return 0

    def load_waveform(self, load_dict):
        """ Loads a sequence or waveform to the specified channel of the pulsing
            device.

        @param str asset_name: The name of the asset to be loaded

        @param dict load_dict:  a dictionary with keys being one of the
                                available channel numbers and items being the
                                name of the already sampled
                                waveform/sequence files.
                                Examples:   {1: rabi_Ch1, 2: rabi_Ch2}
                                            {1: rabi_Ch2, 2: rabi_Ch1}
                                This parameter is optional. If none is given
                                then the channel association is invoked from
                                the sequence generation,
                                i.e. the filename appendix (_Ch1, _Ch2 etc.)

        @return int: error code (0:OK, -1:error)
        """
        if isinstance(load_dict, list):
            waveforms = list(set(load_dict))
        elif isinstance(load_dict, dict):
            waveforms = list(set(load_dict.values()))
        else:
            self.log.error('Method load_waveform expects a list of waveform names or a dict.')
            return self.get_loaded_assets()
        
        waveform = waveforms[0]
        
        if waveform != self._current_ps_waveform_name:

            return self.get_loaded_assets()

        #self.write_pulse_form(self._current_pb_waveform)
        self._currently_loaded_waveform = waveform
        print('load_waveform')

        return self.get_loaded_assets()[0]

    def load_asset(self, asset_name, load_dict=None):
        """ Loads a sequence or waveform to the specified channel of the pulsing
            device.

        @param str asset_name: The name of the asset to be loaded

        @param dict load_dict:  a dictionary with keys being one of the
                                available channel numbers and items being the
                                name of the already sampled
                                waveform/sequence files.
                                Examples:   {1: rabi_Ch1, 2: rabi_Ch2}
                                            {1: rabi_Ch2, 2: rabi_Ch1}
                                This parameter is optional. If none is given
                                then the channel association is invoked from
                                the sequence generation,
                                i.e. the filename appendix (_Ch1, _Ch2 etc.)

        @return int: error code (0:OK, -1:error)
        """
        # ignore if no asset_name is given
        if asset_name is None:
            self.log.warning('"load_asset" called with asset_name = None.')
            return 0

        # check if asset exists
        saved_assets = self.get_saved_asset_names()
        if asset_name not in saved_assets:
            self.log.error('No asset with name "{0}" found for PulseStreamer.\n'
                           '"load_asset" call ignored.'.format(asset_name))
            return -1

        # get samples from file
        filepath = os.path.join(self.host_waveform_directory, asset_name + '.pstream')
        pulse_sequence_raw = dill.load(open(filepath, 'rb'))

        pulse_sequence = []
        for pulse in pulse_sequence_raw:
            pulse_sequence.append(pulse_streamer_pb2.PulseMessage(ticks=pulse[0], digi=pulse[1], ao0=0, ao1=1))

        blank_pulse = pulse_streamer_pb2.PulseMessage(ticks=0, digi=0, ao0=0, ao1=0)
        laser_on = pulse_streamer_pb2.PulseMessage(ticks=0, digi=self._convert_to_bitmask([self._laser_channel]), ao0=0, ao1=0)
        laser_and_uw_channels = self._convert_to_bitmask([self._laser_channel, self._uw_x_channel])
        laser_and_uw_on = pulse_streamer_pb2.PulseMessage(ticks=0, digi=laser_and_uw_channels, ao0=0, ao1=0)
        self._sequence = pulse_streamer_pb2.SequenceMessage(pulse=pulse_sequence, n_runs=0, initial=laser_on,
            final=laser_and_uw_on, underflow=blank_pulse, start=1)

        self._current_loaded_assets = asset_name
        return self.get_loaded_assets()[0]

    def clear_all(self):
        """ Clears all loaded waveforms from the pulse generators RAM.

        @return int: error code (0:OK, -1:error)

        Unused for digital pulse generators without storage capability
        (PulseBlaster, FPGA).
        """
        return 0

    def get_status(self):
        """ Retrieves the status of the pulsing hardware

        @return (int, dict): tuple with an interger value of the current status
                             and a corresponding dictionary containing status
                             description for all the possible status variables
                             of the pulse generator hardware.
        """
        status_dic = dict()
        print('get status')
        status_dic[-1] = 'Failed Request or Failed Communication with device.'
        status_dic[0] = 'Device has stopped, but can receive commands.'
        status_dic[1] = 'Device is active and running.'

        return self.current_status, status_dic

    def get_sample_rate(self):
        """ Get the sample rate of the pulse generator hardware

        @return float: The current sample rate of the device (in Hz)

        Do not return a saved sample rate in a class variable, but instead
        retrieve the current sample rate directly from the device.
        """
        print('get sr')
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        """ Set the sample rate of the pulse generator hardware.

        @param float sample_rate: The sampling rate to be set (in Hz)

        @return float: the sample rate returned from the device.

        Note: After setting the sampling rate of the device, retrieve it again
              for obtaining the actual set value and use that information for
              further processing.
        """
        self.log.debug('PulseStreamer sample rate cannot be configured')
        return self.sample_rate

    def get_analog_level(self, amplitude=None, offset=None):
        """ Retrieve the analog amplitude and offset of the provided channels.

        @param list amplitude: optional, if a specific amplitude value (in Volt
                               peak to peak, i.e. the full amplitude) of a
                               channel is desired.
        @param list offset: optional, if a specific high value (in Volt) of a
                            channel is desired.

        @return: (dict, dict): tuple of two dicts, with keys being the channel
                               number and items being the values for those
                               channels. Amplitude is always denoted in
                               Volt-peak-to-peak and Offset in (absolute)
                               Voltage.
        """
        return {}, {}

    def set_analog_level(self, amplitude=None, offset=None):
        """ Set amplitude and/or offset value of the provided analog channel.

        @param dict amplitude: dictionary, with key being the channel and items
                               being the amplitude values (in Volt peak to peak,
                               i.e. the full amplitude) for the desired channel.
        @param dict offset: dictionary, with key being the channel and items
                            being the offset values (in absolute volt) for the
                            desired channel.

        @return (dict, dict): tuple of two dicts with the actual set values for
                              amplitude and offset.

        If nothing is passed then the command will return two empty dicts.
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
            low = [1,4]
        to obtain the low voltage values of digital channel 1 an 4. A possible
        answer might be
            {1: -0.5, 4: 2.0} {}
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
        low_dict = {}
        high_dict = {}
        if low is [] and high is []:
            for channel in range(8):
                low_dict[channel] = 0.0
                high_dict[channel] = 3.3
        else:
            for channel in low:
                low_dict[channel] = 0.0
            for channel in high:
                high_dict[channel] = 3.3
        return low_dict, high_dict

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

    def get_active_channels(self,  ch=None):
        if ch is None:
            ch = {}
        d_ch_dict = {}
        print('get active ch')
        if len(ch) < 1:
            for chnl in range(1, 9):
                d_ch_dict['d_ch{0}'.format(chnl)] = True
        else:
            for channel in ch:
                d_ch_dict[channel] = True
        return d_ch_dict

    def set_active_channels(self, ch=None):
        if ch is None:
            ch = {}
        d_ch_dict = {
            'd_ch1': True,
            'd_ch2': True,
            'd_ch3': True,
            'd_ch4': True,
            'd_ch5': True,
            'd_ch6': True,
            'd_ch7': True,
            'd_ch8': True}
        print('set act ch')
        return d_ch_dict

    def get_loaded_asset(self):
        """ Retrieve the currently loaded asset name of the device.

        @return str: Name of the current asset, that can be either a filename
                     a waveform, a sequence ect.
        """
        return self.current_loaded_assets

    def get_uploaded_asset_names(self):
        """ Retrieve the names of all uploaded assets on the device.

        @return list: List of all uploaded asset name strings in the current
                      device directory. This is no list of the file names.

        Unused for digital pulse generators without sequence storage capability
        (PulseBlaster, FPGA).
        """
        names = []
        return names

    def get_saved_asset_names(self):
        """ Retrieve the names of all sampled and saved assets on the host PC.
        This is no list of the file names.

        @return list: List of all saved asset name strings in the current
                      directory of the host PC.
        """
        file_list = self._get_filenames_on_host()

        saved_assets = []
        print('get_saved')
        for filename in file_list:
            if filename.endswith('.pstream'):
                asset_name = filename.rsplit('.', 1)[0]
                if asset_name not in saved_assets:
                    saved_assets.append(asset_name)
        return saved_assets

    def delete_asset(self, asset_name):
        """ Delete all files associated with an asset with the passed asset_name from the device memory.

        @param str asset_name: The name of the asset to be deleted
                               Optionally a list of asset names can be passed.

        @return int: error code (0:OK, -1:error)

        Unused for digital pulse generators without sequence storage capability
        (PulseBlaster, FPGA).
        """
        return 0

    def set_asset_dir_on_device(self, dir_path):
        """ Change the directory where the assets are stored on the device.

        @param str dir_path: The target directory

        @return int: error code (0:OK, -1:error)

        Unused for digital pulse generators without changeable file structure
        (PulseBlaster, FPGA).
        """
        return 0

    def get_asset_dir_on_device(self):
        """ Ask for the directory where the hardware conform files are stored on
            the device.

        @return str: The current file directory

        Unused for digital pulse generators without changeable file structure
        (PulseBlaster, FPGA).
        """
        return ''

    def get_interleave(self):
        """ Check whether Interleave is ON or OFF in AWG.

        @return bool: True: ON, False: OFF

        Unused for pulse generator hardware other than an AWG.
        """
        return False

    def set_interleave(self, state=False):
        """ Turns the interleave of an AWG on or off.

        @param bool state: The state the interleave should be set to
                           (True: ON, False: OFF)

        @return bool: actual interleave status (True: ON, False: OFF)

        Note: After setting the interleave of the device, retrieve the
              interleave again and use that information for further processing.

        Unused for pulse generator hardware other than an AWG.
        """
        return False

    def tell(self, command):
        """ Sends a command string to the device.

        @param string command: string containing the command

        @return int: error code (0:OK, -1:error)
        """
        return 0

    def ask(self, question):
        """ Asks the device a 'question' and receive and return an answer from it.
a
        @param string question: string containing the command

        @return string: the answer of the device to the 'question' in a string
        """
        return ''

    def reset(self):
        """ Reset the device.

        @return int: error code (0:OK, -1:error)
        """
        channels = self._convert_to_bitmask([self._laser_channel, self._uw_x_channel])
        self.pulse_streamer.constant(pulse_streamer_pb2.PulseMessage(ticks=0, digi=channels, ao0=0, ao1=0))
        self.pulse_streamer.constant(laser_on)
        print('reset')
        return 0

    def has_sequence_mode(self):
        """ Asks the pulse generator whether sequence mode exists.

        @return: bool, True for yes, False for no.
        """
        return False

    def _get_dir_for_name(self, name):
        """ Get the path to the pulsed sub-directory 'name'.

        @param name: string, name of the folder
        @return: string, absolute path to the directory with folder 'name'.
        """
        path = os.path.join(self.pulsed_file_dir, name)
        print('on activate')
        if not os.path.exists(path):
            os.makedirs(os.path.abspath(path))
        return os.path.abspath(path)

    def _get_filenames_on_host(self):
        """ Get the full filenames of all assets saved on the host PC.

        @return: list, The full filenames of all assets saved on the host PC.
        """
        
        print('get filenames')
        filename_list = [f for f in os.listdir(self.host_waveform_directory) if f.endswith('.pstream')]
        return filename_list

    def _convert_to_bitmask(self, active_channels):
        """ Convert a list of channels into a bitmask.
        @param numpy.array active_channels: the list of active channels like
                            e.g. [0,4,7]. Note that the channels start from 0.
        @return int: The channel-list is converted into a bitmask (an sequence
                     of 1 and 0). The returned integer corresponds to such a
                     bitmask.
        Note that you can get a binary representation of an integer in python
        if you use the command bin(<integer-value>). All higher unneeded digits
        will be dropped, i.e. 0b00100 is turned into 0b100. Examples are
            bin(0) =    0b0
            bin(1) =    0b1
            bin(8) = 0b1000
        Each bit value (read from right to left) corresponds to the fact that a
        channel is on or off. I.e. if you have
            0b001011
        then it would mean that only channel 0, 1 and 3 are switched to on, the
        others are off.
        Helper method for write_pulse_form.
        """
        bits = 0     # that corresponds to: 0b0
        print('bitmask')    # that corresponds to: 0b0
        for channel in active_channels:
            # go through each list element and create the digital word out of
            # 0 and 1 that represents the channel configuration. In order to do
            # that a bitwise shift to the left (<< operator) is performed and
            # the current channel configuration is compared with a bitwise OR
            # to check whether the bit was already set. E.g.:
            #   0b1001 | 0b0110: compare elementwise:
            #           1 | 0 => 1
            #           0 | 1 => 1
            #           0 | 1 => 1
            #           1 | 1 => 1
            #                   => 0b1111
            bits = bits | (1<< channel)
        return bits


    # def load_waveform(self, waveform_name):
        # """ Loads a sequence to the channels of the device in order to be ready for playback.
        # For devices that have a workspace (i.e. AWG) this will load the sequence from the device
        # workspace into the channels.
        # For a device without mass memory this will make the waveform/pattern that has been
        # previously written with self.write_waveform ready to play.

        # @param dict|list sequence_name: a dictionary with keys being one of the available channel
                                        # index and values being the name of the already written
                                        # waveform to load into the channel.
                                        # Examples:   {1: rabi_ch1, 2: rabi_ch2} or
                                                    # {1: rabi_ch2, 2: rabi_ch1}
                                        # If just a list of waveform names if given, the channel
                                        # association will be invoked from the channel
                                        # suffix '_ch1', '_ch2' etc.

        # @return dict: Dictionary containing the actually loaded waveforms per channel.
        # """
        # self.log.warning('PulseStreamer digital pulse generator has no sequencing capabilities.\n'
                         # 'load_sequence call ignored.')
        # return dict()

    def load_sequence(self, sequence_name):
        """ Loads a sequence to the channels of the device in order to be ready for playback.
        For devices that have a workspace (i.e. AWG) this will load the sequence from the device
        workspace into the channels.
        For a device without mass memory this will make the waveform/pattern that has been
        previously written with self.write_waveform ready to play.

        @param dict|list sequence_name: a dictionary with keys being one of the available channel
                                        index and values being the name of the already written
                                        waveform to load into the channel.
                                        Examples:   {1: rabi_ch1, 2: rabi_ch2} or
                                                    {1: rabi_ch2, 2: rabi_ch1}
                                        If just a list of waveform names if given, the channel
                                        association will be invoked from the channel
                                        suffix '_ch1', '_ch2' etc.

        @return dict: Dictionary containing the actually loaded waveforms per channel.
        """
        self.log.warning('PulseStreamer digital pulse generator has no sequencing capabilities.\n'
                         'load_sequence call ignored.')
        return dict()

    def delete_sequence(self, sequence_name):
        """ Delete the sequence with name "sequence_name" from the device memory.

        @param str sequence_name: The name of the sequence to be deleted
                                  Optionally a list of sequence names can be passed.

        @return list: a list of deleted sequence names.
        """
        return list()

    def delete_waveform(self, waveform_name):
        """ Delete the sequence with name "sequence_name" from the device memory.

        @param str sequence_name: The name of the sequence to be deleted
                                  Optionally a list of sequence names can be passed.

        @return list: a list of deleted sequence names.
        """
        return list()
        
    def get_sequence_names(self):
        """ Retrieve the names of all uploaded sequence on the device.

        @return list: List of all uploaded sequence name strings in the device workspace.
        """
        return list()
        
    def get_waveform_names(self):
        """ Retrieve the names of all uploaded sequence on the device.

        @return list: List of all uploaded sequence name strings in the device workspace.
        """
        print('gwv names')
        return list()
        
    def _gen_streamer_seq(self, digital_samples):
        """ Converts sampled sequence to array of tuples for pulsestreamer

        returns dictionary, {'channel': seq}
        """
        channelset = [key for key in digital_samples.keys() if digital_samples[key].any()]
        seq_dict = {}
        LOW = 0
        HIGH = 1
        for channel in channelset:
            d = digital_samples[channel]
            zrs = np.zeros(100)#always buffer the start of every sequence with 100ns of off
            d = np.insert(d,0,zrs)#takes into account if channel on at t = 0
            aa = [x+1 for x, i in enumerate(np.diff(d)) if i != 0]

            dead_init = aa[0] #initial off time (always present due to zrs buffering)
            ontimes =np.diff(aa)[::2] #every second element starting at 0 of the diffed aa
            deadtimes = np.insert(np.diff(aa)[1::2],0,dead_init) #every second element starting at 1 of the diffed aa puls the initial dead time at the start.
            final_dead = len(d)-aa[-1]
            deadtimes = np.append(deadtimes,final_dead)

            # define sequences
            seq_mw     = []

            ontimes = np.append(ontimes,0) 
            for i in range(len(ontimes)-1):
                seq_mw  += [(deadtimes[i], LOW), (ontimes[i], HIGH)]
        
            seq_mw += [(deadtimes[-1],LOW)]
            seq_dict[channel] = seq_mw
        return seq_dict


    def write_waveform(self, name, analog_samples, digital_samples,
                       is_first_chunk, is_last_chunk, total_number_of_samples):
        """
        Write a new sequence on the device memory.

        @param str name: the name of the waveform to be created, No appending.
        @param analog_samples: not implemented
        @param digital_samples: Qudi-format pulse dict of digital channel behaviour
        @param is_first_chunk: yes, I think. If not, then assumes it's appending.
        @param is_last_chunk: sure, why not.
        @param total_number_of_samples: I dont see why the streamer cares.


        """
        waveforms = list()
        for chnl in digital_samples:
            waveforms.append(name + chnl[1:])
        
        chan = list(digital_samples) #PB stuff
        chan.sort() #PB stuff
        chunk_length = len(digital_samples[chan[0]]) #PB stuff
        self._current_activation_config = chan #PB stuff
        
        self._current_ps_waveform = self._gen_streamer_seq(digital_samples)
        self._current_ps_waveform_name = name
        #HERE:proxy func for write_pulse_form, actually writes to hardware here.
        
        
        self.log.info('Waveforms with nametag "{0}" written on pulsestreamer.'.format(name))
        return number_of_samples, waveforms

    def write_sequence(self, name, sequence_parameters):
        """
        Write a new sequence on the device memory.

        @param str name: the name of the waveform to be created/append to
        @param dict sequence_parameters: dictionary containing the parameters for a sequence

        @return: int, number of sequence steps written (-1 indicates failed process)
        """
        self.log.warning('PulseStreamer digital pulse generator has no sequencing capabilities.\n'
                         'write_sequence call ignored.')
        return -1



    def get_loaded_assets(self):
        """ Retrieve the currently loaded asset names for each active channel
            of the device.

        @return (dict, str): Dictionary with keys being the channel number and
                             values being the respective asset loaded into the
                             channel, string describing the asset type
                             ('waveform' or 'sequence')

        The returned dictionary will have the channel numbers as keys. In case
        of loaded waveforms the dictionary values will be the waveform names. In
        case of a loaded sequence the values will be the sequence name appended
        by a suffix representing the track loaded to the respective channel
        (i.e. '<sequence_name>_1').
        """
        print('boogly boo3')
        asset_type = 'waveform' #if self._current_loaded_assets else 'I FUCKED UP'
        print(asset_type)
        asset_dict = {}
        for index, entry in enumerate(self._activation_config):
            # asset_dict[index+1] = '{0}_'.format(self._current_pb_waveform_name, entry.replace('d_',''))
            asset_dict[index+1] = self._current_loaded_assets
        return asset_dict, asset_type
        
    # def get_loaded_assets(self):
        # """
        # Retrieve the currently loaded asset names for each active channel of the device.
        # The returned dictionary will have the channel numbers as keys.
        # In case of loaded waveforms the dictionary values will be the waveform names.
        # In case of a loaded sequence the values will be the sequence name appended by a suffix
        # representing the track loaded to the respective channel (i.e. '<sequence_name>_1').

        # @return (dict, str): Dictionary with keys being the channel number and values being the
                             # respective asset loaded into the channel,
                             # string describing the asset type ('waveform' or 'sequence')
        # """
        # Determine if it's a waveform or a sequence
        # asset_type = None
        # for asset_name in self.current_loaded_assets.values():
            # if 'ch' in asset_name.rsplit('_', 1)[1]:
                # current_type = 'waveform'
            # else:
                # current_type = 'sequence'

            # if asset_type is None or asset_type == current_type:
                # asset_type = current_type
            # else:
                # self.log.error('Unable to determine loaded asset type. Mixed naming convention '
                               # 'assets loaded (waveform and sequence tracks).')
                # return dict(), ''

        # return self.current_loaded_assets, asset_type
        
        
        
        
