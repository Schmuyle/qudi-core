# -*- coding: utf-8 -*-
"""
This file contains basic pulse analysis methods for Qudi.

"""

import numpy as np

from qudi.logic.pulsed.pulse_analyzer import PulseAnalyzerBase
def find_edge(y,bins=20):
    """Returns edge of a step function"""
    h,b=np.histogram(y,bins=bins)
    i0 = int(bins/2)
    i  = h[i0:].argmax()+i0
    threshold = 0.5*(b[0]+b[i])
    return int(np.where(y>threshold)[0][0])
    
def spin_state_sn(c, edge, time_int, t1, dt = 10,t0 = 0):

    I = int(round(time_int/float(dt)))
    i0 = edge + int(round(t0/float(dt)))
    y = np.empty((c.shape[0],))
    for i, slot in enumerate(c):
        y[i] = slot[i0:i0+I].sum()
    if t1 >= 0:
        i1 = edge + int(round(t1/float(dt)))    
        y1 = np.empty((c.shape[0],))
        for i, slot in enumerate(c):
            y1[i] = slot[i1:i1+I].sum()
        y = y/y1.mean()
    return y




class BasicPulseAnalyzer(PulseAnalyzerBase):
    """ax

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def analyse_mean_norm(self, laser_data, signal_start=0.0, signal_end=200e-9, norm_start=300e-9,
                          norm_end=500e-9):
        """

        @param laser_data:
        @param signal_start:
        @param signal_end:
        @param norm_start:
        @param norm_end:
        This function is inferior to the one from pi3d. The pi3d function does not insist you know the start of the signal. It calculates that using the find edge function.
        @return:
        @return:
        """
        # Get number of lasers
        num_of_lasers = laser_data.shape[0]
        # num_of_lasers = laser_data.shape[0]
        # np.savetxt('outs.csv',laser_data)
        # print(laser_data)
        # Get counter bin width
        bin_width = self.fast_counter_settings.get('bin_width')
        profile = laser_data.sum(0)	 
        edge = find_edge(profile)
        


        if not isinstance(bin_width, float):
            return np.zeros(num_of_lasers), np.zeros(num_of_lasers)

        # Convert the times in seconds to bins (i.e. array indices)
        # signal_start_bin = round(signal_start / bin_width)
        signal_start_bin = edge
        signal_end_bin = round(edge+(signal_end-signal_start) / bin_width)
        norm_start_bin = round(edge+norm_start / bin_width)
        norm_end_bin = round(edge + norm_end / bin_width)


        # initialize data arrays for signal and measurement error
        signal_data = np.empty(num_of_lasers, dtype=float)
        ref_data = np.empty(num_of_lasers, dtype=float)

        error_data = np.empty(num_of_lasers, dtype=float)

        # loop over all laser pulses and analyze them
        for ii, laser_arr in enumerate(laser_data):
            
            # calculate the sum and mean of the data in the normalization window
            tmp_data = laser_arr[norm_start_bin:norm_end_bin]

            reference_sum = np.sum(tmp_data)
            reference_mean = (reference_sum / len(tmp_data)) if len(tmp_data) != 0 else 0.0
            ref_data[ii] = reference_sum

        for ii, laser_arr in enumerate(laser_data):

            # calculate the sum and mean of the data in the signal window
            tmp_data = laser_arr[signal_start_bin:signal_end_bin]

            signal_sum = np.sum(tmp_data)
            signal_mean = (signal_sum / len(tmp_data)) if len(tmp_data) != 0 else 0.0

            # Calculate normalized signal while avoiding division by zero
            if reference_mean > 0 and signal_mean >= 0:
                # signal_data[ii] = signal_mean / reference_mean
                signal_data[ii] = signal_sum / ref_data.mean()
            else:
                signal_data[ii] = 0.0

            # Calculate measurement error while avoiding division by zero
            if reference_sum > 0 and signal_sum > 0:
                # calculate with respect to gaussian error 'evolution'
                error_data[ii] = signal_data[ii] * np.sqrt(1 / signal_sum + 1 / ref_data.mean())
            else:
                error_data[ii] = 0.0

        return signal_data, error_data

    def analyse_sum(self, laser_data, signal_start=0.0, signal_end=200e-9):
        """
        @param laser_data:
        @param signal_start:
        @param signal_end:
        @return:
        """
        # Get number of lasers
        num_of_lasers = laser_data.shape[0]
        # Get counter bin width
        bin_width = self.fast_counter_settings.get('bin_width')

        if not isinstance(bin_width, float):
            return np.zeros(num_of_lasers), np.zeros(num_of_lasers)

        # Convert the times in seconds to bins (i.e. array indices)
        signal_start_bin = round(signal_start / bin_width)
        signal_end_bin = round(signal_end / bin_width)

        # initialize data arrays for signal and measurement error
        signal_data = np.empty(num_of_lasers, dtype=float)
        error_data = np.empty(num_of_lasers, dtype=float)

        # loop over all laser pulses and analyze them
        for ii, laser_arr in enumerate(laser_data):
            # calculate the sum of the data in the signal window
            signal = laser_arr[signal_start_bin:signal_end_bin].sum()
            signal_error = np.sqrt(signal)

            # Avoid numpy C type variables overflow and NaN values
            if signal < 0 or signal != signal:
                signal_data[ii] = 0.0
                error_data[ii] = 0.0
            else:
                signal_data[ii] = signal
                error_data[ii] = signal_error

        return signal_data, error_data

    def analyse_mean(self, laser_data, signal_start=0.0, signal_end=200e-9):
        """

        @param laser_data:
        @param signal_start:
        @param signal_end:
        @return:
        """
        # Get number of lasers
        num_of_lasers = laser_data.shape[0]
        # Get counter bin width
        bin_width = self.fast_counter_settings.get('bin_width')

        if not isinstance(bin_width, float):
            return np.zeros(num_of_lasers), np.zeros(num_of_lasers)

        # Convert the times in seconds to bins (i.e. array indices)
        signal_start_bin = round(signal_start / bin_width)
        signal_end_bin = round(signal_end / bin_width)

        # initialize data arrays for signal and measurement error
        signal_data = np.empty(num_of_lasers, dtype=float)
        error_data = np.empty(num_of_lasers, dtype=float)

        # loop over all laser pulses and analyze them
        for ii, laser_arr in enumerate(laser_data):
            # calculate the mean of the data in the signal window
            signal = laser_arr[signal_start_bin:signal_end_bin].mean()
            signal_sum = laser_arr[signal_start_bin:signal_end_bin].sum()
            signal_error = np.sqrt(signal_sum) / (signal_end_bin - signal_start_bin)

            # Avoid numpy C type variables overflow and NaN values
            if signal < 0 or signal != signal:
                signal_data[ii] = 0.0
                error_data[ii] = 0.0
            else:
                signal_data[ii] = signal
                error_data[ii] = signal_error

        return signal_data, error_data
