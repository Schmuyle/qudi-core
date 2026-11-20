import ctypes
import platform
import numpy as np
from collections import OrderedDict

class PulseFucker():

    def __init__(self):
        print('Get ready for fuckery')

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
        activation_config = OrderedDict()
        activation_config['all'] = ['d_ch1', 'd_ch2', 'd_ch3', 'd_ch4', 'd_ch5', 'd_ch6', 'd_ch7', 'd_ch8']
        active_channel_set = activation_config.values()
        self._current_activation_config = active_channel_set
        load_dict = {1: 'rabi_Ch1', 2: 'rabi_Ch2'}
        waveforms = list(set(load_dict.values()))
        waveform = waveforms[0]
        self._currently_loaded_waveform = waveform
        self._current_pb_waveform_name = 'gofuckyourself'
        
        asset_type = 'waveform' if self._currently_loaded_waveform else None

        asset_dict = {}
        for index, entry in enumerate(self._current_activation_config):
            # asset_dict[index+1] = '{0}_'.format(self._current_pb_waveform_name, entry.replace('d_',''))
            asset_dict[index+1] = self._current_pb_waveform_name
        return asset_dict, asset_type