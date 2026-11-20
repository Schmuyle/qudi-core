# -*- coding: utf-8 -*-

"""
This file contains the Qudi Predefined Methods for sequence generator

"""

import numpy as np
from qudi.logic.pulsed.pulse_objects import PulseBlock, PulseBlockEnsemble, PulseSequence
from qudi.logic.pulsed.pulse_objects import PredefinedGeneratorBase
from enum import Enum

"""
General Pulse Creation Procedure:
=================================
- Create at first each PulseBlockElement object
- add all PulseBlockElement object to a list and combine them to a
  PulseBlock object.
- Create all needed PulseBlock object with that idea, that means
  PulseBlockElement objects which are grouped to PulseBlock objects.
- Create from the PulseBlock objects a PulseBlockEnsemble object.
- If needed and if possible, combine the created PulseBlockEnsemble objects
  to the highest instance together in a PulseSequence object.
"""
class rfsequences(Enum):
    rabi = 'rabi'
    ramsey = 'ramsey'
    spinecho = 'spin_echo'
    cwdrive = 'cwdrive'
    T1 = 'T1'
    
class mwsequences(Enum):
    spinecho = 'spin_echo'
    XY8 = 'XY8'
    spinlock = 'spin_lock'
    
class rfchannels(Enum):
    x = 'x'
    mx = '-x'
    y = 'y'
    my = '-y'
    rf = 'rf'
    
class pulsesequences(Enum):
    ramsey = 'ramsey'
    ramseymw = 'ramseymw'
    ramseysweep = 'ramsey_sweep'
    spinecho = 'spin_echo'
    spinechosweep = 'spin_echo_sweep'
    mwrabi = 'mwrabi'

#defaultsdic = {phase:[0,360,10], time:[0,10e-6, 1e-6], freq:[5.05e6, 5.1e6, 5e3]}
class rfvariables(Enum):
    time = 'time'
    freq = 'freq'   
    phase = 'phase'
    NVphase = 'NVphase'
    

def dBmtoV(pdbm):
    pwatts = 10**((pdbm-30)/10)
    vrms = np.sqrt(50*pwatts)
    return 2*np.sqrt(2)*vrms
  
class BasicPredefinedGenerator(PredefinedGeneratorBase):
    """

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    ################################################################################################
    #                             Generation methods for waveforms                                 #
    ################################################################################################
    def generate_laser_on(self, name='laser_on', length=3.0e-6):
        """ Generates Laser on.

        @param str name: Name of the PulseBlockEnsemble
        @param float length: laser duration in seconds

        @return object: the generated PulseBlockEnsemble object.
        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # create the laser element
        laser_element = self._get_laser_element(length=length, increment=0)
        # Create block and append to created_blocks list
        laser_block = PulseBlock(name=name)
        laser_block.append(laser_element)
        created_blocks.append(laser_block)
        # Create block ensemble and append to created_ensembles list
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((laser_block.name, 0))
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_laser_mw_on(self, name='laser_mw_on', length=3.0e-6):
        """ General generation method for laser on and microwave on generation.

        @param string name: Name of the PulseBlockEnsemble to be generated
        @param float length: Length of the PulseBlockEnsemble in seconds

        @return object: the generated PulseBlockEnsemble object.
        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # create the laser_mw element
        laser_mw_element = self._get_mw_laser_element(length=length,
                                                      increment=0,
                                                      amp=self.microwave_amplitude,
                                                      freq=self.microwave_frequency,
                                                      phase=0)
        # Create block and append to created_blocks list
        laser_mw_block = PulseBlock(name=name)
        laser_mw_block.append(laser_mw_element)
        created_blocks.append(laser_mw_block)
        # Create block ensemble and append to created_ensembles list
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((laser_mw_block.name, 0))
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_two_digital_high(self, name='digital_high', length=3.0e-6, digital_channel1='d_ch1', digital_channel2='d_ch1'):
        """ General generation method for laser on and microwave on generation.

        @param string name: Name of the PulseBlockEnsemble to be generated
        @param float length: Length of the PulseBlockEnsemble in seconds

        @return object: the generated PulseBlockEnsemble object.
        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        digital_channels = list([digital_channel1, digital_channel2])
        # create the laser_mw element
        trigger_element = self._get_trigger_element(length =length,
                                                    increment=0,
                                                    channels=list(digital_channels))

        # Create block and append to created_blocks list
        laser_mw_block = PulseBlock(name=name)
        laser_mw_block.append(trigger_element)
        created_blocks.append(laser_mw_block)
        # Create block ensemble and append to created_ensembles list
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((laser_mw_block.name, 0))
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_idle(self, name='idle', length=3.0e-6):
        """ Generate just a simple idle ensemble.

        @param str name: Name of the PulseBlockEnsemble to be generated
        @param float length: Length of the PulseBlockEnsemble in seconds

        @return object: the generated PulseBlockEnsemble object.
        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # create the laser_mw element
        idle_element = self._get_idle_element(length=length, increment=0)
        # Create block and append to created_blocks list
        idle_block = PulseBlock(name=name)
        idle_block.append(idle_element)
        created_blocks.append(idle_block)
        # Create block ensemble and append to created_ensembles list
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((idle_block.name, 0))
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_rabi(self, name='rabi', tau_start=1.0e-9, tau_step=10.0e-9, num_of_points=50, abs_phase=0, rfchan = rfchannels.x):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        #channel = rfchan.value
        iq_freq = self.IQ_freq

        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # mw_element = self._get_mwp_element(length=tau_start,
                                          # increment=tau_step,
                                          # amp=self.microwave_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=channel)        
                                          
        awgtrig_element = self._get_awgtrig_element()
        
        mw_element = self._get_mw_element(length=tau_start,
                                          increment=tau_step,
                                          amp=self.microwave_amplitude,
                                          freq=iq_freq,
                                          phase=abs_phase)

        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length,
                                                     increment=0)
        delay_element = self._get_delay_gate_element()

        # Create block and append to created_blocks list
        rabi_block = PulseBlock(name=name)
        # rabi_block.append(awgtrig_element)
        rabi_block.append(mw_element)
        rabi_block.append(waiting_element)
        rabi_block.append(laser_element)
        rabi_block.append(delay_element)
        rabi_block.append(waiting_element)
        created_blocks.append(rabi_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((rabi_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
        # add metadata to invoke settings later on
        block_ensemble.measurement_information['alternating'] = False
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = num_of_points
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # Append ensemble to created_ensembles list
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_pulsedodmr(self, name='pulsedODMR', freq_start=2870.0e6, freq_step=0.2e6,
                            num_of_points=50):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # Create frequency array
        freq_array = freq_start + np.arange(num_of_points) * freq_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length,
                                                     increment=0)
        delay_element = self._get_delay_gate_element()

        # Create block and append to created_blocks list
        pulsedodmr_block = PulseBlock(name=name)
        for mw_freq in freq_array:
            mw_element = self._get_mw_element(length=self.rabi_period / 2,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=mw_freq,
                                              phase=0)
            pulsedodmr_block.append(mw_element)
            pulsedodmr_block.append(laser_element)
            pulsedodmr_block.append(delay_element)
            pulsedodmr_block.append(waiting_element)
        created_blocks.append(pulsedodmr_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((pulsedodmr_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        block_ensemble.measurement_information['alternating'] = False
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = freq_array
        block_ensemble.measurement_information['units'] = ('Hz', '')
        block_ensemble.measurement_information['labels'] = ('Frequency', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = num_of_points
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    # def generate_ramsey(self, name='ramsey', tau_start=1.0e-6, tau_step=1.0e-6, num_of_points=50,
                        # alternating=True):
        # """

        # """
        # created_blocks = list()
        # created_ensembles = list()
        # created_sequences = list()

        # # get tau array for measurement ticks
        # tau_array = tau_start + np.arange(num_of_points) * tau_step

        # # create the elements
        # waiting_element = self._get_idle_element(length=self.wait_time,
                                                 # increment=0)
        # laser_element = self._get_laser_gate_element(length=self.laser_length,
                                                     # increment=0)
        # delay_element = self._get_delay_gate_element()
        # pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              # increment=0,
                                              # amp=self.microwave_amplitude,
                                              # freq=self.microwave_frequency,
                                              # phase=0)
        # # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        # if self.microwave_channel.startswith('a'):
            # pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   # increment=0,
                                                   # amp=self.microwave_amplitude,
                                                   # freq=self.microwave_frequency,
                                                   # phase=180)
        # else:
            # pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   # increment=0,
                                                   # amp=self.microwave_amplitude,
                                                   # freq=self.microwave_frequency,
                                                   # phase=0)
        # tau_element = self._get_idle_element(length=tau_start, increment=tau_step)

        # # Create block and append to created_blocks list
        # ramsey_block = PulseBlock(name=name)
        # ramsey_block.append(pihalf_element)
        # ramsey_block.append(tau_element)
        # ramsey_block.append(pihalf_element)
        # ramsey_block.append(laser_element)
        # ramsey_block.append(delay_element)
        # ramsey_block.append(waiting_element)
        # if alternating:
            # ramsey_block.append(pihalf_element)
            # ramsey_block.append(tau_element)
            # ramsey_block.append(pi3half_element)
            # ramsey_block.append(laser_element)
            # ramsey_block.append(delay_element)
            # ramsey_block.append(waiting_element)
        # created_blocks.append(ramsey_block)

        # # Create block ensemble
        # block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        # block_ensemble.append((ramsey_block.name, num_of_points - 1))

        # # Create and append sync trigger block if needed
        # if self.sync_channel:
            # sync_block = PulseBlock(name='sync_trigger')
            # sync_block.append(self._get_sync_element())
            # created_blocks.append(sync_block)
            # block_ensemble.append((sync_block.name, 0))

        # # add metadata to invoke settings later on
        # number_of_lasers = 2 * num_of_points if alternating else num_of_points
        # block_ensemble.measurement_information['alternating'] = alternating
        # block_ensemble.measurement_information['laser_ignore_list'] = list()
        # block_ensemble.measurement_information['controlled_variable'] = tau_array
        # block_ensemble.measurement_information['units'] = ('s', '')
        # block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        # block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        # block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            # ensemble=block_ensemble, created_blocks=created_blocks)

        # # append ensemble to created ensembles
        # created_ensembles.append(block_ensemble)
        # return created_blocks, created_ensembles, created_sequences
        
    def generate_ramsey(self, name='ramsey', tau_start=0.0e-6, tau_step=1.0e-6,
                          num_of_points=50, alternating=True, rfchan = rfchannels.x):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        channel = rfchan.value

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mwp_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=channel)
        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=channel)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mwp_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=channel)
        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)

        # Create block and append to created_blocks list
        ramsey_block = PulseBlock(name=name)
        ramsey_block.append(pihalf_element)
        ramsey_block.append(tau_element)
        # hahn_block.append(pi_element)
        ramsey_block.append(tau_element)
        ramsey_block.append(pihalf_element)
        ramsey_block.append(lasergate_element)
        ramsey_block.append(laser_element)
        ramsey_block.append(delay_element)
        ramsey_block.append(waiting_element)
        if alternating:
            ramsey_block.append(pihalf_element)
            ramsey_block.append(tau_element)
            # hahn_block.append(pi_element)
            ramsey_block.append(tau_element)
            ramsey_block.append(pi3half_element)
            ramsey_block.append(lasergate_element)
            ramsey_block.append(laser_element)
            ramsey_block.append(delay_element)
            # hahn_block.append(waiting_element)
        created_blocks.append(ramsey_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((ramsey_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_ramsey_from_list(self, name='ramsey', tau_list='[1e-6, 2e-6]', alternating = True):
        """

        """

        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get tau array for measurement ticks
        tau_array = [n.strip() for n in tau_list]

        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length,
                                                     increment=0)
        delay_element = self._get_delay_gate_element()
        # get pihalf element
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)

        if alternating:
            if self.microwave_channel.startswith('a'):
                pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                       increment=0,
                                                       amp=self.microwave_amplitude,
                                                       freq=self.microwave_frequency,
                                                       phase=180)
            else:
                pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                       increment=0,
                                                       amp=self.microwave_amplitude,
                                                       freq=self.microwave_frequency,
                                                       phase=0)

        # Create block and append to created_blocks list
        ramsey_block = PulseBlock(name=name)
        for tau in tau_array:
            tau_element = self._get_idle_element(length=tau, increment=0)
            ramsey_block.append(pihalf_element)
            ramsey_block.append(tau_element)
            ramsey_block.append(tau_element)
            ramsey_block.append(pihalf_element)
            ramsey_block.append(laser_element)
            ramsey_block.append(delay_element)
            ramsey_block.append(waiting_element)

            if alternating:
                ramsey_block.append(pihalf_element)
                ramsey_block.append(tau_element)
                ramsey_block.append(pi3half_element)
                ramsey_block.append(laser_element)
                ramsey_block.append(delay_element)
                ramsey_block.append(waiting_element)

        created_blocks.append(ramsey_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((ramsey_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
        # add metadata to invoke settings later on
        number_of_lasers = 2 * len(tau_array) if alternating else len(tau_array)
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_hahnecho(self, name='hahn_echo', tau_start=1e-9, tau_step=1.0e-6,
                          num_of_points=5, alternating=True, pi32 = True, phase0 = 'x', phase1 = 'x', phase2 = 'x'):
        """

        """
        if tau_start < 1e-9:
            tau_start = tau_start + 1e-9
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        # I_element = self._get_I_element(length=self.rabi_period,
                              # increment=0,
                              # amp=self.I_amplitude)
        #Q_element = self._get_Q_element(length=self.rabi_period,
                      #        increment=0,
        #                      amp=self.Q_amplitude)

        
        first_element = self._get_mwp_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=phase0)
        second_element = self._get_mwp_element(length=self.rabi_period / 2,
                                              increment=0,
                                              amp=None,
                                              freq=None,
                                              phase=phase1)
        third_element = self._get_mwp_element(length=self.rabi_period / 4,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase=phase2)

        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3halfx_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=-self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        else:
            pi32_element = self._get_mwp_element(length= 3*self.rabi_period / 4 if pi32 else self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase='x' if pi32 else '-x')
          #  pi3halfy_element = self._get_Q_element(length=3 * self.rabi_period_y / 4,
                                               #    increment=0,
                                               #    amp=self.microwave_amplitude,
                                               #    freq=self.microwave_frequency,
                                               #    phase=0)
        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)

        # Create block and append to created_blocks list
        hahn_block = PulseBlock(name=name)

        hahn_block.append(first_element)
        hahn_block.append(tau_element)
        hahn_block.append(second_element)
        hahn_block.append(tau_element)
        hahn_block.append(third_element)

        hahn_block.append(waiting_element)
        hahn_block.append(lasergate_element)
        hahn_block.append(laser_element)
        hahn_block.append(delay_element)
        hahn_block.append(waiting_element)
        if alternating:
            hahn_block.append(first_element)
            hahn_block.append(tau_element)
            hahn_block.append(second_element)
            hahn_block.append(tau_element)
            hahn_block.append(pi32_element)
            hahn_block.append(waiting_element)
            hahn_block.append(lasergate_element)
            hahn_block.append(laser_element)
            hahn_block.append(delay_element)
            hahn_block.append(waiting_element)
        created_blocks.append(hahn_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((hahn_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
        
    def generate_XY8(self, name='XY8', tau_start=10e-9, tau_step=1.0e-6,tau_init = 1.0e-6,
                          num_of_points=50, alternating=True, symmetric = True, pi32 = True, order = 1, phases = 'x,y,x,y,y,x,y,x'):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        phaselist = phases.split(",")
        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,increment=0)

                                                 
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        

        
        
        pihalfx_element = self._get_mwp_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=None,
                                              freq=None,
                                              phase='x')


        pix_element = self._get_mwp_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase='x')
        pimx_element = self._get_mwp_element(length=self.rabi_period_mx / 2,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase='-x')
        piy_element = self._get_mwp_element(length=self.rabi_period_y / 2,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase='y')
        pimy_element = self._get_mwp_element(length=self.rabi_period_my / 2,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase='-y')
        # pimx_element = self._get_mw_element(length=self.rabi_periodmx / 2,
                                          # increment=0,
                                          # amp=-self.microwave_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=0)
        # pimy_element = self._get_Q_element(length=self.rabi_period_my / 2,
                                          # increment=0,
                                          # amp=-self.Q_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=0)
        # phasedic = {'x': pix_element, '-x':pimx_element, 'y':piy_element, '-y':pimy_element}
        phasedic = {'x': pix_element, 'y':piy_element,'-x': pimx_element, '-y':pimy_element}
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3halfx_element = self._get_mw_element(length=self.rabi_periodmx / 4,
                                                   increment=0,
                                                   amp=-self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        else:
            pi32_element = self._get_mwp_element(length=3 * self.rabi_period / 4 if pi32 else self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase='x' if pi32 else '-x')
        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)
        tauinit_element = self._get_idle_element(length=tau_init, increment=0)
        tauon2_element = self._get_idle_element(length=tau_start/2., increment=tau_step/2.)

        # Create block and append to created_blocks list
        XY8_block = PulseBlock(name=name)
        XY8_block.append(pihalfx_element)
        
        if symmetric:
            XY8_block.append(tauon2_element)
        else:
            XY8_block.append(tauinit_element)
        for i in range(order):
            for phase in phaselist:
                XY8_block.append(phasedic[phase])
                XY8_block.append(tau_element)
        XY8_block.pop()

        if symmetric:
            XY8_block.append(tauon2_element)
        else:
            XY8_block.append(tauinit_element)
        XY8_block.append(pihalfx_element)
        #Readout
        XY8_block.append(lasergate_element)
        XY8_block.append(laser_element)
        XY8_block.append(delay_element)
        XY8_block.append(waiting_element)
        if alternating:
            XY8_block.append(pihalfx_element)
            if symmetric:
                XY8_block.append(tauon2_element)
            else:
                XY8_block.append(tauinit_element)
            for i in range(order):

                for phase in phaselist:
                    XY8_block.append(phasedic[phase])
                    XY8_block.append(tau_element)
            XY8_block.pop()

            if symmetric:
                XY8_block.append(tauon2_element)
            else:
                XY8_block.append(tauinit_element)

        XY8_block.append(pi32_element)

        XY8_block.append(lasergate_element)
        XY8_block.append(laser_element)
        XY8_block.append(delay_element)
        XY8_block.append(waiting_element)
        created_blocks.append(XY8_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((XY8_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array 
        block_ensemble.measurement_information['order'] = order
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
        
    def generate_XY8awg(self, name='XY8awg', tau_start=10e-9, tau_step=1.0e-6,tau_init = 1.0e-6,
                          num_of_points=50, alternating=True, symmetric = True, xmid = True, pi32 = True, order = 1, phases = 'x,y,x,y,y,x,y,x'):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        phaselist = phases.split(",")
        number_of_pulses = len(phaselist)
        phaselist1 = phaselist[:int(number_of_pulses/2)]
        phaselist2 = phaselist[int(number_of_pulses/2):]
        
        mw_period = self.rabi_period
        iq_freq = self.IQ_freq
        
        
        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment = 0)
        delay_element = self._get_delay_gate_element()
        awgtrig_element = self._get_awgtrig_element()
        
        # Create block and append to created_blocks list
        XY8awg_block = PulseBlock(name=name)
        
        # IQ phase correction
        def mw_func(block_name=XY8awg_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        
        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)
        tauinit_element = self._get_idle_element(length=tau_init, increment=0)
        tauon2_element = self._get_idle_element(length=tau_start/2., increment=tau_step/2.)
        
        phasedic = {'x':0, 'y':90}

        XY8awg_block.append(mw_func(XY8awg_block,'pi2',0))
        
        if symmetric:
            XY8awg_block.append(tauon2_element)
        else:
            XY8awg_block.append(tauinit_element)
        
        if xmid:
            for i in range(order):
                for ph in phaselist1:
                    XY8awg_block.append(mw_func(XY8awg_block,'pi',phasedic[ph]))
                    XY8awg_block.append(tau_element)
                XY8awg_block.pop()
                XY8awg_block.append(tauon2_element)
                XY8awg_block.append(mw_func(XY8awg_block,'pi',0))
                XY8awg_block.append(tauon2_element)
                for ph in phaselist2:
                    XY8awg_block.append(mw_func(XY8awg_block,'pi',phasedic[ph]))
                    XY8awg_block.append(tau_element)
            XY8awg_block.pop()
                
        else:
            for i in range(order):
                for ph in phaselist:
                    XY8awg_block.append(mw_func(XY8awg_block,'pi',phasedic[ph]))
                    XY8awg_block.append(tau_element)
            XY8awg_block.pop()

        if symmetric:
            XY8awg_block.append(tauon2_element)
        else:
            XY8awg_block.append(tauinit_element)
        XY8awg_block.append(mw_func(XY8awg_block,'pi2',0))
        #Readout
        XY8awg_block.append(waiting_element)
        XY8awg_block.append(laser_element)
        XY8awg_block.append(delay_element)
        XY8awg_block.append(waiting_element)
        if alternating:
            XY8awg_block.append(mw_func(XY8awg_block,'pi2',0))
            if symmetric:
                XY8awg_block.append(tauon2_element)
            else:
                XY8awg_block.append(tauinit_element)
                
            if xmid:
                for i in range(order):
                    for ph in phaselist1:
                        XY8awg_block.append(mw_func(XY8awg_block,'pi',phasedic[ph]))
                        XY8awg_block.append(tau_element)
                    XY8awg_block.pop()
                    XY8awg_block.append(tauon2_element)
                    XY8awg_block.append(mw_func(XY8awg_block,'pi',0))
                    XY8awg_block.append(tauon2_element)
                    for ph in phaselist2:
                        XY8awg_block.append(mw_func(XY8awg_block,'pi',phasedic[ph]))
                        XY8awg_block.append(tau_element)
                XY8awg_block.pop()
            else:
                for i in range(order):
                    for phase in phaselist:
                        XY8awg_block.append(mw_func(XY8awg_block,'pi',phasedic[ph]))
                        XY8awg_block.append(tau_element)
                XY8awg_block.pop()

            if symmetric:
                XY8awg_block.append(tauon2_element)
            else:
                XY8awg_block.append(tauinit_element)

        XY8awg_block.append(mw_func(XY8awg_block,'pi32',180))

        XY8awg_block.append(waiting_element)
        XY8awg_block.append(laser_element)
        XY8awg_block.append(delay_element)
        XY8awg_block.append(waiting_element)
        created_blocks.append(XY8awg_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((XY8awg_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))   

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array 
        block_ensemble.measurement_information['order'] = order
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
    
    # def generate_DDRF(self, name='DDRF',tau_init = 10e-6, tau_start=10e-9, tau_step=1.0e-6, t_rf = 1000e-9,
                          # num_of_points=5, alternating=True, tau_init_incr = False, order = 1, DDphases = 'x,y,x,y,y,x,y,x'):
        # """

        # """
        # created_blocks = list()
        # created_ensembles = list()
        # created_sequences = list()
        # phaselist = DDphases.split(",")
        # # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        # laser_length_gate = 3e-6 #laser gates are 3us
        # print('appending laser length')
        # laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # # get tau array for measurement ticks
        # tau_array = tau_start + np.arange(num_of_points) * tau_step

        # # create the elements
        # waiting_element = self._get_idle_element(length=self.wait_time,
                                                 # increment=0)
        # lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        # laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        # delay_element = self._get_delay_gate_element()
        

        
        
        # pihalfx_element = self._get_mw_element(length=self.rabi_period / 4,
                                              # increment=0,
                                              # amp=self.microwave_amplitude,
                                              # freq=self.microwave_frequency,
                                              # phase=0)

        # pihalfy_element = self._get_Q_element(length=self.rabi_period_y / 4,
                                              # increment=0,
                                              # amp=self.Q_amplitude,
                                              # freq=self.microwave_frequency,
                                              # phase=0)
        # pix_element = self._get_mw_element(length=self.rabi_period / 2,
                                          # increment=0,
                                          # amp=self.microwave_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=0)
        # piy_element = self._get_Q_element(length=self.rabi_period_y / 2,
                                          # increment=0,
                                          # amp=self.Q_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=0)
        # pimx_element = self._get_mw_element(length=self.rabi_periodmx / 2,
                                          # increment=0,
                                          # amp=-self.microwave_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=0)
        # pimy_element = self._get_Q_element(length=self.rabi_period_my / 2,
                                          # increment=0,
                                          # amp=-self.Q_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=0)
        # phasedic = {'x': pix_element, '-x':pimx_element, 'y':piy_element, '-y':pimy_element}
        # # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        # if self.microwave_channel.startswith('a'):
            # pi3halfx_element = self._get_mw_element(length=self.rabi_periodmx / 4,
                                                   # increment=0,
                                                   # amp=-self.microwave_amplitude,
                                                   # freq=self.microwave_frequency,
                                                   # phase=0)
        # else:
            # pi3halfx_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   # increment=0,
                                                   # amp=self.microwave_amplitude,
                                                   # freq=self.microwave_frequency,
                                                   # phase=0)
        # tau_element = self._get_idle_element(length=tau_start, increment=tau_step)
        # tauinit_element = self._get_idle_element(length=tau_start/2. if tau_init_incr else tau_init, increment=tau_step/2. if tau_init_incr else 0)
        # rf_element = self._get_rf_element(length=t_rf,
                                          # increment=0,
                                          # amp=None,
                                          # freq=None,
                                          # phase=0)
        # rfmwtau_elements = self._get_rfmwtau_element(length_rf=t_rf,
                                          # length_mw=self.rabi_period/2,
                                          # length_tau=tau_start,
                                          # increment=tau_step,
                                          # amp=None,
                                          # freq=None,
                                          # phase=0)
        # # Create block and append to created_blocks list
        # DDRF_block = PulseBlock(name=name)
        # RF_block = PulseBlock(name='rf')
        
        # DDRF_block.append(pihalfx_element)
        # DDRF_block.append(tauinit_element)
        # RF_block.append(tauinit_element)
        # RF_block.append(rf_element)
        # RF_block.append(tauinit_element)
        # # DDRF_block.append(rf_element)     

        # for i in range(order):
            # for phase in phaselist:
                # DDRF_block.append(phasedic[phase])
                # DDRF_block.append(tau_element)

        # DDRF_block.append(pix_element)
        # DDRF_block.append(tau_element)

        # for i in range(order):
            # for phase in phaselist:
                # DDRF_block.append(phasedic[phase])
                # DDRF_block.append(tau_element)
        # DDRF_block.pop()
        # # DDRF_block.append(rf_element) 
        # DDRF_block.append(tauinit_element)
        # DDRF_block.append(pihalfx_element)
        # #Readout
        # DDRF_block.append(lasergate_element)
        # DDRF_block.append(laser_element)
        # DDRF_block.append(delay_element)
        # DDRF_block.append(waiting_element)
        # if alternating:
            
            # DDRF_block.append(pihalfx_element)
            # DDRF_block.append(tauinit_element)
      
            # for i in range(order):
                # for phase in phaselist:
                    # DDRF_block.append(phasedic[phase])
                    # DDRF_block.append(tau_element)

            # DDRF_block.append(pix_element)
            # DDRF_block.append(tau_element)
            # for i in range(order):
                # for phase in phaselist:
                    # DDRF_block.append(phasedic[phase])
                    # DDRF_block.append(tau_element)
            # DDRF_block.pop()
            # DDRF_block.append(tauinit_element)
        

        # DDRF_block.append(pi3halfx_element)

        # DDRF_block.append(lasergate_element)
        # DDRF_block.append(laser_element)
        # DDRF_block.append(delay_element)
        # DDRF_block.append(waiting_element)
        # created_blocks.append(DDRF_block)
        # created_blocks.append(RF_block)

        # # Create block ensemble
        # block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        # block_ensemble.append((DDRF_block.name, num_of_points - 1))
        # block_ensemble.append((RF_block.name, num_of_points - 1))

        # # Create and append sync trigger block if needed
        # if self.sync_channel:
            # sync_block = PulseBlock(name='sync_trigger')
            # sync_block.append(self._get_sync_element())
            # created_blocks.append(sync_block)
            # block_ensemble.append((sync_block.name, 0))

        # # add metadata to invoke settings later on
        # number_of_lasers = 2 * num_of_points if alternating else num_of_points
        # block_ensemble.measurement_information['alternating'] = alternating
        # block_ensemble.measurement_information['laser_ignore_list'] = list()
        # block_ensemble.measurement_information['controlled_variable'] = tau_array 
        # block_ensemble.measurement_information['order'] = order
        # block_ensemble.measurement_information['units'] = ('s', '')
        # block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        # block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        # block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            # ensemble=block_ensemble, created_blocks=created_blocks)

        # # append ensemble to created ensembles
        # created_ensembles.append(block_ensemble)
        # return created_blocks, created_ensembles, created_sequences
    
    
    def generate_DDRF(self, name='DDRF',time_off = 10e-6, tau_init = 1e-6, tau_start=10e-9, tau_step=0.1e-6, t_rf = 1000e-9,
                          num_of_points=10, alternating=True, auto_phases = False, N_dd = 2,logic_0 = True,pi32 = False,  DDphases = 'x,y,x,y,y,x,y,x', rfseq = rfsequences.ramsey):
        """
        If fixed interpulse, then 'time off' is tau.
        """
        fold_sequence = True
        fold_channel = 'd_ch5'
        rfseqrun = rfseq.value
        tshift = 0

        order = 1
        evdic = {0:'x',1:'y'}
        if auto_phases:
            phaselist = [evdic[np.mod(n,2)] for n in range(N_dd)]
        else:    
            phaselist = DDphases.split(",")
        
        lendd = len(phaselist)
        tmax = tau_start + num_of_points*tau_step*2 + t_rf*(1/4 + 1/2 + 3/4)
        timedd = {'0': 0,'x':self.rabi_period/2, 'y': self.rabi_period_y/2}
        lenmw = np.array([timedd[phase] for phase in phaselist]).sum()
        tdd = 2 * np.array([timedd[phase]+time_off/lendd for phase in phaselist]).sum() + self.rabi_period/2 #this is the total time taken for the whole DD sequence, start to finish
        if tmax > tdd:
            self.log.warning('the total range spanned by the rf sequence exceeds t_off. Increase t_off. ')
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        
        if self.microwave_channel.startswith('a') and fold_sequence:
            self.log.error('Have not implemented sequence folding with analog channels yet.')
        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us

        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        

        if self.microwave_channel.startswith('a'):
            pi3halfx_element = self._get_mw_element(length=self.rabi_periodmx / 4,
                                                   increment=0,
                                                   amp=-self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        else:
            pi3halfx_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
          
        phasedic = {'0':self._get_idle_element(length = 0,increment = 0), 'x':self._get_mwxy_element(self.rabi_period/2, 'x'), 'y':self._get_mwxy_element(self.rabi_period_y/2, 'y')}
        
        timeoff_element = self._get_idle_element(length=time_off/lendd if not rfseqrun == 'cwdrive' else tau_start, increment=0 if not rfseqrun == 'cwdrive' else tau_step)

        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)
        tauinit_element = self._get_idle_element(tau_init, increment= 0)
        rfpi2_element = self._get_rf_element(length=t_rf/4.,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase=0)
        rfpi_element = self._get_rf_element(length=t_rf/2.,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase=0)
        rf3pi2_element = self._get_rf_element(length=3/4.*t_rf,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase=0)
        rfpi2_element_idle = self._get_idle_element(length=t_rf/4.,
                                          increment=0)
        rfpi_element_idle = self._get_idle_element(length=t_rf/2.,
                                          increment=0)
        rf3pi2_element_idle = self._get_idle_element(length=3/4.*t_rf,
                                          increment=0)
        rfdrive_element = self._get_rf_element(length=tau_start*len(phaselist) + lenmw + self.rabi_period/4,
                                          increment=tau_step*len(phaselist),
                                          amp=None,
                                          freq=None,
                                          phase=0)
        rfrabi_element = self._get_rf_element(length=tau_start/2,
                                          increment=tau_step/2,
                                          amp=None,
                                          freq=None,
                                          phase=0)

        
        
        
        # Create block and append to created_blocks list
        DDRF_block = PulseBlock(name=name)
        RF_block = PulseBlock(name='RF')
        
        
        DDRF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x'))
        RF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x', state = 'idle'))
        
        DDRF_block.append(tauinit_element)
        RF_block.append(tauinit_element)
        #rf active area, async
    
        ### Silent Sequence MW
        for i in range(order):
            for phase in phaselist:
                DDRF_block.append(phasedic[phase])
                DDRF_block.append(timeoff_element)
        
        DDRF_block.append(self._get_mwxy_element(self.rabi_period/2, 'x'))
        DDRF_block.append(timeoff_element)
        for i in range(order):
            for phase in phaselist[::-1] if True else phaselist:
                DDRF_block.append(phasedic[phase])
                DDRF_block.append(timeoff_element)
        DDRF_block.pop()

        DDRF_block.append(tauinit_element)
        DDRF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x'))
        ##Active sequence RF. From here...
        if rfseqrun == 'T1':
            buffer_element_1 = self._get_idle_element(tau_start, increment=tau_step)
            buffer_element_2 = self._get_idle_element(tdd-tau_start-t_rf, increment=-1*tau_step)
            RF_block.append(buffer_element_1)
            RF_block.append(rfpi_element)
            RF_block.append(buffer_element_2)
            RF_block.append(rfpi_element if logic_0 else rfpi_element_idle)
            RF_block.append(tauinit_element)
            RF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x', state = 'idle')) 
        elif rfseqrun == 'ramsey' or rfseqrun == 'spin_echo':

            buffer_element_1 = self._get_idle_element(length=tdd/2-tau_start-t_rf/2 - tshift if rfseqrun == 'spin_echo' else tdd/2-tau_start-t_rf/4-tshift, increment=-1*tau_step)
            buffer_element_2 = self._get_idle_element(length=tdd/2-tau_start-t_rf/2 + tshift if rfseqrun == 'spin_echo' else tdd/2-tau_start-t_rf/4+tshift, increment=-1*tau_step)
            RF_block.append(buffer_element_1)
            RF_block.append(rfpi2_element )
            RF_block.append(tau_element)
            if rfseqrun =='spin_echo':
                RF_block.append(rfpi_element)
            RF_block.append(tau_element)

            RF_block.append(rfpi2_element)
            RF_block.append(buffer_element_2)
            RF_block.append(tauinit_element)
            RF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x', state = 'idle'))      
        elif rfseqrun == 'rabi':    
            buffer_element_1 = self._get_idle_element(tdd/2 -tau_start/2-tshift, increment=-1*tau_step/2)
            buffer_element_2 = self._get_idle_element(tdd/2 -tau_start/2+tshift, increment=-1*tau_step/2)
            RF_block.append(buffer_element_1)
            RF_block.append(rfrabi_element)
            RF_block.append(rfrabi_element)
            RF_block.append(buffer_element_2)
            RF_block.append(tauinit_element)
            RF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x', state = 'idle'))   
        #...to here must equal tdd
        else:
            RF_block.append(rfdrive_element)
            RF_block.append(rfdrive_element)
            RF_block.append(tauinit_element)
            RF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x', state = 'idle')) 
        
        # the total time elapsed during this part is: the length of one DDseq
        
        #Readout
        DDRF_block.append(lasergate_element)
        DDRF_block.append(laser_element)
        DDRF_block.append(delay_element)
        DDRF_block.append(waiting_element)
        
        RF_block.append(lasergate_element)
        RF_block.append(laser_element)
        RF_block.append(delay_element)
        RF_block.append(waiting_element)
        
        if alternating:
            DDRF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x'))
            RF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x', state = 'idle'))
            
            DDRF_block.append(tauinit_element)
            RF_block.append(tauinit_element)
            #rf active area, async
        
            ### Silent Sequence MW
            for i in range(order):
                for phase in phaselist:
                    DDRF_block.append(phasedic[phase])
                    DDRF_block.append(timeoff_element)
            
            DDRF_block.append(self._get_mwxy_element(self.rabi_period/2, 'x'))
            DDRF_block.append(timeoff_element)
            for i in range(order):
                for phase in phaselist[::-1] if True else phaselist:
                    DDRF_block.append(phasedic[phase])
                    DDRF_block.append(timeoff_element)
            DDRF_block.pop()

            DDRF_block.append(tauinit_element)
            DDRF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x'))
            ##Active sequence RF. From here...

            if rfseqrun == 'ramsey' or rfseqrun == 'spin_echo':
                buffer_element = self._get_idle_element(length=tdd/2-tau_start-t_rf/2. if rfseqrun == 'spin_echo' else tdd/2-tau_start-t_rf/4., increment=-1*tau_step)
                buffer_element_3p2 = self._get_idle_element(length=tdd/2-tau_start-t_rf if rfseqrun == 'spin_echo' else tdd/2-tau_start-3*t_rf/4., increment=-1*tau_step)
                RF_block.append(buffer_element)
                RF_block.append(rfpi2_element if pi32 else rfpi2_element_idle)
                RF_block.append(tau_element)
                if rfseqrun == 'spin_echo':
                    RF_block.append(rfpi_element if pi32 else rfpi_element_idle)
                RF_block.append(tau_element)
                RF_block.append(rf3pi2_element if pi32 else rf3pi2_element_idle)
                RF_block.append(buffer_element_3p2)

            else:
                for i in range(order):
                    for phase in phaselist:
                        RF_block.append(phasedic[phase])
                        RF_block.append(timeoff_element)
                    
                    RF_block.append(self._get_mwxy_element(self.rabi_period/2, 'x'))
                    RF_block.append(timeoff_element)
                    for i in range(order):
                        for phase in phaselist:
                            RF_block.append(phasedic[phase])
                            RF_block.append(timeoff_element)
                    RF_block.pop()
                
            RF_block.append(tauinit_element)
            RF_block.append(self._get_mwxy_element(self.rabi_period/4, 'x', state = 'idle'))      
            #...to here must equal tdd
            
            
            # the total time elapsed during this part is: the length of one DDseq
            
            #Readout
            DDRF_block.append(lasergate_element)
            DDRF_block.append(laser_element)
            DDRF_block.append(delay_element)
            DDRF_block.append(waiting_element)
            
            RF_block.append(lasergate_element)
            RF_block.append(laser_element)
            RF_block.append(delay_element)
            RF_block.append(waiting_element)
 
        created_blocks.append(DDRF_block)
        

        created_blocks.append(RF_block)
        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)

        block_ensemble.append((DDRF_block.name, num_of_points - 1))
        block_ensemble.append((RF_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['fold_sequence'] = fold_sequence
        block_ensemble.measurement_information['fold_channel'] = fold_channel
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array 
        block_ensemble.measurement_information['order'] = order
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
        
        
    def generate_deer(self, name='deer', t_rf_start=1.0e-9, t_rf_step=100.0e-9,
                          num_of_points=1, t_SE = 84e-6,t_buff = 1e-5, alternating=True):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        t_rf_array = t_rf_start + np.arange(num_of_points) * t_rf_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
        rf_element = self._get_rf_element(length=t_rf_start,
                                          increment=t_rf_step,
                                          amp=None,
                                          freq=None,
                                          phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        tau1_element = self._get_idle_element(length=t_SE-t_buff-t_rf_start, increment=-1*t_rf_step)
        buff_element = self._get_idle_element(length=t_buff, increment=0)
        tau_element = self._get_idle_element(length=t_SE, increment=0)

        # Create block and append to created_blocks list
        deer_block = PulseBlock(name=name)
        deer_block.append(pihalf_element)
        deer_block.append(tau1_element)
        deer_block.append(rf_element)
        deer_block.append(buff_element)
        deer_block.append(pi_element)
        deer_block.append(tau_element)
        deer_block.append(pihalf_element)

        deer_block.append(lasergate_element)
        deer_block.append(laser_element)
        deer_block.append(delay_element)
        deer_block.append(waiting_element)
        if alternating:
            deer_block.append(pihalf_element)
            deer_block.append(tau_element)
            deer_block.append(pi_element)
            deer_block.append(tau_element)
            deer_block.append(pihalf_element)

            deer_block.append(lasergate_element)
            deer_block.append(laser_element)
            deer_block.append(delay_element)
            deer_block.append(waiting_element)
        created_blocks.append(deer_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((deer_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = t_rf_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences 
        
    def generate_deerdrive(self, name='deerdrive', t_rf=200.0e-9, tau_start=1e-9, tau_step=1e-6,
                          num_of_points=1, alternating=True):
        
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalfrf_element = self._get_mwrf_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        pirf_element = self._get_mwrf_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
        rf_element = self._get_rf_element(length=t_rf,
                                          increment=0,
                                          amp=None,
                                          freq=None,
                                          phase=0)   
        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)
        tau_norf_element = self._get_idle_element(length=tau_start + t_rf, increment=tau_step)
                                          

        # Create block and append to created_blocks list
        deer_block = PulseBlock(name=name)
        deer_block.append(pihalf_element)
        deer_block.append(tau_element)
        deer_block.append(rf_element)
        deer_block.append(pi_element)
        deer_block.append(tau_norf_element)
        deer_block.append(pihalf_element)

        deer_block.append(lasergate_element)
        deer_block.append(laser_element)
        deer_block.append(delay_element)
        deer_block.append(waiting_element)
        if alternating:
            deer_block.append(pihalf_element)
            deer_block.append(tau_norf_element)
            deer_block.append(pi_element)
            deer_block.append(tau_norf_element)
            deer_block.append(pihalf_element)

            deer_block.append(lasergate_element)
            deer_block.append(laser_element)
            deer_block.append(delay_element)
            deer_block.append(waiting_element)
        created_blocks.append(deer_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((deer_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences 
        
    # def generate_rotaverage(self, name='rot_ave', tau_start=0.0e-6, tau_step=1.0e-6,
                          # num_of_points=50, alternating=False):
        # """

        # """
        # created_blocks = list()
        # created_ensembles = list()
        # created_sequences = list()

        # # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        # laser_length_gate = 3e-6 #laser gates are 3us
        # print('appending laser length')
        # laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # # get tau array for measurement ticks
        # tau_array = tau_start + np.arange(num_of_points) * tau_step

        # # create the elements
        # waiting_element = self._get_idle_element(length=self.wait_time,
                                                 # increment=0)
        # ramstime_element = self._get_idle_element(length=self.rams_time,
                                                 # increment=0)
        # lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        # laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        # delay_element = self._get_delay_gate_element()
        # pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              # increment=0,
                                              # amp=self.microwave_amplitude,
                                              # freq=self.microwave_frequency,
                                              # phase=0)
        # pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          # increment=0,
                                          # amp=self.microwave_amplitude,
                                          # freq=self.microwave_frequency,
                                          # phase=0)
        # # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        # if self.microwave_channel.startswith('a'):
            # pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   # increment=0,
                                                   # amp=self.microwave_amplitude,
                                                   # freq=self.microwave_frequency,
                                                   # phase=180)
        # else:
            # pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   # increment=0,
                                                   # amp=self.microwave_amplitude,
                                                   # freq=self.microwave_frequency,
                                                   # phase=0)
        # tau_element = self._get_idle_element(length=tau_start, increment=tau_step)

        # # Create block and append to created_blocks list
        # rot_ave_block = PulseBlock(name=name)
        
        # rot_ave_block.append(pihalf_element)#1
        # rot_ave_block.append(tau_element)
        # rot_ave_block.append(pihalf_element)#1
        
        # rot_ave_block.append(tau_element)
        
        # rot_ave_block.append(pihalf_element)#2
        # rot_ave_block.append(tau_element)
        # rot_ave_block.append(pihalf_element)#2
        
        # # rot_ave_block.append(waiting_element)
        
        # # rot_ave_block.append(pihalf_element)#3
        # # rot_ave_block.append(tau_element)
        # # rot_ave_block.append(pihalf_element)#3
        
        # # rot_ave_block.append(pihalf_element)#3
        # rot_ave_block.append(lasergate_element)
        # rot_ave_block.append(laser_element)
        # rot_ave_block.append(delay_element)
        # if alternating:
            # rot_ave_block.append(pihalf_element)#1
            # rot_ave_block.append(tau_element)
            # rot_ave_block.append(pihalf_element)#1
            
            # rot_ave_block.append(tau_element)
            
            # rot_ave_block.append(pihalf_element)#2
            # rot_ave_block.append(tau_element)
            # rot_ave_block.append(pi3half_element)#2
            
            # # rot_ave_block.append(waiting_element)
            
            # # rot_ave_block.append(pihalf_element)#3
            # # rot_ave_block.append(tau_element)
            # # rot_ave_block.append(pi3half_element)#3
            
            # rot_ave_block.append(lasergate_element)
            # rot_ave_block.append(laser_element)
            # rot_ave_block.append(delay_element)
        
        # created_blocks.append(rot_ave_block)

        # # Create block ensemble
        # block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        # block_ensemble.append((rot_ave_block.name, num_of_points - 1))

        # # Create and append sync trigger block if needed
        # if self.sync_channel:
            # sync_block = PulseBlock(name='sync_trigger')
            # sync_block.append(self._get_sync_element())
            # created_blocks.append(sync_block)
            # block_ensemble.append((sync_block.name, 0))

        # # add metadata to invoke settings later on
        # number_of_lasers = 2 * num_of_points if alternating else num_of_points
        # block_ensemble.measurement_information['alternating'] = alternating
        # block_ensemble.measurement_information['laser_ignore_list'] = list()
        # block_ensemble.measurement_information['controlled_variable'] = tau_array
        # block_ensemble.measurement_information['units'] = ('s', '')
        # block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        # block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        # block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            # ensemble=block_ensemble, created_blocks=created_blocks)

        # # append ensemble to created ensembles
        # created_ensembles.append(block_ensemble)
        # return created_blocks, created_ensembles, created_sequences

    def generate_mwnuclear(self, name='mwnuclear', t_rf_start=1.0e-9, t_rf_step=100.0e-9, num_of_points=1, rf_freq = 4.8e6, rf_phase = 0, rf_freq_fixed = 5.096e6, fixed_pulse_time = 60e-6, seq="x,rf,x", alternating=False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        seqlist = seq.split(",")
        rf_volt = dBmtoV(self.rf_power)
        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        t_rf_array = t_rf_start + np.arange(num_of_points) * t_rf_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        
        mw_element = self._get_mwp_element(length=self.rabi_period / 2,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase="x")
                                              
        rfpi_element = self._get_rf_element(length=fixed_pulse_time,
                                          increment=0,
                                          amp=rf_volt,
                                          freq=rf_freq_fixed,
                                          phase=0)
        if self.rf_channel.startswith('a'):
            rf_element = self._get_rf_element(length=t_rf_start,
                                              increment=t_rf_step,
                                              amp=rf_volt,
                                              freq=rf_freq,
                                              phase=rf_phase)
        else:
            rf_element = self._get_mwp_element(length=t_rf_start,
                                              increment=t_rf_step,
                                              amp=None,
                                              freq=None,
                                              phase='rf')                                             
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)        
        seqdic = {"x": mw_element,"rf": rf_element,"rfpi": rfpi_element}

        # Create block and append to created_blocks list
        mwnuclear_block = PulseBlock(name=name)
        for element in seqlist:
            mwnuclear_block.append(seqdic[element])

        mwnuclear_block.append(waiting_element)
        mwnuclear_block.append(lasergate_element)
        mwnuclear_block.append(laser_element)
        mwnuclear_block.append(delay_element)
        mwnuclear_block.append(waiting_element)
        if alternating:
            mwnuclear_block.append(pihalf_element)
            # mwnuclear_block.append(tau_element)
            # mwnuclear_block.append(pi_element)
            # mwnuclear_block.append(tau_element)
            # mwnuclear_block.append(pihalf_element)

            # mwnuclear_block.append(lasergate_element)
            # mwnuclear_block.append(laser_element)
            # mwnuclear_block.append(delay_element)
            # mwnuclear_block.append(waiting_element)
        created_blocks.append(mwnuclear_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((mwnuclear_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = t_rf_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences 
        
    def generate_mwnucleardf(self, name='mwnucleardf', center_freq = 5.095e6, range_freq = 20e3, d_freq = 1e3, rf_freq_fixed = 5.095e6, fixed_pulse_time = 10e-6, sequence_list = '0,rf,0'):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        alternating = False
        rf_phase = 0
        t_rf = self.rf_rabi_period/2.
        rf_volt = dBmtoV(self.rf_power)

        mwpulses1, mwpulses2 = sequence_list.split(",rf,")
        mwpulses1 = mwpulses1.split(',')
        mwpulses2 = mwpulses2.split(',')
        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        num_of_points = int(2*range_freq/d_freq)
        rf_array = center_freq - range_freq + np.arange(num_of_points) * d_freq
        

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        awgtrig_element = self._get_awgtrig_element()
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        mwpi_element = self._get_mwp_element(length=self.rabi_period / 2,
                                      increment=0,
                                      amp=self.microwave_amplitude,
                                      freq=self.microwave_frequency,
                                      phase="x")
        rfpi_element = self._get_rf_element(length=fixed_pulse_time,
                                          increment=0,
                                          amp=rf_volt,
                                          freq=rf_freq_fixed,
                                          phase=0)
        mw_dummy_element =self._get_idle_element(length=self.rabi_period / 2, increment=0)
        rf_dummy_element =self._get_idle_element(length=self.rabi_period / 2, increment=0)
        pulsedic = {'x':mwpi_element, 'o': mw_dummy_element,'0': rf_dummy_element, 'rfpi':rfpi_element}

        # Create block and append to created_blocks list
        mwnuclear_block = PulseBlock(name=name)
        mwnuclear_block.append(awgtrig_element)
        for freq in rf_array:
            rf_element = self._get_rf_element(length=t_rf,
                                              increment=0,
                                              amp=rf_volt,
                                              freq=freq,
                                              phase=rf_phase)

            
            for ph in mwpulses1:
                mwnuclear_block.append(pulsedic[ph])
            mwnuclear_block.append(rf_element)
            for ph in mwpulses2:
                mwnuclear_block.append(pulsedic[ph])
            mwnuclear_block.append(waiting_element)
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)

        created_blocks.append(mwnuclear_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((mwnuclear_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = ('Hz', '')
        block_ensemble.measurement_information['labels'] = ('freq', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences 
    
    def generate_test_analogmw(self, name = 'test_analogmw', abs_phase = 0, rel_phase = 90, t_start = 1e-9, t_step = 50e-9, num_of_points = 50, rf_freq = 80e6):
        """
        
        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        # alternating = False
        t_rf = self.rf_rabi_period/2.
        rf_volt = dBmtoV(self.rf_power)
        iq_freq = self.IQ_freq
        # laser_length_gate = 3e-6
        print('appending laser length')
        # laser_length_laser = self.laser_length - 3e-6+100e-9
        
        waiting_element = self._get_idle_element(length=1e-9+0*self.wait_time,
                                                 increment=0)
        # lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        awgtrig_element = self._get_awgtrig_element()
        # laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        # delay_element = self._get_delay_gate_element()
        
        # tau_array = t_start + np.arange(num_of_points)*t_step
        
        # tau_element = self._get_idle_element(length=t_start, increment=t_step)
        
        # rfpi_element = self._get_rf_element(length=t_rf,
                                  # increment=0,
                                  # amp=rf_volt,
                                  # freq=rf_freq,
                                  # phase=0)
        
        mwpi_element = self._get_mw_element(length=self.rabi_period / 2.,
                                      increment=0,
                                      amp=self.microwave_amplitude,
                                      freq=iq_freq,
                                      phase=abs_phase,
                                      iq_phase=rel_phase)
        
        test_analogmw_block = PulseBlock(name=name)
        test_analogmw_block.append(awgtrig_element)        
        test_analogmw_block.append(mwpi_element)
        # test_analogmw_block.append(waiting_element)
        # test_analogmw_block.append(tau_element)
        # test_analogmw_block.append(rfpi_element)
        # test_analogmw_block.append(tau_element)
        # test_analogmw_block.append(mwpi_element)
        # test_analogmw_block.append(waiting_element)
        # test_analogmw_block.append(lasergate_element)
        # test_analogmw_block.append(laser_element)
        # test_analogmw_block.append(delay_element)
        # test_analogmw_block.append(waiting_element)
        created_blocks.append(test_analogmw_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((test_analogmw_block.name, 0))

        # Create and append sync trigger block if needed
        # if self.sync_channel:
            # sync_block = PulseBlock(name='sync_trigger')
            # sync_block.append(self._get_sync_element())
            # created_blocks.append(sync_block)
            # block_ensemble.append((sync_block.name, 0))
            
        # if self.awgtrig_channel:
            # awgtrig_block = PulseBlock(name='awgtrig_trigger')
            # awgtrig_block.append(self._get_awgtrig_element())
            # created_blocks.append(awgtrig_block)
            # block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # # add metadata to invoke settings later on
        # number_of_lasers = 2 * num_of_points if alternating else num_of_points
        # block_ensemble.measurement_information['alternating'] = alternating
        # block_ensemble.measurement_information['laser_ignore_list'] = list()
        # block_ensemble.measurement_information['controlled_variable'] = tau_array
        # block_ensemble.measurement_information['units'] = ('s', '')
        # block_ensemble.measurement_information['labels'] = ('tau', 'Signal')
        # block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        # block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            # ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
    
    def generate_deerdf(self, name='deerdf', center_freq = 100e6, range_freq = 5e6, d_freq = 500e3, t_rf_start = 1e-9, t_rf_step = 50e-9, num_of_points = 50, phase_step = 15.0, fixed_freq=100e6, fixed_time = 50e-6, buff_time = 1e-6, type = rfvariables.time, alternating=True):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        rf_phase = 0
        t_rf = self.rf_rabi_period/2.
        rf_volt = dBmtoV(self.rf_power)
        
        vartype = type.value

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        if vartype == 'time':
            
            rf_array = t_rf_start + np.arange(num_of_points) * t_rf_step
            unit = 's'
            sname = 'tau'
            
        if vartype == 'freq':
            
            num_of_points = int(2*range_freq/d_freq)
            rf_array = center_freq - range_freq + np.arange(num_of_points) * d_freq
            unit = 'Hz'
            sname = 'freq'

        if vartype == 'phase':
            
            rf_array = np.arange(num_of_points)*phase_step
            unit = 'degs'
            sname = 'phase'                  

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        awgtrig_element = self._get_awgtrig_element()
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
        
        mwpi_element = self._get_mwp_element(length=self.rabi_period / 2,
                                      increment=0,
                                      amp=self.microwave_amplitude,
                                      freq=self.microwave_frequency,
                                      phase="x")
                                      
        mwpi2_element = self._get_mwp_element(length=self.rabi_period / 4,
                                      increment=0,
                                      amp=self.microwave_amplitude,
                                      freq=self.microwave_frequency,
                                      phase="x")
        
        tau2_element =self._get_idle_element(length= fixed_time, increment = 0)
        
        buffer_element = self._get_idle_element(length=buff_time, increment=0)
                              

        # Create block and append to created_blocks list
        mwnuclear_block = PulseBlock(name=name)
        mwnuclear_block.append(awgtrig_element)
        
        for var in rf_array:
            rf_element = self._get_rf_element(length=var if vartype == 'time' else t_rf,
                                              increment=0,
                                              amp=rf_volt,
                                              freq= var if vartype == 'freq' else fixed_freq,
                                              phase= var if vartype =='phase' else rf_phase)
                                              
            rf_off_element = self._get_rf_element(length=var if vartype == 'time' else t_rf,
                                              increment=0,
                                              amp=rf_volt,
                                              freq= 10e6,
                                              phase=rf_phase)
                                              
            tau1_element = self._get_idle_element(length = fixed_time-buff_time-var if vartype == 'time' else fixed_time-buff_time-t_rf, increment = 0)
            
            mwnuclear_block.append(mwpi2_element)
            mwnuclear_block.append(tau1_element)
            mwnuclear_block.append(rf_element)
            mwnuclear_block.append(buffer_element)
            mwnuclear_block.append(mwpi_element)
            mwnuclear_block.append(tau2_element)
            mwnuclear_block.append(mwpi2_element)
            mwnuclear_block.append(waiting_element)
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)
            if alternating == True:
                mwnuclear_block.append(mwpi2_element)
                mwnuclear_block.append(tau2_element)
                mwnuclear_block.append(mwpi_element)
                mwnuclear_block.append(tau2_element)
                mwnuclear_block.append(mwpi2_element)
                mwnuclear_block.append(waiting_element)
                mwnuclear_block.append(lasergate_element)
                mwnuclear_block.append(laser_element)
                mwnuclear_block.append(delay_element)
                mwnuclear_block.append(waiting_element)
        created_blocks.append(mwnuclear_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((mwnuclear_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences     

    def generate_nuclearrfmw(self, name ='nuclearrfmw',rf1_freq = 5.095e6, rf2_freq = 4.7899e6, rf2_time = 67e-6, tau_start = 1e-9, tau_step = 100e-9, num_of_points = 1, fixed_time = 250e-6, sequence = pulsesequences.mwrabi, alternating = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        mw_period = self.rabi_period
        
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()
                                              
        rf1_pi_element = self._get_rf_element(length=rf_period/2,
                                          increment=0,
                                          amp=rf_volt,
                                          freq=rf1_freq,
                                          phase=0)
                                          
        rf1_pi2_element = self._get_rf_element(length=rf_period/4,
                                          increment=0,
                                          amp=rf_volt,
                                          freq=rf1_freq,
                                          phase=0)        
                                          
        rf2_element = self._get_rf_element(length=rf2_time,
                                          increment=0,
                                          amp=rf_volt,
                                          freq=rf2_freq,
                                          phase=0)
                                          
        rf1_pi32_element = self._get_rf_element(length=rf_period/4.,
                                  increment=0,
                                  amp=rf_volt,
                                  freq=rf1_freq,
                                  phase=180)
                                          
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        mw_element = self._get_mwp_element(length=tau_start,
                                          increment=tau_step,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase='x')
                                          
        mw_pi_element = self._get_mwp_element(length=mw_period/2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase='x')    

        mw_sweep_element = self._get_mwp_element(length=tau_start,
                                          increment=tau_step,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase='x') 
                                          
        dummy_element =self._get_idle_element(length= tau_start, increment = tau_step)
        fixed_dummy_element =self._get_idle_element(length= fixed_time, increment = 0)
        
        #seqdic = {"x": mw_element,"rf1": rf1_element,"rf2": rf2_element}
        seqtype = sequence.value

        # Create block and append to created_blocks list
        mwnuclear_block = PulseBlock(name=name)
        #for element in seqlist:
            #mwnuclear_block.append(seqdic[element])
        
        
        if seqtype == 'mwrabi':
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(rf2_element)
            mwnuclear_block.append(mw_element)
            mwnuclear_block.append(rf2_element)
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(waiting_element)
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)
            created_blocks.append(mwnuclear_block)
            alternating = False            
        
        if seqtype == 'ramsey':
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(rf2_element)
            mwnuclear_block.append(rf1_pi2_element)
            mwnuclear_block.append(dummy_element)
            mwnuclear_block.append(rf1_pi2_element)            
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)
            if alternating == True:
                mwnuclear_block.append(rf1_pi_element)
                mwnuclear_block.append(rf2_element)
                mwnuclear_block.append(rf1_pi2_element)
                mwnuclear_block.append(dummy_element)
                mwnuclear_block.append(rf1_pi32_element)            
                mwnuclear_block.append(lasergate_element)
                mwnuclear_block.append(laser_element)
                mwnuclear_block.append(delay_element)
                mwnuclear_block.append(waiting_element)
            created_blocks.append(mwnuclear_block)

        if seqtype == 'ramseymw':
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(rf2_element)
            mwnuclear_block.append(mw_pi_element)
            mwnuclear_block.append(rf1_pi2_element)
            mwnuclear_block.append(dummy_element)
            mwnuclear_block.append(rf1_pi2_element)            
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)
            if alternating == True:
                mwnuclear_block.append(rf1_pi_element)
                mwnuclear_block.append(rf2_element)
                mwnuclear_block.append(mw_pi_element)
                mwnuclear_block.append(rf1_pi2_element)
                mwnuclear_block.append(dummy_element)
                mwnuclear_block.append(rf1_pi32_element)            
                mwnuclear_block.append(lasergate_element)
                mwnuclear_block.append(laser_element)
                mwnuclear_block.append(delay_element)
                mwnuclear_block.append(waiting_element)
            created_blocks.append(mwnuclear_block)
            
        if seqtype == 'ramsey_sweep':
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(rf2_element)
            mwnuclear_block.append(mw_sweep_element)
            mwnuclear_block.append(rf1_pi2_element)
            mwnuclear_block.append(fixed_dummy_element)
            mwnuclear_block.append(rf1_pi2_element)            
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)
            if alternating == True:
                mwnuclear_block.append(rf1_pi_element)
                mwnuclear_block.append(rf2_element)
                mwnuclear_block.append(mw_sweep_element)
                mwnuclear_block.append(rf1_pi2_element)
                mwnuclear_block.append(fixed_dummy_element)
                mwnuclear_block.append(rf1_pi32_element)            
                mwnuclear_block.append(lasergate_element)
                mwnuclear_block.append(laser_element)
                mwnuclear_block.append(delay_element)
                mwnuclear_block.append(waiting_element)
            created_blocks.append(mwnuclear_block)
            
        if seqtype == 'spin_echo':
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(rf2_element)
            mwnuclear_block.append(mw_pi_element)
            mwnuclear_block.append(rf1_pi2_element)
            mwnuclear_block.append(dummy_element)
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(dummy_element)
            mwnuclear_block.append(rf1_pi2_element)
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)
            if alternating == True:
                mwnuclear_block.append(rf1_pi_element)
                mwnuclear_block.append(rf2_element)
                mwnuclear_block.append(mw_pi_element)
                mwnuclear_block.append(rf1_pi2_element)
                mwnuclear_block.append(dummy_element)
                mwnuclear_block.append(rf1_pi_element)
                mwnuclear_block.append(dummy_element)
                mwnuclear_block.append(rf1_pi32_element)            
                mwnuclear_block.append(lasergate_element)
                mwnuclear_block.append(laser_element)
                mwnuclear_block.append(delay_element)
                mwnuclear_block.append(waiting_element)
            created_blocks.append(mwnuclear_block)  
            
        if seqtype == 'spin_echo_sweep':
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(rf2_element)
            mwnuclear_block.append(mw_sweep_element)
            mwnuclear_block.append(rf1_pi2_element)
            mwnuclear_block.append(fixed_dummy_element)
            mwnuclear_block.append(rf1_pi_element)
            mwnuclear_block.append(fixed_dummy_element)
            mwnuclear_block.append(rf1_pi2_element)
            mwnuclear_block.append(lasergate_element)
            mwnuclear_block.append(laser_element)
            mwnuclear_block.append(delay_element)
            mwnuclear_block.append(waiting_element)
            if alternating == True:
                mwnuclear_block.append(rf1_pi_element)
                mwnuclear_block.append(rf2_element)
                mwnuclear_block.append(mw_sweep_element)
                mwnuclear_block.append(rf1_pi2_element)
                mwnuclear_block.append(fixed_dummy_element)
                mwnuclear_block.append(rf1_pi_element)
                mwnuclear_block.append(fixed_dummy_element)
                mwnuclear_block.append(rf1_pi32_element)            
                mwnuclear_block.append(lasergate_element)
                mwnuclear_block.append(laser_element)
                mwnuclear_block.append(delay_element)
                mwnuclear_block.append(waiting_element)
            created_blocks.append(mwnuclear_block)            


        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((mwnuclear_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    

        # add metadata to invoke settings later on 
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences 
        
    
    def generate_rfsuper(self, name='rfsuper', tau_start = 1e-9, tau_step = 10e-9, num_of_points = 20, rf_wait = 1e-9, fixed_freq = 100e6, range_freq = 10e6, d_freq = 500e3, alt_freq = 100e6, d_phase=10, mw_tau=50e-6, mw_phase=0, mwsequence = mwsequences.spinecho, rfsequence = rfsequences.rabi, type = rfvariables.time, alternating = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        t_rf = rf_period/2
        iq_freq = self.IQ_freq
        
        # get measurement array for measurement ticks
        mwseqtype = mwsequence.value
        rfseqtype = rfsequence.value
        vartype = type.value
        
        if vartype == 'time':
            rf_array = tau_start + np.arange(num_of_points) * tau_step
            unit = 's'
            sname = 'tau'
            
        if vartype == 'freq':
            
            num_of_points = int(2*range_freq/d_freq)
            rf_array = (fixed_freq - range_freq) + np.arange(num_of_points) * d_freq
            unit = 'Hz'
            sname = 'freq'    
            
        if vartype == 'phase':
            
            num_of_points = int(360./d_phase)
            rf_array = np.arange(num_of_points+1) * d_phase
            unit = '°'
            sname = 'phase'   

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        awgtrig_element = self._get_awgtrig_element()
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        
        mw_tau2_element = self._get_idle_element(length = mw_tau, increment = 0)
        
        rfsuper_block = PulseBlock(name=name)
        # creates phase synchronous IQ mw elements
        def mw_func(block_name=rfsuper_block, length='pi2', phase_add = mw_phase):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        # Create block and append to created_blocks list
        

        # rfsuper_block.append(awgtrig_element)
        for var in rf_array:
            if vartype == 'time':
                mw_tau1 = mw_tau-var-rf_wait
            else:
                mw_tau1 = mw_tau-t_rf-rf_wait
            
            mw_tau_alt = mw_tau - rf_period - rf_wait
            
            mw_tau1_element = self._get_idle_element(length = mw_tau1, increment = 0)

            mw_tau_alt_element = self._get_idle_element(length = mw_tau_alt, increment = 0)
            
            rf_wait_element = self._get_idle_element(length = rf_wait, increment = 0)
            
            rf_element = self._get_rf_element(length=var if vartype == 'time' else t_rf,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = var if vartype == 'freq' else fixed_freq,
                                                phase = var if vartype =='phase' else 0)
                                                
            rf_alt_element = self._get_rf_element(length=rf_period,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = alt_freq,
                                                phase = var if vartype =='phase' else 0)
                                                
            rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
            rfsuper_block.append(mw_tau2_element)
            rfsuper_block.append(mw_func(rfsuper_block,'pi',mw_phase))
            rfsuper_block.append(rf_wait_element)
            rfsuper_block.append(rf_element)
            rfsuper_block.append(mw_tau1_element)
            rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
            rfsuper_block.append(waiting_element)
            rfsuper_block.append(laser_element)
            rfsuper_block.append(delay_element)
            rfsuper_block.append(waiting_element)
            if alternating:               
                rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
                rfsuper_block.append(mw_tau2_element)
                rfsuper_block.append(mw_func(rfsuper_block,'pi',mw_phase))
                rfsuper_block.append(mw_tau2_element)
                #rfsuper_block.append(rf_wait_element)
                #rfsuper_block.append(rf_alt_element)
                #rfsuper_block.append(mw_tau_alt_element)
                rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
                rfsuper_block.append(waiting_element)
                rfsuper_block.append(laser_element)
                rfsuper_block.append(delay_element)
                rfsuper_block.append(waiting_element)


        created_blocks.append(rfsuper_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((rfsuper_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
        
        
    def generate_rf2super(self, name='rf2super', tau_start = 1e-9, tau_step = 10e-9, num_of_points = 20, rftime1 = 10e-9, rf_wait = 1e-9, fixed_freq = 100e6, mw_tau=50e-6, mw_phase=0, 
                            mwsequence =mwsequences.spinecho, rfsequence = rfsequences.rabi, type = rfvariables.time, alternating = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        t_rf = rf_period/2
        iq_freq = self.IQ_freq
        
        # get measurement array for measurement ticks
        mwseqtype = mwsequence.value
        rfseqtype = rfsequence.value
        vartype = type.value
        
        if vartype == 'time':
            rf_array = tau_start + np.arange(num_of_points) * tau_step
            unit = 's'
            sname = 'tau'

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        awgtrig_element = self._get_awgtrig_element()
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        
        mw_tau2_element = self._get_idle_element(length = mw_tau, increment = 0)
        
        rfsuper_block = PulseBlock(name=name)
        # creates phase synchronous IQ mw elements
        def mw_func(block_name=rfsuper_block, length='pi2', phase_add = mw_phase):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        # Create block and append to created_blocks list
        

        # rfsuper_block.append(awgtrig_element)
        for var in rf_array:
            mw_tau1 = mw_tau-var-rf_wait
                
            mw_tau1_element = self._get_idle_element(length = mw_tau1, increment = 0)
            
            rf_wait_element = self._get_idle_element(length = rf_wait, increment = 0)
            
            rf_element = self._get_rf_element(length=var,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = fixed_freq,
                                                phase = 0)
                                                
            rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
            rfsuper_block.append(rf_wait_element)
            rfsuper_block.append(rf_element)
            rfsuper_block.append(mw_tau1_element)
            rfsuper_block.append(mw_func(rfsuper_block,'pi',mw_phase))
            rfsuper_block.append(rf_wait_element)
            rfsuper_block.append(rf_element)
            rfsuper_block.append(mw_tau1_element)
            rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
            rfsuper_block.append(waiting_element)
            rfsuper_block.append(laser_element)
            rfsuper_block.append(delay_element)
            rfsuper_block.append(waiting_element)
            if alternating:               
                rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
                rfsuper_block.append(mw_tau2_element)
                rfsuper_block.append(mw_func(rfsuper_block,'pi',mw_phase))
                rfsuper_block.append(mw_tau2_element)
                rfsuper_block.append(mw_func(rfsuper_block,'pi2',mw_phase))
                rfsuper_block.append(waiting_element)
                rfsuper_block.append(laser_element)
                rfsuper_block.append(delay_element)
                rfsuper_block.append(waiting_element)


        created_blocks.append(rfsuper_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((rfsuper_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
    
    def generate_deerdelay(self, name='deerdelay', tau_start = 1e-9, tau_step = 10e-9, num_of_points = 20, fixed_freq = 100e6, mw_tau=50e-6, alternating = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        t_rf = rf_period/2
        iq_freq = self.IQ_freq
        
        rf_array = tau_start + np.arange(num_of_points) * tau_step
        unit = 's'
        sname = 'tau'   

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        awgtrig_element = self._get_awgtrig_element()
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        
        mw_tau1_element = self._get_idle_element(length = mw_tau, increment = 0)
        
        deerdelay_block = PulseBlock(name=name)
        # creates phase synchronous IQ mw elements
        def mw_func(block_name=deerdelay_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        # Create block and append to created_blocks list
        

        for var in rf_array:
            mw_tau2 = mw_tau-var-t_rf
            
            mw_tau2_element = self._get_idle_element(length = mw_tau2, increment = 0)
            
            tau_delay_element = self._get_idle_element(length = var, increment = 0)
            
            rf_element = self._get_rf_element(length=t_rf,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = fixed_freq,
                                                phase = 0)
                                                
            deerdelay_block.append(mw_func(deerdelay_block,'pi2',0))
            deerdelay_block.append(mw_tau1_element)
            deerdelay_block.append(mw_func(deerdelay_block,'pi',0))
            deerdelay_block.append(tau_delay_element)
            deerdelay_block.append(rf_element)
            deerdelay_block.append(mw_tau2_element)
            deerdelay_block.append(mw_func(deerdelay_block,'pi2',0))
            deerdelay_block.append(waiting_element)
            deerdelay_block.append(laser_element)
            deerdelay_block.append(delay_element)
            deerdelay_block.append(waiting_element)
            if alternating:               
                deerdelay_block.append(mw_func(deerdelay_block,'pi2',0))
                deerdelay_block.append(mw_tau1_element)
                deerdelay_block.append(mw_func(deerdelay_block,'pi',0))
                deerdelay_block.append(mw_tau1_element)
                deerdelay_block.append(mw_func(deerdelay_block,'pi2',0))
                deerdelay_block.append(waiting_element)
                deerdelay_block.append(laser_element)
                deerdelay_block.append(delay_element)
                deerdelay_block.append(waiting_element)


        created_blocks.append(deerdelay_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((deerdelay_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
        
    # def generate_rfDDsuper(self, name = 'rfDDsuper', tau_se=50e-6, tau_start=1e-9, tau_step=100e-9, num_of_points=10, rf_freq = 100e6, range_freq = 10e6, d_freq = 500e3, 
                            # det_freq=0, DDphases='x,y,x,y,x,y,x,y,x', rfseq = rfsequences.rabi, type = rfvariables.time, alternating=False):
        # """
        
        # """
        # # fold sequence: separate rf and mw sequences run simultaneously
        # fold_sequence = True
        # fold_channel = 'a_ch2' # the rf channel
        
        # created_blocks=list()
        # created_ensembles=list()
        # created_sequences=list()
        
        # rf_volt = dBmtoV(self.rf_power)
        # rf_period = self.rf_rabi_period
        # mw_period = self.rabi_period
        # iq_freq = self.IQ_freq

        # rfseqrun = rfseq.value
        # vartype = type.value
        
        # phaselist = DDphases.split(",")
        
        # if phaselist[0] == '0':
            # lendd = len(phaselist)
            # timedd = np.zeros(lendd)
            # total_dd_time = mw_period/2
        # else:
            # lendd = len(phaselist)-1
            # timedd = np.append(np.insert(np.ones(int((lendd/2)-1)),0,1/2),1/2)
            # timedd = np.append(timedd,timedd)
            # timedd = 2*timedd[1:]
            # total_dd_time = round(sum(timedd[:-1])*tau_se + (lendd+1)*mw_period/2,9)
        
        # print('total dd time = '+str(total_dd_time))
            
        # # get array for measurement ticks (just time for now, can add in frequency
        # if vartype == 'time':
            # rf_array = tau_start + np.arange(num_of_points) * tau_step
            # unit = 's'
            # sname = 'tau'        
            
        # if vartype == 'freq':
            # num_of_points = int(2*range_freq/d_freq)
            # rf_array = (rf_freq - range_freq) + np.arange(num_of_points) * d_freq
            # unit = 'Hz'
            # sname = 'freq'
            # if rfseqrun != 'rabi':
                # self.log.error('Have not implemented this sequence')            
        
        # if vartype == 'phase':
            # d_phase = int(360./num_of_points)
            # rf_array = np.arange(num_of_points+1) * d_phase
            # unit = '°'
            # sname = 'phase'
            # num_of_points=num_of_points+1
            # if rfseqrun == 'rabi':
                # self.log.error('Have not implemented rabi sequence for other variables.')
                
        # if vartype == 'NVphase':
            # d_phase = int(360./num_of_points)
            # rf_array = np.arange(num_of_points+1) * d_phase
            # unit = '°'
            # sname = 'phase'
            # num_of_points=num_of_points+1
            # if rfseqrun == 'ramsey':
                # self.log.error('Have not implemented ramsey sequence for this variable.')
            # if rfseqrun == 'spin_echo':
                # self.log.error('Have not implemented spin_echo sequence for other variable.')
      
        # # create both blocks
        # rfDDsuper_block = PulseBlock(name=name)
        # RF_block = PulseBlock(name='RF')
        
        # # IQ phase correction
        # def mw_func(block_name=rfDDsuper_block, length='pi2', phase_add = 0):
            # pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            # acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            # mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    # increment = 0, 
                                                    # amp = self.microwave_amplitude, 
                                                    # freq = iq_freq, 
                                                    # phase = acc_phase + phase_add)
            # return mw_phase_element
            
        # def rf_func(block_name=RF_block, length='pi2', phase_add = 0):
            # pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            # acc_phase = np.mod((block_name.init_length_s)*(rf_freq+det_freq)*360,360)
            
            # rf_phase_element = self._get_rf_element(length=pulse_dic[length]*rf_period, 
                                                    # increment = 0, 
                                                    # amp = rf_volt, 
                                                    # freq = rf_freq, 
                                                    # phase = acc_phase + phase_add)
            # return rf_phase_element
            
        # # create elements
        # waiting_element = self._get_idle_element(length = self.wait_time, increment=0)
        # laser_element=self._get_laser_gate_element(length=self.laser_length, increment=0)
        # delay_element=self._get_delay_gate_element()
        # awgtrig_element = self._get_awgtrig_element()
        
        # phasedic = {'x':0, 'y':90}                                                              
        
        # tau_se_element = self._get_idle_element(length = tau_se, increment = 0)
            
        # for var in rf_array:
            # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
            # rfDDsuper_block.append(tau_se_element)
            
            # RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
            # RF_block.append(tau_se_element)
            
            # ddcounter=0
            # for ph in phaselist:
                # if ph == '0':
                    # rfDDsuper_block.append(self._get_idle_element(length = 0, increment = 0))
                # else:
                    # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi', phasedic[ph]))
                # rfDDsuper_block.append(self._get_idle_element(length = tau_se*timedd[ddcounter], increment = 0))
                # ddcounter += 1
            
            # rfDDsuper_block.pop()
            
            # if rfseqrun == 'rabi':
                # if vartype == 'time':
                    # rf_rabi_element = self._get_rf_element(length = var,
                                                            # increment = 0,
                                                            # amp = rf_volt,
                                                            # freq = rf_freq,
                                                            # phase = 0)
                    # t_buff = total_dd_time - var
                
                # if vartype =='freq':
                    # rf_rabi_element = self._get_rf_element(length = rf_period/2,
                                                            # increment = 0,
                                                            # amp = rf_volt,
                                                            # freq = var,
                                                            # phase = 0)
                    # t_buff = total_dd_time - rf_period/2
                    
                # if vartype =='NVphase':
                    # rf_rabi_element = self._get_rf_element(length = tau_start,
                                                            # increment = 0,
                                                            # amp = rf_volt,
                                                            # freq = rf_freq,
                                                            # phase = 0)
                    # t_buff = total_dd_time - tau_start
                
                # buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                # RF_block.append(buffer_element)
                # RF_block.append(rf_rabi_element)
                # RF_block.append(buffer_element)
            
            # if rfseqrun == 'ramsey':
                # if vartype == 'time':
                    # t_buff = total_dd_time - var - rf_period/2
                # else:
                    # t_buff = total_dd_time - tau_start - rf_period/2
                # # if vartype == 'phase':
                        # # rf_phase_element = self._get_rf_element(length=rf_period/4,
                                                # # increment = 0,
                                                # # amp = rf_volt,
                                                # # freq = rf_freq,
                                                # # phase = var)
                # buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                # tau_rf_element = self._get_idle_element(length = var if vartype=='time' else tau_start, increment = 0)
                # RF_block.append(buffer_element)
                # RF_block.append(rf_func(RF_block,'pi2',0))
                # RF_block.append(tau_rf_element)
                # if vartype == 'phase':
                    # RF_block.append(rf_func(RF_block,'pi2',var))
                # else:
                    # RF_block.append(rf_func(RF_block,'pi2',0))
                # RF_block.append(buffer_element)
            
            # if rfseqrun == 'spin_echo':
                # if vartype=='time':
                    # t_buff = total_dd_time - 2*var - rf_period
                # else:
                    # t_buff = total_dd_time-2*tau_start - rf_period
                
                # # if vartype == 'phase':
                        # # rf_phase_element = self._get_rf_element(length=rf_period/4,
                                                # # increment = 0,
                                                # # amp = rf_volt,
                                                # # freq = rf_freq,
                                                # # phase = var)
                                                
                # buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                # tau_rf_element = self._get_idle_element(length = var if vartype == 'time' else tau_start, increment = 0)
                # RF_block.append(buffer_element)
                # RF_block.append(rf_func(RF_block,'pi2',0))
                # RF_block.append(tau_rf_element)
                # RF_block.append(rf_func(RF_block,'pi',0))
                # RF_block.append(tau_rf_element)
                # if vartype == 'phase':
                    # RF_block.append(rf_func(RF_block,'pi2',var))
                # else:
                    # RF_block.append(rf_func(RF_block,'pi2',0))
                # RF_block.append(buffer_element)
                
            # rfDDsuper_block.append(tau_se_element)
            # if vartype == 'NVphase':
                # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', var))
            # else:
                # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
            
            # RF_block.append(tau_se_element)
            # RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0))
            
            # rfDDsuper_block.append(waiting_element)
            # rfDDsuper_block.append(laser_element)
            # rfDDsuper_block.append(delay_element)
            # rfDDsuper_block.append(waiting_element)
            
            # RF_block.append(waiting_element)
            # RF_block.append(laser_element)
            # RF_block.append(delay_element)
            # RF_block.append(waiting_element)             
            
            # if alternating:
                # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
                # rfDDsuper_block.append(tau_se_element)
                
                # RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
                # RF_block.append(tau_se_element)
                
                # ddcounter = 0
                # for ph in phaselist:
                    # if ph == '0':
                        # rfDDsuper_block.append(self._get_idle_element(length = 0, increment = 0))
                    # else:
                        # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi', phasedic[ph]))
                    # rfDDsuper_block.append(self._get_idle_element(length = tau_se*timedd[ddcounter], increment = 0))
                    # ddcounter += 1
                # rfDDsuper_block.pop()
                
                # if rfseqrun == 'rabi':
                    # buffer_element = self._get_idle_element(length = total_dd_time, increment = 0)
                    # RF_block.append(buffer_element)                
                
                # if rfseqrun == 'ramsey':
                    # if vartype == 'time':
                        # t_buff = total_dd_time - var - rf_period/2
                    # else:
                        # t_buff = total_dd_time - tau_start - rf_period/2
                        
                    # # if vartype == 'phase':
                        # # rf_phase_alt_element = self._get_rf_element(length=rf_period/4,
                                                # # increment = 0,
                                                # # amp = rf_volt,
                                                # # freq = rf_freq,
                                                # # phase = var-180)
                    # buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                    # tau_rf_element = self._get_idle_element(length = var if vartype=='time' else tau_start, increment = 0)
                    # RF_block.append(buffer_element)
                    # RF_block.append(rf_func(RF_block,'pi2',0))
                    # RF_block.append(tau_rf_element)
                    # if vartype == 'phase':
                        # RF_block.append(rf_func(RF_block,'pi2',var-180))
                    # else:
                        # RF_block.append(rf_func(RF_block,'pi2',-180))
                    # RF_block.append(buffer_element)
                
                # if rfseqrun == 'spin_echo':
                    # if vartype == 'time':
                        # t_buff = total_dd_time - 2*var - rf_period
                    # else:
                        # t_buff = total_dd_time - 2*tau_start - rf_period
                        
                    # # if vartype == 'phase':
                        # # rf_phase_alt_element = self._get_rf_element(length=rf_period/4,
                                                # # increment = 0,
                                                # # amp = rf_volt,
                                                # # freq = rf_freq,
                                                # # phase = var-180)
                    
                    # buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                    # tau_rf_element = self._get_idle_element(length = var if vartype == 'time' else tau_start, increment = 0)
                    # RF_block.append(buffer_element)
                    # RF_block.append(rf_func(RF_block,'pi2',0))
                    # RF_block.append(tau_rf_element)
                    # RF_block.append(rf_func(RF_block,'pi',0))
                    # RF_block.append(tau_rf_element)
                    # if vartype == 'phase':
                        # RF_block.append(rf_func(RF_block,'pi2',var-180))
                    # else:
                        # RF_block.append(rf_func(RF_block,'pi2',-180))
                    # RF_block.append(buffer_element)
                    
                # rfDDsuper_block.append(tau_se_element)
                # if rfseqrun == 'rabi' and vartype == 'NVphase':
                    # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', var-180))
                # elif rfseqrun == 'rabi' and num_of_points == 1:
                    # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi32', -180))    
                # else:
                    # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
                # RF_block.append(tau_se_element)
                # RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0))

                # rfDDsuper_block.append(waiting_element)
                # rfDDsuper_block.append(laser_element)
                # rfDDsuper_block.append(delay_element)
                # rfDDsuper_block.append(waiting_element)

                
                # RF_block.append(waiting_element)
                # RF_block.append(laser_element)
                # RF_block.append(delay_element)
                # RF_block.append(waiting_element)             
            
        # created_blocks.append(rfDDsuper_block)
        # created_blocks.append(RF_block)
        
        # # Create block ensemble
        # block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        # block_ensemble.append((rfDDsuper_block.name, 0))
        # block_ensemble.append((RF_block.name, 0))

        # # Create and append sync trigger block if needed
        # if self.sync_channel:
            # sync_block = PulseBlock(name='sync_trigger')
            # sync_block.append(self._get_sync_element())
            # created_blocks.append(sync_block)
            # block_ensemble.append((sync_block.name, 0))
            
        # if self.awgtrig_channel:
            # awgtrig_block = PulseBlock(name='awgtrig_trigger')
            # awgtrig_block.append(self._get_awgtrig_element())
            # created_blocks.append(awgtrig_block)
            # block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # # add metadata to invoke settings later on
        # number_of_lasers = 2 * num_of_points if alternating else num_of_points
        # block_ensemble.measurement_information['alternating'] = alternating
        # block_ensemble.measurement_information['fold_sequence'] = fold_sequence
        # block_ensemble.measurement_information['fold_channel'] = fold_channel
        # block_ensemble.measurement_information['laser_ignore_list'] = list()
        # block_ensemble.measurement_information['controlled_variable'] = rf_array
        # block_ensemble.measurement_information['units'] = (unit, '')
        # block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        # block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        # block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            # ensemble=block_ensemble, created_blocks=created_blocks)
 
        # # append ensemble to created ensembles
        # created_ensembles.append(block_ensemble)
        # return created_blocks, created_ensembles, created_sequences
    
    def generate_rfDDsuper(self, name = 'rfDDsuper', tau_se=50e-6, tau_dd=50e-6, tau_start=1e-9, tau_step=100e-9, num_of_points=10, rf_freq = 100e6, range_freq = 10e6, d_freq =                       500e3, det_freq=0, absphase = 0, aphase = 0, pulse_time = 1e-9, DDphases='0,x,0', rfseq = rfsequences.rabi, type = rfvariables.time, alternating=False):
        """
        
        """
        # fold sequence: separate rf and mw sequences run simultaneously
        fold_sequence = True
        fold_channel = 'a_ch2' # the rf channel
        
        created_blocks=list()
        created_ensembles=list()
        created_sequences=list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        mw_period = self.rabi_period
        iq_freq = self.IQ_freq

        rfseqrun = rfseq.value
        vartype = type.value
        
        # Set up Dynamical Decoupling pulses
        phaselist = DDphases.split(",") # create list of dynamical decoupling pulse phases
        lendd = len(phaselist)-1 
        tmax = tau_start + num_of_points*tau_step*2 + rf_period # max time of P1 sequence
        ddpulses = {'0':0,'x':mw_period/2,'y':mw_period/2}
        timedd = np.append(np.insert(np.ones(int((lendd/2)-1)),0,1/2),1/2)
        timedd = 2*np.append(timedd,timedd) # total dynamical decoupling time
        # timedd = timedd[1:-1]
        
        def nonzero(x):
            return x != '0'
        
        # total dynamical decoupling time accounting for "0" pulses.
        phaselist_nonzero = sum(map(nonzero,phaselist)) 
        if phaselist_nonzero == len(phaselist):
            tdd = round((phaselist_nonzero*mw_period/2) + (lendd * tau_dd*2),9)
        else:
            tdd = round((phaselist_nonzero*mw_period/2) + ((phaselist_nonzero) * tau_dd*2),9)
        
        print(tdd)
        
        # ensures correct timing
        if vartype == 'time':
            if tmax > tdd:
                self.log.warning('the total range spanned by the rf sequence exceeds t_off. Increase t_off ')
            
        # get array for measurement ticks (just time for now, can add in frequency
        if vartype == 'time':
            rf_array = tau_start + np.arange(num_of_points) * tau_step
            unit = 's'
            sname = 'tau'        
            
        if vartype == 'freq':
            num_of_points = int(2*range_freq/d_freq)
            rf_array = (rf_freq - range_freq) + np.arange(num_of_points) * d_freq
            unit = 'Hz'
            sname = 'freq'
            if rfseqrun != 'rabi':
                self.log.error('Have not implemented this sequence')            
        
        if vartype == 'phase':
            d_phase = int(360./num_of_points)
            rf_array = np.arange(num_of_points+1) * d_phase
            unit = '°'
            sname = 'phase'
            num_of_points=num_of_points+1
            if rfseqrun == 'rabi':
                self.log.error('Have not implemented rabi sequence for other variables.')
                
        if vartype == 'NVphase':
            d_phase = int(360./num_of_points)
            rf_array = np.arange(num_of_points+1) * d_phase
            unit = '°'
            sname = 'phase'
            num_of_points=num_of_points+1
            if rfseqrun == 'ramsey':
                self.log.error('Have not implemented ramsey sequence for this variable.')
            if rfseqrun == 'spin_echo':
                self.log.error('Have not implemented spin_echo sequence for other variable.')
      
        # create both blocks
        rfDDsuper_block = PulseBlock(name=name)
        RF_block = PulseBlock(name='RF')
        
        # IQ phase correction
        def mw_func(block_name=rfDDsuper_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
            
        def rf_func(block_name=RF_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*(rf_freq+det_freq)*360,360)
            
            rf_phase_element = self._get_rf_element(length=pulse_dic[length]*rf_period, 
                                                    increment = 0, 
                                                    amp = rf_volt, 
                                                    freq = rf_freq, 
                                                    phase = acc_phase + phase_add)
            return rf_phase_element
            
            
        def rf_func_arb(block_name=RF_block, length=10e-9, phase_add = 0):
            acc_phase = np.mod((block_name.init_length_s)*(rf_freq+det_freq)*360,360)
            
            rf_phase_element = self._get_rf_element(length=length, 
                                                    increment = 0, 
                                                    amp = rf_volt, 
                                                    freq = rf_freq, 
                                                    phase = acc_phase + phase_add)
            return rf_phase_element
            
        # create elements
        waiting_element = self._get_idle_element(length = self.wait_time, increment=0)
        laser_element=self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element=self._get_delay_gate_element()
        awgtrig_element = self._get_awgtrig_element()
        
        mw_pix_element = mw_func(rfDDsuper_block, 'pi', 0)
        mw_piy_element = mw_func(rfDDsuper_block, 'pi', 90)
        mw_pi2x_element = mw_func(rfDDsuper_block, 'pi2', 0)
        mw_pi2y_element = mw_func(rfDDsuper_block, 'pi2', 90)
        mw_pi32x_element = mw_func(rfDDsuper_block, 'pi32', -180)
        
        phasedic = {'x':0, 'y':90}
        
        rf_pi_element = self._get_rf_element(length=rf_period/2,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = rf_freq,
                                                phase = 0)        
                                                
        rf_pi2_element = self._get_rf_element(length=rf_period/4,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = rf_freq,
                                                phase = 0)         
                                                
        rf_pi32_element = self._get_rf_element(length=rf_period/4,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = rf_freq,
                                                phase = 180)        
                                                        
        
        tau_se_element = self._get_idle_element(length = tau_se, increment = 0)        
            
        for var in rf_array:
            rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0)) # MW pi/2 pulse
            rfDDsuper_block.append(tau_se_element) # tau free evolution
            
            # idle periods to keep the MW and RF blocks in sync
            RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
            RF_block.append(tau_se_element)
            
            # Dynamical decoupling pulses + times between them
            ddcounter = 0
            rfDDsuper_block.append(self._get_idle_element(length = round(tau_dd*timedd[ddcounter],9), increment = 0))
            for ph in phaselist:
                ddcounter += 1
                if ph == '0':
                    rfDDsuper_block.append(self._get_idle_element(length = 0, increment = 0))
                else:
                    rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi', phasedic[ph]))
                    rfDDsuper_block.append(self._get_idle_element(length = round(tau_dd*timedd[ddcounter],9), increment = 0))
            
            
            if rfseqrun == 'rabi':
            # defines rabi pulses for different variables
                if vartype == 'time':
                    t_buff = tdd - var
                
                if vartype =='freq':
                    t_buff = tdd - rf_period/2
                    
                if vartype =='NVphase':
                    t_buff = tdd - tau_start
                    
                buffer_element = self._get_idle_element(length = t_buff/2, increment = 0) # to maintain sync between MW and RF
                RF_block.append(buffer_element)
                    
                if vartype == 'time':
                    addphase = np.mod((RF_block.init_length_s)*(rf_freq+det_freq)*360,360)
                    rf_rabi_element = self._get_rf_element(length = var,
                                                            increment = 0,
                                                            amp = rf_volt,
                                                            freq = rf_freq,
                                                            phase = aphase + addphase)
                
                if vartype =='freq':
                    rf_rabi_element = self._get_rf_element(length = rf_period/2,
                                                            increment = 0,
                                                            amp = rf_volt,
                                                            freq = var,
                                                            phase = 0)
                    
                if vartype =='NVphase':
                    rf_rabi_element = self._get_rf_element(length = tau_start,
                                                            increment = 0,
                                                            amp = rf_volt,
                                                            freq = rf_freq,
                                                            phase = 0)
                

                RF_block.append(rf_rabi_element) # add RF rabi pulse
                RF_block.append(buffer_element)
            
            if rfseqrun == 'ramsey':
            # defines buffer periods
                if vartype == 'time':
                    t_buff = tdd - var - rf_period/4 - pulse_time
                else:
                    t_buff = tdd - tau_start - rf_period/4 - pulse_time
                # if vartype == 'phase':
                        # rf_phase_element = self._get_rf_element(length=rf_period/4,
                                                # increment = 0,
                                                # amp = rf_volt,
                                                # freq = rf_freq,
                                                # phase = var)
                buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                tau_rf_element = self._get_idle_element(length = var if vartype=='time' else tau_start, increment = 0)
                RF_block.append(buffer_element)
                RF_block.append(rf_func(RF_block,'pi2',absphase)) # First rf pi/2 pulse for ramsey
                RF_block.append(tau_rf_element) # p1 free evolution period
                if vartype == 'phase':
                    RF_block.append(rf_func(RF_block,'pi2',absphase+var)) # second rf pi/2 pulse for ramsey
                else:
                    RF_block.append(rf_func_arb(RF_block,pulse_time,absphase+aphase))
                RF_block.append(buffer_element)
            
            if rfseqrun == 'spin_echo':
                # defines buffer times
                if vartype=='time':
                    t_buff = tdd - 2*var - 3*rf_period/4 - pulse_time
                else:
                    t_buff = tdd-2*tau_start - 3*rf_period/4 - pulse_time
                
                # if vartype == 'phase':
                        # rf_phase_element = self._get_rf_element(length=rf_period/4,
                                                # increment = 0,
                                                # amp = rf_volt,
                                                # freq = rf_freq,
                                                # phase = var)
                                                
                buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                tau_rf_element = self._get_idle_element(length = var if vartype == 'time' else tau_start, increment = 0)
                RF_block.append(buffer_element)
                # rf spin echo sequence
                RF_block.append(rf_func(RF_block,'pi2',absphase)) 
                RF_block.append(tau_rf_element)
                RF_block.append(rf_func(RF_block,'pi',absphase))
                RF_block.append(tau_rf_element)
                if vartype == 'phase':
                    RF_block.append(rf_func(RF_block,'pi2',absphase+var))
                else:
                    RF_block.append(rf_func_arb(RF_block,pulse_time,absphase+aphase))
                RF_block.append(buffer_element)
            
            # second NV free evolution period
            rfDDsuper_block.append(tau_se_element)
            if vartype == 'NVphase':
                rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', var))
            else:
                rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
            
            # idle blocks added to rf sequence to match mw sequence
            RF_block.append(tau_se_element)
            RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0))
            
            rfDDsuper_block.append(waiting_element)
            rfDDsuper_block.append(laser_element)
            rfDDsuper_block.append(delay_element)
            rfDDsuper_block.append(waiting_element)
            
            RF_block.append(waiting_element)
            RF_block.append(laser_element)
            RF_block.append(delay_element)
            RF_block.append(waiting_element)             
            
            if alternating:
                rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
                rfDDsuper_block.append(tau_se_element)
                
                RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
                RF_block.append(tau_se_element)
                
                ddcounter = 0
                rfDDsuper_block.append(self._get_idle_element(length = round(tau_dd*timedd[ddcounter],9), increment = 0))
                for ph in phaselist:
                    ddcounter += 1
                    if ph == '0':
                        rfDDsuper_block.append(self._get_idle_element(length = 0, increment = 0))
                    else:
                        rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi', phasedic[ph]))
                        rfDDsuper_block.append(self._get_idle_element(length = round(tau_dd*timedd[ddcounter],9), increment = 0))
                
                if rfseqrun == 'rabi':
                    buffer_element = self._get_idle_element(length = tdd, increment = 0)
                    RF_block.append(buffer_element)                
                
                if rfseqrun == 'ramsey':
                    if vartype == 'time':
                        t_buff = tdd - var - rf_period/4 - pulse_time
                    else:
                        t_buff = tdd - tau_start - rf_period/4 - pulse_time
                        
                    # if vartype == 'phase':
                        # rf_phase_alt_element = self._get_rf_element(length=rf_period/4,
                                                # increment = 0,
                                                # amp = rf_volt,
                                                # freq = rf_freq,
                                                # phase = var-180)
                    buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                    tau_rf_element = self._get_idle_element(length = var if vartype=='time' else tau_start, increment = 0)
                    RF_block.append(buffer_element)
                    RF_block.append(rf_func(RF_block,'pi2',absphase))
                    RF_block.append(tau_rf_element)
                    if vartype == 'phase':
                        RF_block.append(rf_func(RF_block,'pi2',absphase+var-180))
                    else:
                        RF_block.append(rf_func_arb(RF_block,pulse_time,absphase+aphase-180)) 
                    RF_block.append(buffer_element)
                
                if rfseqrun == 'spin_echo':
                    if vartype == 'time':
                        t_buff = tdd - 2*var - 3*rf_period/4 - pulse_time
                    else:
                        t_buff = tdd - 2*tau_start - 3*rf_period/4 - pulse_time
                        
                    # if vartype == 'phase':
                        # rf_phase_alt_element = self._get_rf_element(length=rf_period/4,
                                                # increment = 0,
                                                # amp = rf_volt,
                                                # freq = rf_freq,
                                                # phase = var-180)
                    
                    buffer_element = self._get_idle_element(length = t_buff/2, increment = 0)
                    tau_rf_element = self._get_idle_element(length = var if vartype == 'time' else tau_start, increment = 0)
                    RF_block.append(buffer_element)
                    RF_block.append(rf_func(RF_block,'pi2',absphase))
                    RF_block.append(tau_rf_element)
                    RF_block.append(rf_func(RF_block,'pi',absphase))
                    RF_block.append(tau_rf_element)
                    if vartype == 'phase':
                        RF_block.append(rf_func(RF_block,'pi2',absphase+var-180))
                    else:
                        RF_block.append(rf_func_arb(RF_block,pulse_time,absphase+aphase-180))
                    RF_block.append(buffer_element)
                    
                rfDDsuper_block.append(tau_se_element)
                if rfseqrun == 'rabi' and vartype == 'NVphase':
                    rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', var-180))
                elif rfseqrun == 'rabi' and num_of_points == 1:
                    # rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi32', -180))    
                    rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
                else:
                    rfDDsuper_block.append(mw_func(rfDDsuper_block, 'pi2', 0))
                RF_block.append(tau_se_element)
                RF_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0))

                rfDDsuper_block.append(waiting_element)
                rfDDsuper_block.append(laser_element)
                rfDDsuper_block.append(delay_element)
                rfDDsuper_block.append(waiting_element)

                
                RF_block.append(waiting_element)
                RF_block.append(laser_element)
                RF_block.append(delay_element)
                RF_block.append(waiting_element)             
            
        created_blocks.append(rfDDsuper_block)
        created_blocks.append(RF_block)
        
        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((rfDDsuper_block.name, 0))
        block_ensemble.append((RF_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['fold_sequence'] = fold_sequence
        block_ensemble.measurement_information['fold_channel'] = fold_channel
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
 
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    
    def generate_HHp1pol(self, name = 'HHp1pol', t_SE = 16e-6, t_SL=50e-6, tau_start=1e-9, tau_step=100e-9, num_of_points=10, rf_freq = 100e6, mwphases='x,y,x', 
                            rfphases='x,y,-x', mwseq = mwsequences.spinlock, alternating = True):
        """
         
        """
        # fold sequence: separate rf and mw sequences run simultaneously
        fold_sequence = True
        fold_channel = 'a_ch2' # the rf channel
        
        created_blocks=list()
        created_ensembles=list()
        created_sequences=list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        mw_period = self.rabi_period
        iq_freq = self.IQ_freq
        
        mwphaselist = mwphases.split(",")
        rfphaselist = rfphases.split(",")
        
        mwseqrun = mwseq.value
    
        rf_array = tau_start + np.arange(num_of_points) * tau_step
        
        unit = 's'
        sname = 'tau'                   
      
        # create both blocks
        HHp1pol_block = PulseBlock(name=name)
        HHRF_block = PulseBlock(name='HHRF')
        
        # IQ phase correction
        def mw_func(block_name=HHp1pol_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period,

                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        def mw_func_arb(block_name=HHp1pol_block, arb_length=100e-9, phase_add = 0):
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length = arb_length, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        def rf_func(block_name=HHRF_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*(rf_freq)*360,360)
            
            rf_phase_element = self._get_rf_element(length=pulse_dic[length]*rf_period, 
                                                    increment = 0, 
                                                    amp = rf_volt, 
                                                    freq = rf_freq, 
                                                    phase = acc_phase + phase_add)
            return rf_phase_element
        
        def rf_func_arb(block_name=HHRF_block, arb_length=100e-9, phase_add = 0):
            
            acc_phase = np.mod((block_name.init_length_s)*(rf_freq)*360,360)
            
            rf_phase_element = self._get_rf_element(length=arb_length, 
                                                    increment = 0, 
                                                    amp = rf_volt, 
                                                    freq = rf_freq, 
                                                    phase = acc_phase + phase_add)
            return rf_phase_element  
            
        # create elements
        waiting_element = self._get_idle_element(length = self.wait_time, increment=0)
        laser_element=self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element=self._get_delay_gate_element()
        awgtrig_element = self._get_awgtrig_element()
        
        phasedic = {'x':0, 'y':90, '-x':180}
        
        buff_time = 5e-9
                   
        for var in rf_array:
            if mwseqrun == 'spin_lock':
                HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[0]]))
                HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[0]]))
                
                if mw_period < rf_period:
                    pulse_buffer = 1/4*rf_period - 1/4*mw_period
                    HHp1pol_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 
                elif rf_period < mw_period:
                    pulse_buffer = 1/4*mw_period - 1/4*rf_period
                    HHRF_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 

                HHp1pol_block.append(self._get_idle_element(length = buff_time, increment=0))
                HHRF_block.append(self._get_idle_element(length = buff_time, increment=0))
                
                HHp1pol_block.append(mw_func_arb(HHp1pol_block, t_SL, phasedic[mwphaselist[1]]))
                HHRF_block.append(rf_func_arb(HHRF_block, var, phasedic[rfphaselist[1]]))
                sl_buffer = t_SL - var
                HHRF_block.append(self._get_idle_element(length = sl_buffer, increment=0))
                
                HHp1pol_block.append(self._get_idle_element(length = buff_time, increment=0))
                HHRF_block.append(self._get_idle_element(length = buff_time, increment=0))
                
                HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[2]]))
                HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[2]]))
                
                if mw_period < rf_period:
                    pulse_buffer = 1/4*rf_period - 1/4*mw_period
                    HHp1pol_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 
                elif rf_period < mw_period:
                    pulse_buffer = 1/4*mw_period - 1/4*rf_period
                    HHRF_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 

            if mwseqrun == 'spin_echo':
                HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[0]]))
                HHRF_block.append(self._get_idle_element(length = 1/4*mw_period, increment=0))
                
                total_time = t_SE*2 + 1/2*mw_period
                rf_buff_time = round((total_time - var - 2*buff_time - 1/2*rf_period)/2,9)
                
                HHp1pol_block.append(self._get_idle_element(length = t_SE, increment=0))
                HHp1pol_block.append(mw_func(HHp1pol_block, 'pi', phasedic[mwphaselist[0]]))
                HHp1pol_block.append(self._get_idle_element(length = t_SE, increment=0))
                
                HHRF_block.append(self._get_idle_element(length = rf_buff_time, increment=0))
                HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[0]]))
                HHRF_block.append(self._get_idle_element(length = buff_time, increment=0))
                HHRF_block.append(rf_func_arb(HHRF_block, var, phasedic[rfphaselist[1]]))
                HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[2]]))
                HHRF_block.append(self._get_idle_element(length = rf_buff_time, increment=0))

                HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[2]]))
                HHRF_block.append(self._get_idle_element(length = 1/4*mw_period, increment=0))

            HHp1pol_block.append(waiting_element)
            HHp1pol_block.append(laser_element)
            HHp1pol_block.append(delay_element)
            HHp1pol_block.append(waiting_element)
            
            HHRF_block.append(waiting_element)
            HHRF_block.append(laser_element)
            HHRF_block.append(delay_element)
            HHRF_block.append(waiting_element)

            if alternating:
                if mwseqrun == 'spin_lock':
                    HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[0]]))
                    HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[0]]))
                    
                    if mw_period < rf_period:
                        pulse_buffer = 1/4*rf_period - 1/4*mw_period
                        HHp1pol_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 
                    elif rf_period < mw_period:
                        pulse_buffer = 1/4*mw_period - 1/4*rf_period
                        HHRF_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 

                    HHp1pol_block.append(self._get_idle_element(length = buff_time, increment=0))
                    HHRF_block.append(self._get_idle_element(length = buff_time, increment=0))                

                    HHp1pol_block.append(mw_func_arb(HHp1pol_block, t_SL, phasedic[mwphaselist[1]]))
                    
                    HHRF_block.append(rf_func_arb(HHRF_block, var, phasedic[rfphaselist[1]]))
                    sl_buffer = t_SL - var
                    HHRF_block.append(self._get_idle_element(length = sl_buffer, increment=0))
     
                    HHp1pol_block.append(self._get_idle_element(length = buff_time, increment=0))
                    HHRF_block.append(self._get_idle_element(length = buff_time, increment=0))
                    
                    HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[2]]+180))
                    HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[2]]))
                    
                    if mw_period < rf_period:
                        pulse_buffer = 1/4*rf_period - 1/4*mw_period
                        HHp1pol_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 
                    elif rf_period < mw_period:
                        pulse_buffer = 1/4*mw_period - 1/4*rf_period
                        HHRF_block.append(self._get_idle_element(length = pulse_buffer, increment=0)) 

                    
                if mwseqrun == 'spin_echo':
                    HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[0]]))
                    HHRF_block.append(self._get_idle_element(length = 1/4*mw_period, increment=0))
                    
                    total_time = t_SE*2 + 1/2*mw_period
                    rf_buff_time = round((total_time - var - 2*buff_time - 1/2*rf_period)/2,9)
                    
                    HHp1pol_block.append(self._get_idle_element(length = t_SE, increment=0))
                    HHp1pol_block.append(mw_func(HHp1pol_block, 'pi', phasedic[mwphaselist[0]]))
                    HHp1pol_block.append(self._get_idle_element(length = t_SE, increment=0))
                    
                    HHRF_block.append(self._get_idle_element(length = rf_buff_time, increment=0))
                    HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[0]]))
                    HHRF_block.append(self._get_idle_element(length = buff_time, increment=0))
                    HHRF_block.append(rf_func_arb(HHRF_block, var, phasedic[rfphaselist[1]]))
                    HHRF_block.append(rf_func(HHRF_block,'pi2', phasedic[rfphaselist[2]]+180))
                    HHRF_block.append(self._get_idle_element(length = rf_buff_time, increment=0))

                    HHp1pol_block.append(mw_func(HHp1pol_block, 'pi2', phasedic[mwphaselist[2]]))
                    HHRF_block.append(self._get_idle_element(length = 1/4*mw_period, increment=0))
                
                HHp1pol_block.append(waiting_element)
                HHp1pol_block.append(laser_element)
                HHp1pol_block.append(delay_element)
                HHp1pol_block.append(waiting_element)
                
                HHRF_block.append(waiting_element)
                HHRF_block.append(laser_element)
                HHRF_block.append(delay_element)
                HHRF_block.append(waiting_element)
            
            
        created_blocks.append(HHp1pol_block)
        created_blocks.append(HHRF_block)
        
        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((HHp1pol_block.name, 0))
        block_ensemble.append((HHRF_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['fold_sequence'] = fold_sequence
        block_ensemble.measurement_information['fold_channel'] = fold_channel
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
 
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

        
    def generate_correlation(self, name = 'correlation', tau_se=50e-6, tau_start=1e-9, tau_step=100e-9, num_of_points=10, det_freq=0, 
                            se_seq1 = 'x,x,y', se_seq2 = 'x,x,y', alternating=False):
        """
        
        """
        
        created_blocks=list()
        created_ensembles=list()
        created_sequences=list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        mw_period = self.rabi_period
        iq_freq = self.IQ_freq
        
        sephaselist1 = se_seq1.split(",")
        sephaselist2 = se_seq2.split(",")

        fold_sequence = False

        rf_array = tau_start + np.arange(num_of_points) * tau_step
        unit = 's'
        sname = 'tau'
                
        # create blocks        
        correlation_block = PulseBlock(name=name)
        
        # IQ phase correction
        def mw_func(block_name=correlation_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
            
        waiting_element = self._get_idle_element(length = self.wait_time, increment=0)
        laser_element=self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element=self._get_delay_gate_element()
        awgtrig_element = self._get_awgtrig_element()
        
        tau_se_element = self._get_idle_element(length = tau_se, increment = 0)
        
        phasedic = {'x':0, 'y':90}
        
        for var in rf_array:
            # NV spin echo sequence 1
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[0]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist1[1]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[2]]))
            
            # variable time between spin echo sequences
            correlation_block.append(self._get_idle_element(length = var, increment = 0))

            # NV spin echo sequence 2
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[0]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist2[1]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[2]])) 

            correlation_block.append(waiting_element)
            correlation_block.append(laser_element)
            correlation_block.append(delay_element)
            correlation_block.append(waiting_element)
            
            if alternating:
                # NV spin echo sequence 1
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[0]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist1[1]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[2]]))
                
                # variable time between spin echo sequences
                correlation_block.append(self._get_idle_element(length = var, increment = 0))

                # NV spin echo sequence 2
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[0]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist2[1]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[2]] - 180))

                correlation_block.append(waiting_element)
                correlation_block.append(laser_element)
                correlation_block.append(delay_element)
                correlation_block.append(waiting_element)
                
        created_blocks.append(correlation_block)  
        
        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((correlation_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
 
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
    
    def generate_correlationRF(self, name = 'correlationRF', tau_se=4e-6, t_corr=200e-6, tau_start=1e-9, tau_step=100e-9, num_of_points=10, rf_pulse = '2pi', rf_freq = 100e6, range_freq=10e6,
                               d_freq = 500e3, det_freq=0, rfseq = rfsequences.rabi, type = rfvariables.time, se_seq1 = 'x,x,y', se_seq2 = 'x,x,y', alternating=False):
        """
        
        """
        # fold the sequence for simultaneous MW and RF
        fold_sequence = True
        fold_channel = 'a_ch2' # the rf channel
        
        created_blocks=list()
        created_ensembles=list()
        created_sequences=list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        mw_period = self.rabi_period
        iq_freq = self.IQ_freq
        
        rfpulsedic = {'pi2':1/4, 'pi':1/2, '2pi':1}
        rf_pulse_length = rfpulsedic[rf_pulse]*rf_period
        
        sephaselist1 = se_seq1.split(",")
        sephaselist2 = se_seq2.split(",")

        rfseqrun = rfseq.value
        vartype = type.value
        
        # get array for measurement ticks (just time for now, can add in frequency
        if vartype == 'time':
            rf_array = tau_start + np.arange(num_of_points) * tau_step
            unit = 's'
            sname = 'tau'
            
        if vartype == 'freq':
            num_of_points = int(2*range_freq/d_freq)
            rf_array = (rf_freq - range_freq) + np.arange(num_of_points) * d_freq
            unit = 'Hz'
            sname = 'freq'            
        
        if vartype == 'phase':
            d_phase = int(360./num_of_points)
            rf_array = np.arange(num_of_points+1) * d_phase
            unit = '°'
            sname = 'phase'
            num_of_points=num_of_points+1
            self.log.error('Have not implemented  sequence for this variable.')
                
        # create blocks        
        correlation_block = PulseBlock(name=name)
        RFcorrelation_block = PulseBlock(name='RF')  
        
        # IQ phase correction
        def mw_func(block_name=correlation_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
            
        def rf_func(block_name=RFcorrelation_block, length='pi2', pulse_freq=rf_freq, phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2, '2pi':1, 'pi32': 1/4}
            acc_phase = np.mod((block_name.init_length_s)*(pulse_freq+det_freq)*360,360)
            
            rf_phase_element = self._get_rf_element(length=pulse_dic[length]*rf_period, 
                                                    increment = 0, 
                                                    amp = rf_volt, 
                                                    freq = pulse_freq, 
                                                    phase = acc_phase + phase_add)
            return rf_phase_element
            
        waiting_element = self._get_idle_element(length = self.wait_time, increment=0)
        laser_element=self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element=self._get_delay_gate_element()
        awgtrig_element = self._get_awgtrig_element()
        
        tau_se_element = self._get_idle_element(length = tau_se, increment = 0)
        
        phasedic = {'x':0, 'y':90}

        for var in rf_array:
            if vartype == 'freq':
                rfpulsefreq = var
            else:
                rfpulsefreq = rf_freq
            
            # NV spin echo sequence 1
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[0]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist1[1]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[2]]))
            
            # idle time for RF sequence during NV spin echo 1
            RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
            RFcorrelation_block.append(tau_se_element)            
            RFcorrelation_block.append(self._get_idle_element(length = 1/2*self.rabi_period, increment=0)) 
            RFcorrelation_block.append(tau_se_element)
            RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
            
            # variable time between spin echo sequences
            correlation_block.append(self._get_idle_element(length = t_corr, increment = 0))
            if vartype == 'time':
                t_buff1 = var
                t_buff2 = t_corr - var - rf_pulse_length
                if t_buff2 < 0:
                    self.log.error('WRONG TIMING')
            else:
                t_buff1 = (t_corr - rf_pulse_length)/2
                t_buff2 = (t_corr - rf_pulse_length)/2

            RFcorrelation_block.append(self._get_idle_element(length = t_buff1, increment = 0))
            RFcorrelation_block.append(rf_func(RFcorrelation_block, rf_pulse, rfpulsefreq, 0))
            RFcorrelation_block.append(self._get_idle_element(length = t_buff2, increment = 0))
            
            # NV spin echo sequence 2
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[0]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist2[1]]))
            correlation_block.append(tau_se_element)
            correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[2]]))            

            # idle time for RF sequence during NV spin echo 2
            RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
            RFcorrelation_block.append(tau_se_element)            
            RFcorrelation_block.append(self._get_idle_element(length = 1/2*self.rabi_period, increment=0)) 
            RFcorrelation_block.append(tau_se_element)
            RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0))   

            correlation_block.append(waiting_element)
            correlation_block.append(laser_element)
            correlation_block.append(delay_element)
            correlation_block.append(waiting_element)
            
            RFcorrelation_block.append(waiting_element)
            RFcorrelation_block.append(laser_element)
            RFcorrelation_block.append(delay_element)
            RFcorrelation_block.append(waiting_element)

            if alternating:
                # NV spin echo sequence 1
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[0]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist1[1]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist1[2]]))
                
                # idle time for RF sequence during NV spin echo 1
                RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
                RFcorrelation_block.append(tau_se_element)            
                RFcorrelation_block.append(self._get_idle_element(length = 1/2*self.rabi_period, increment=0)) 
                RFcorrelation_block.append(tau_se_element)
                RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
                
                # variable time between spin echo sequences
                correlation_block.append(self._get_idle_element(length = t_corr, increment = 0))
                RFcorrelation_block.append(self._get_idle_element(length = t_corr, increment = 0))

                # NV spin echo sequence 2
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[0]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi', phasedic[sephaselist2[1]]))
                correlation_block.append(tau_se_element)
                correlation_block.append(mw_func(correlation_block, 'pi2', phasedic[sephaselist2[2]]))            

                # idle time for RF sequence during NV spin echo 2
                RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0)) 
                RFcorrelation_block.append(tau_se_element)            
                RFcorrelation_block.append(self._get_idle_element(length = 1/2*self.rabi_period, increment=0)) 
                RFcorrelation_block.append(tau_se_element)
                RFcorrelation_block.append(self._get_idle_element(length = 1/4*self.rabi_period, increment=0))   

                correlation_block.append(waiting_element)
                correlation_block.append(laser_element)
                correlation_block.append(delay_element)
                correlation_block.append(waiting_element)
                
                RFcorrelation_block.append(waiting_element)
                RFcorrelation_block.append(laser_element)
                RFcorrelation_block.append(delay_element)
                RFcorrelation_block.append(waiting_element)
                
        created_blocks.append(correlation_block)  
        created_blocks.append(RFcorrelation_block)  
        
        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((correlation_block.name, 0))
        block_ensemble.append((RFcorrelation_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['fold_sequence'] = fold_sequence
        block_ensemble.measurement_information['fold_channel'] = fold_channel
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
 
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
    
    def generate_foldtest(self, name = 'foldtest', mw_time = 100e-9, rf_time = 200e-9, rf_freq=100e6, tau_start = 1e-9, tau_step = 10e-9, num_of_points = 25):
        """
        
        """
        fold_sequence = True
        fold_channel = 'a_ch2'
        alternating = False
        
        created_blocks=list()
        created_ensembles=list()
        created_sequences=list()
        
        iq_freq = self.IQ_freq
        rf_volt = dBmtoV(self.rf_power)
        
        # laser_length_gate = 3e-6
        # laser_length_laser = self.laser_length - 3e-6+100e-9
        
        waiting_element = self._get_idle_element(length = self.wait_time, increment=0)
        laser_element=self._get_laser_element(length=self.laser_length, increment=0)
        delay_element=self._get_delay_gate_element()
        awgtrig_element = self._get_awgtrig_element()
        
        tau_array = tau_start + np.arange(num_of_points) * tau_step
        
        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)

        
        foldtest_block = PulseBlock(name=name)
        rffold_block = PulseBlock(name='RF')
        
        rf_element = self._get_rf_element(length=rf_time,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = rf_freq,
                                                phase = 0)
        
        def mw_func(block_name=foldtest_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        foldtest_block.append(mw_func(foldtest_block,'pi2',0))
        rffold_block.append(self._get_idle_element(length = self.rabi_period/2., increment=0))
        
        foldtest_block.append(tau_element)
        rffold_block.append(tau_element)        
        
        foldtest_block.append(self._get_idle_element(length = rf_time, increment=0))
        rffold_block.append(rf_element)        
        
        foldtest_block.append(waiting_element)
        foldtest_block.append(laser_element)
        foldtest_block.append(delay_element)
        foldtest_block.append(waiting_element)
        
        rffold_block.append(waiting_element)
        rffold_block.append(laser_element)
        rffold_block.append(delay_element)
        rffold_block.append(waiting_element)
        
        created_blocks.append(foldtest_block)
        created_blocks.append(rffold_block)
        
        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((foldtest_block.name, 0))
        block_ensemble.append((rffold_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
        
        # Create and append awg trigger block if needed        
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['fold_sequence'] = fold_sequence
        block_ensemble.measurement_information['fold_channel'] = fold_channel        
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
 
    def generate_mwsuper(self, name='mwsuper', tau_start=1e-9, tau_step=10e-9, num_of_points = 50, abs_phase = 0, fixed_time = 50e-6, sequence = rfsequences.ramsey, 
                            type = rfvariables.time, alternating = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        iq_freq = self.IQ_freq
        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get measurement array for measurement ticks
        seqtype = sequence.value
        vartype = type.value
        
        if vartype == 'time':
            
            rf_array = tau_start + np.arange(num_of_points) * tau_step
            unit = 's'
            sname = 'tau'
            
        # if vartype == 'freq':
            
            # num_of_points = int(2*range_freq/d_freq)
            # rf_array = (freq - range_freq) + np.arange(num_of_points) * d_freq
            # unit = 'Hz'
            # sname = 'freq'    
            
        if vartype == 'phase':            
            rf_array = np.linspace(0,360,num_of_points) 
            unit = '°'
            sname = 'phase'   

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        awgtrig_element = self._get_awgtrig_element()
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        
        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                      increment=0,
                                      amp=self.microwave_amplitude,
                                      freq=iq_freq,
                                      phase=abs_phase)        
        
        pi2_element = self._get_mw_element(length=self.rabi_period / 4,
                                      increment=0,
                                      amp=self.microwave_amplitude,
                                      freq=iq_freq,
                                      phase=abs_phase)
        
        dummy_element =self._get_idle_element(length=self.rabi_period / 2, increment=0)
        # Create block and append to created_blocks list
        mwsuper_block = PulseBlock(name=name)  
        
        # creates phase synchronous IQ mw elements
        def mw_func(block_name=mwsuper_block, length='pi2', phase_add = abs_phase):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        # mwsuper_block.append(awgtrig_element)
        
        for var in rf_array:
            tau_element = self._get_idle_element(length = var if vartype =='time' else fixed_time,
                                                increment = 0)
            
            mwsuper_block.append(mw_func(mwsuper_block,'pi2',abs_phase))
            # print('time elapsed in sequence')
            # print(mwsuper_block.init_length_s)
            # print('phase position')
            # print(iq_freq*(mwsuper_block.init_length_s))
            mwsuper_block.append(tau_element)
            if seqtype=='spin_echo':
                mwsuper_block.append(mw_func(mwsuper_block,'pi',abs_phase))
                mwsuper_block.append(tau_element)
                
            mwsuper_block.append(mw_func(mwsuper_block,'pi2', (abs_phase+var) if vartype=='phase' else abs_phase))
            mwsuper_block.append(waiting_element)
            mwsuper_block.append(laser_element)
            mwsuper_block.append(delay_element)
            mwsuper_block.append(waiting_element)
            
            if alternating:
                mwsuper_block.append(mw_func(mwsuper_block,'pi2',abs_phase))
                mwsuper_block.append(tau_element)
                if seqtype=='spin_echo':
                    mwsuper_block.append(mw_func(mwsuper_block,'pi',abs_phase))
                    mwsuper_block.append(tau_element)
                
                mwsuper_block.append(mw_func(mwsuper_block,'pi2', (abs_phase+var-180) if vartype=='phase' else abs_phase-180))    
                mwsuper_block.append(waiting_element)
                mwsuper_block.append(laser_element)
                mwsuper_block.append(delay_element)
                mwsuper_block.append(waiting_element)
                
        created_blocks.append(mwsuper_block)
        
        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((mwsuper_block.name, num_of_points - 1))
        

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences  
        
    def generate_hahnechosync(self, name='hahn_echo_sync', tau_start=40.0e-6, tau_step=1.0e-6,
                          num_of_points=1, alternating=True, ramsey = False, pi1 = False, pi2 = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us

        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length

        time_before = self.time_before_mw
        print(type(self.rotation_period),type(self.rabi_period),type(self.laser_delay),type(self.time_before_mw)) 
        time_after = self.rotation_period - 2*tau_start - self.rabi_period - self.laser_delay - laser_length_gate - time_before
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_before_element = self._get_idle_element(length=time_before,increment=0)
        waiting_after_element = self._get_idle_element(length=time_after,increment= -2*tau_step )
                                                 
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        laser_prep_element = self._get_laser_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
        pifull_element = self._get_mw_element(length=self.rabi_period,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)                                          
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)

        # Create block and append to created_blocks list
        hahn_sync_block = PulseBlock(name=name)
        if num_of_points < 2:
            hahn_sync_block.append(laser_prep_element)
        hahn_sync_block.append(delay_element)
        hahn_sync_block.append(waiting_before_element)
        if not pi1:
            hahn_sync_block.append(pihalf_element)
        hahn_sync_block.append(tau_element)
        if not ramsey:
            hahn_sync_block.append(pi_element)
        hahn_sync_block.append(tau_element)
        if not pi1:
            hahn_sync_block.append(pihalf_element)
        hahn_sync_block.append(waiting_after_element)
        hahn_sync_block.append(lasergate_element)
        hahn_sync_block.append(laser_element)
        hahn_sync_block.append(delay_element)
        # hahn_sync_block.append(waiting_element)# this is the synchronisation time - must be set so that time from first pi/2 pulse to here is exactly rotation period
        if alternating:
            hahn_sync_block.append(waiting_before_element)
            if not pi1:
                hahn_sync_block.append(pihalf_element)
            hahn_sync_block.append(tau_element)
            if not pi1:
                hahn_sync_block.append(pi_element)
            if not ramsey:
                hahn_sync_block.append(pi_element)
            if pi2:
                hahn_sync_block.append(pifull_element)
            hahn_sync_block.append(tau_element)
            if not pi1:
                hahn_sync_block.append(pi3half_element)
            hahn_sync_block.append(waiting_after_element)
            hahn_sync_block.append(lasergate_element)
            hahn_sync_block.append(laser_element)
            hahn_sync_block.append(delay_element)
            # hahn_sync_block.append(waiting_element)
        created_blocks.append(hahn_sync_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((hahn_sync_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences


    def generate_rotaverage(self, name='rot_ave', tau_start=1.0e-6, tau_step=1.0e-6,
                          num_of_points=1, tau_1 = 1e-6, tau_2 = 1e-6, alternating=False, testing = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us


        
        #########################################################################Rotational Averaging Pulse Sequence#############################################################################
        #                  |<-----------------------------------------------------------------T_rot-------------------------------------------------------------------->|                       #
        #__________________|LASER|______________________________________________________________________________________________________________________________________|LASER|_________________#
        #________________________________|pi2|__t__|pi2|____________________________|pi2|__t__|pi2|_____________________________|pi2|__t__|pi2|_________________________________________________#
        #      Trigger            |<-tb->|      |<---------------T_rot/3------------------>|<------------------T_rot/3--------------- >|       |<------time_after----->|                        #
        #                                |<---t_seq--->|                            |<---t_seq--->|                             |<---t_seq--->|                                                 #
        #                                              |<-------time_between------->|              |<-------time_between------->|                                                               #
        #                  |<--t_prep--->|                                                                                                                                                      #
        #########################################################################################################################################################################################
        
        
        #########################################################################Rotational Averaging Pulse Sequence 2###########################################################################
        #                  |<-----------------------------------------------------------------T_rot-------------------------------------------------------------------------->|                 #
        #__________________|LASER|____________________________________________________________________________________________________________________________________________|LASER|___________#
        #________________________________|pi2|__t__|pi2|____________________________|pi2|__t__|pi2|_____________________________|pi2|__tau-1__|pi|__tau-2__|pi2|________________________________#
        #      Trigger            |<-tb->|   |<---------------T_rot/3------------------>|<------------------T_rot/3--------------- >|                          |<-time_after->|                 #
        #                                |<---t_seq--->|                            |<---t_seq--->|                             |<---------time_seq_var------->|                                #
        #                                              |<-------time_between------->|              |<-------time_between------->|                                                               #
        #                  |<--t_prep--->|                                                                                                                                                      #
        #########################################################################################################################################################################################
        
        #########################################################################Rotational Averaging Pulse Sequence 3###########################################################################
        #                  |<-----------------------------------------------------------------T_rot-------------------------------------------------------------------------->|                 #
        #__________________|LASER|____________________________________________________________________________________________________________________________________________|LASER|___________#
        #________________________________|pi2|_t_|pi|_t_|pi2|____________________________|pi2|_t_|pi|_t_|pi2|_____________________________|pi2|_t_|pi|_t_|pi2|________________________________#
        #      Trigger            |<-tb->|         |<-------------------T_rot/3------------------>|<-----------------------T_rot/3--------------- >|         |<-time_after->|                 #
        #                                |<-----t_seq------>|                            |<------t_seq----->|                             |<----t_seq------->|                                #
        #                                                   |<-------time_between------->|                  |<--------time_between------->|                                                               #
        #                  |<--t_prep--->|                                                                                                                                                      #
        #########################################################################################################################################################################################
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        time_before = self.time_before_mw
        time_prep = self.laser_delay + laser_length_gate + time_before
        tpi2 = self.rabi_period/4.
        tpi = self.rabi_period/2.
        time_rams = self.rams_time
        
        
        time_between = self.rotation_period/3.- 2*tau_start - 2 * tpi2 # center of pi to center of pi

        time_seq = tpi2 + tau_start + tpi+ tau_start + tpi2

        
        time_after = self.rotation_period - time_prep - time_seq - time_between - time_seq - time_between - time_seq
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step
        # if 'testing' sequence just does a pi pulse 'time_before' after the laser in the first seq and nothing in the second.
        time_testing = self.rotation_period - time_prep - 2*tpi2
        # create the elements
        ramsey_time_element = self._get_idle_element(length=time_rams,increment=0)
        waiting_before_element = self._get_idle_element(length=time_before,increment=0)
        waiting_between_element = self._get_idle_element(length=time_between,increment= 0 )
        waiting_after_element = self._get_idle_element(length=time_after if not testing else time_testing,increment= 0 )
                                                 
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        laser_prep_element = self._get_laser_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
                                      
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        tau_element = self._get_idle_element(length=tau_start, increment=0)
        # tau2_element = self._get_idle_element(length=tau_2, increment=0)

        # Create block and append to created_blocks list
        rot_ave_block = PulseBlock(name=name)
        if not testing:
            rot_ave_block.append(laser_prep_element)
            rot_ave_block.append(delay_element)
            rot_ave_block.append(waiting_before_element)

            rot_ave_block.append(pihalf_element)
            rot_ave_block.append(tau_element)
            rot_ave_block.append(pi_element)
            rot_ave_block.append(tau_element)
            rot_ave_block.append(pihalf_element)
            
            rot_ave_block.append(waiting_between_element)
            
            rot_ave_block.append(pihalf_element)
            rot_ave_block.append(tau_element)
            rot_ave_block.append(pi_element)
            rot_ave_block.append(tau_element)
            rot_ave_block.append(pihalf_element)
            
            rot_ave_block.append(waiting_between_element)
            
            rot_ave_block.append(pihalf_element)
            rot_ave_block.append(tau_element)
            rot_ave_block.append(pi_element)
            rot_ave_block.append(tau_element)
            rot_ave_block.append(pihalf_element)
            
            rot_ave_block.append(waiting_after_element)
            
            rot_ave_block.append(lasergate_element)
            rot_ave_block.append(laser_element)
            rot_ave_block.append(delay_element)
            # hahn_sync_block.append(waiting_element)# this is the synchronisation time - must be set so that time from first pi/2 pulse to here is exactly rotation period
            if alternating:
                rot_ave_block.append(waiting_before_element)
                rot_ave_block.append(pihalf_element)
                rot_ave_block.append(ramsey_time_element)
                rot_ave_block.append(pihalf_element)
                
                rot_ave_block.append(waiting_between_element)
                
                rot_ave_block.append(pihalf_element)
                rot_ave_block.append(ramsey_time_element)
                rot_ave_block.append(pihalf_element)
                
                rot_ave_block.append(waiting_between_element)
                
                rot_ave_block.append(pihalf_element)
                rot_ave_block.append(tau_element)
                rot_ave_block.append(pi3half_element)
                
                rot_ave_block.append(waiting_after_element)
                
                rot_ave_block.append(lasergate_element)
                rot_ave_block.append(laser_element)
                rot_ave_block.append(delay_element)

        else:
            rot_ave_block.append(laser_prep_element)
            rot_ave_block.append(delay_element)
            rot_ave_block.append(waiting_before_element)
            
            rot_ave_block.append(pi_element)

            
            

            
            rot_ave_block.append(waiting_after_element)
            
            rot_ave_block.append(lasergate_element)
            rot_ave_block.append(laser_element)
            rot_ave_block.append(delay_element)
            # hahn_sync_block.append(waiting_element)# this is the synchronisation time - must be set so that time from first pi/2 pulse to here is exactly rotation period
            if alternating:

                rot_ave_block.append(waiting_before_element)
                
            
                rot_ave_block.append(waiting_after_element)
                
                rot_ave_block.append(lasergate_element)
                rot_ave_block.append(laser_element)
                rot_ave_block.append(delay_element)
        created_blocks.append(rot_ave_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((rot_ave_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_pipi(self, name='pi_pi', tau_start=0.0e-6, tau_step=1.0e-6,
                          num_of_points=50,  alternating=True):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        delay_element = self._get_delay_gate_element()

        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog

        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)

        # Create block and append to created_blocks list
        hahn_block = PulseBlock(name=name)

        hahn_block.append(tau_element)
        
        hahn_block.append(pi_element)
        hahn_block.append(tau_element)

        hahn_block.append(lasergate_element)
        hahn_block.append(laser_element)
        hahn_block.append(delay_element)
        hahn_block.append(waiting_element)
        if alternating:

            hahn_block.append(tau_element)

            hahn_block.append(tau_element)

            hahn_block.append(lasergate_element)
            hahn_block.append(laser_element)
            hahn_block.append(delay_element)
            hahn_block.append(waiting_element)
        created_blocks.append(hahn_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((hahn_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_acSync(self, name='acSync', tau_start=0.0e-6, tau_step=1.0e-6,
                          num_of_points=50, total_seq_time = 100e-6):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # if self.laser_length > 3e-6:# for laser pulses longer than 3us, counter overloading can occur (only if the gate time is as long as the laser time). so we append to the laser_gate block the remaining duration of the laser
        laser_length_gate = 3e-6 #laser gates are 3us
        print('appending laser length')
        laser_length_laser = self.laser_length - 3e-6+100e-9 #just ensures its not zero length
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step
        filter = tau_array >= total_seq_time - self.laser_length -2e-6 
        if filter.any():
            self.log.warning('the total range spanned by the rf sequence exceeds t_off. Increase t_off. ')


        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
        laser2_element = self._get_laser_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()

        mw_element = self._get_mw_element(length=tau_start,
                                          increment=tau_step,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        
        t1 = total_seq_time/2 - tau_start/2 - self.laser_length

        t1_element = self._get_idle_element(length=total_seq_time/2 - tau_start/2 - self.laser_length, increment=-tau_step/2)

        # Create block and append to created_blocks list
        hahn_block = PulseBlock(name=name)


        hahn_block.append(laser2_element)
        
        hahn_block.append(t1_element)
        hahn_block.append(mw_element)
        hahn_block.append(t1_element)

        hahn_block.append(lasergate_element)
        hahn_block.append(laser_element)
        hahn_block.append(delay_element)
        hahn_block.append(waiting_element)
        
        created_blocks.append(hahn_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((hahn_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = num_of_points #
        block_ensemble.measurement_information['alternating'] = False
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences



    def generate_hahnecho_exp(self, name='hahn_echo', tau_start=1.0e-6, tau_end=1.0e-6,
                                 num_of_points=50, alternating=True):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()


        # get tau array for measurement ticks
        if tau_start == 0.0:
            tau_array = np.geomspace(1e-9, tau_end, num_of_points - 1)
            tau_array = np.insert(tau_array, 0, 0.0)
        else:
            tau_array = np.geomspace(tau_start, tau_end, num_of_points)

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        lasergate_element = self._get_laser_gate_element(length=laser_length_gate, increment=0)
        laser_element = self._get_laser_element(length=laser_length_laser, increment=0)
                                                     
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                          increment=0,
                                          amp=self.microwave_amplitude,
                                          freq=self.microwave_frequency,
                                          phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)

        # Create block and append to created_blocks list
        # Create block and append to created_blocks list
        hahn_block = PulseBlock(name=name)
        for tau in tau_array:
            tau_element = self._get_idle_element(length=tau, increment=0.0)
            hahn_block.append(pihalf_element)
            hahn_block.append(tau_element)
            hahn_block.append(pi_element)
            hahn_block.append(tau_element)
            hahn_block.append(pihalf_element)
            hahn_block.append(waiting_element)
            hahn_block.append(lasergate_element)
            hahn_block.append(laser_element)
            hahn_block.append(delay_element)
            hahn_block.append(waiting_element)
            if alternating:
                hahn_block.append(pihalf_element)
                hahn_block.append(tau_element)
                hahn_block.append(pi_element)
                hahn_block.append(tau_element)
                hahn_block.append(pi3half_element)
                hahn_block.append(waiting_element)
                hahn_block.append(lasergate_element)
                hahn_block.append(laser_element)
                hahn_block.append(delay_element)
                hahn_block.append(waiting_element)
        created_blocks.append(hahn_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((hahn_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_t1(self, name='T1', tau_start=1.0e-6, tau_step=1.0e-6,
                    num_of_points=50, alternating = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length,
                                                     increment=0)
        delay_element = self._get_delay_gate_element()
        if alternating: # get pi element
            pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)

        tau_element = self._get_idle_element(length=tau_start, increment=tau_step)
        t1_block = PulseBlock(name=name)
        t1_block.append(tau_element)
        t1_block.append(laser_element)
        t1_block.append(delay_element)
        t1_block.append(waiting_element)
        if alternating:
            t1_block.append(pi_element)
            t1_block.append(tau_element)
            t1_block.append(laser_element)
            t1_block.append(delay_element)
            t1_block.append(waiting_element)
        created_blocks.append(t1_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((t1_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_t1_exponential(self, name='T1_exp', tau_start=1.0e-6, tau_end=1.0e-6,
                    num_of_points=50, alternating=False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get tau array for measurement ticks
        if tau_start == 0.0:
            tau_array = np.geomspace(1e-9, tau_end, num_of_points - 1)
            tau_array = np.insert(tau_array, 0, 0.0)
        else:
            tau_array = np.geomspace(tau_start, tau_end, num_of_points)

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length,
                                                     increment=0)
        delay_element = self._get_delay_gate_element()
        if alternating:  # get pi element
            pi_element = self._get_mw_element(length=self.rabi_period / 2,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        t1_block = PulseBlock(name=name)
        for tau in tau_array:
            tau_element = self._get_idle_element(length=tau, increment=0.0)
            t1_block.append(tau_element)
            t1_block.append(laser_element)
            t1_block.append(delay_element)
            t1_block.append(waiting_element)
            if alternating:
                t1_block.append(pi_element)
                t1_block.append(tau_element)
                t1_block.append(laser_element)
                t1_block.append(delay_element)
                t1_block.append(waiting_element)
        created_blocks.append(t1_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((t1_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)
        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_HHamp(self, name='hh_amp', spinlock_length=20e-6, amp_start=0.05, amp_step=0.01,
                       num_of_points=50):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get amplitude array for measurement ticks
        amp_array = amp_start + np.arange(num_of_points) * amp_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time, increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)

        # Create block and append to created_blocks list
        hhamp_block = PulseBlock(name=name)
        for sl_amp in amp_array:
            sl_element = self._get_mw_element(length=spinlock_length,
                                              increment=0,
                                              amp=sl_amp,
                                              freq=self.microwave_frequency,
                                              phase=90)
            hhamp_block.append(pihalf_element)
            hhamp_block.append(sl_element)
            hhamp_block.append(pihalf_element)
            hhamp_block.append(laser_element)
            hhamp_block.append(delay_element)
            hhamp_block.append(waiting_element)

            hhamp_block.append(pi3half_element)
            hhamp_block.append(sl_element)
            hhamp_block.append(pihalf_element)
            hhamp_block.append(laser_element)
            hhamp_block.append(delay_element)
            hhamp_block.append(waiting_element)
        created_blocks.append(hhamp_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((hhamp_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        block_ensemble.measurement_information['alternating'] = True
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = amp_array
        block_ensemble.measurement_information['units'] = ('V', '')
        block_ensemble.measurement_information['labels'] = ('MW amplitude', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = 2 * num_of_points
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_HHtau(self, name='hh_tau', spinlock_amp=0.1, tau_start=1e-6, tau_step=1e-6,
                       num_of_points=50):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time, increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        sl_element = self._get_mw_element(length=tau_start,
                                          increment=tau_step,
                                          amp=spinlock_amp,
                                          freq=self.microwave_frequency,
                                          phase=90)

        # Create block and append to created_blocks list
        hhtau_block = PulseBlock(name=name)
        hhtau_block.append(pihalf_element)
        hhtau_block.append(sl_element)
        hhtau_block.append(pihalf_element)
        hhtau_block.append(laser_element)
        hhtau_block.append(delay_element)
        hhtau_block.append(waiting_element)

        hhtau_block.append(pi3half_element)
        hhtau_block.append(sl_element)
        hhtau_block.append(pihalf_element)
        hhtau_block.append(laser_element)
        hhtau_block.append(delay_element)
        hhtau_block.append(waiting_element)
        created_blocks.append(hhtau_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((hhtau_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        block_ensemble.measurement_information['alternating'] = True
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Spinlock time', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = 2 * num_of_points
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_HHpol(self, name='hh_pol', spinlock_length=20.0e-6, spinlock_amp=0.1,
                       polarization_steps=50):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get steps array for measurement ticks
        steps_array = np.arange(2 * polarization_steps)

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time, increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        sl_element = self._get_mw_element(length=spinlock_length,
                                          increment=0,
                                          amp=spinlock_amp,
                                          freq=self.microwave_frequency,
                                          phase=90)

        # Create block for "up"-polarization and append to created_blocks list
        up_block = PulseBlock(name=name + '_up')
        up_block.append(pihalf_element)
        up_block.append(sl_element)
        up_block.append(pihalf_element)
        up_block.append(laser_element)
        up_block.append(delay_element)
        up_block.append(waiting_element)
        created_blocks.append(up_block)

        # Create block for "down"-polarization and append to created_blocks list
        down_block = PulseBlock(name=name + '_down')
        down_block.append(pi3half_element)
        down_block.append(sl_element)
        down_block.append(pi3half_element)
        down_block.append(laser_element)
        down_block.append(delay_element)
        down_block.append(waiting_element)
        created_blocks.append(down_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((up_block.name, polarization_steps - 1))
        block_ensemble.append((down_block.name, polarization_steps - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        block_ensemble.measurement_information['alternating'] = False
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = steps_array
        block_ensemble.measurement_information['units'] = ('#', '')
        block_ensemble.measurement_information['labels'] = ('Polarization Steps', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = 2 * polarization_steps
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_xy8_tau(self, name='xy8_tau', tau_start=0.5e-6, tau_step=0.01e-6, num_of_points=50,
                         xy8_order=4, alternating=True):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step
        # calculate "real" start length of tau due to finite pi-pulse length
        real_start_tau = max(0, tau_start - self.rabi_period / 2)

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time, increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        pix_element = self._get_mw_element(length=self.rabi_period / 2,
                                           increment=0,
                                           amp=self.microwave_amplitude,
                                           freq=self.microwave_frequency,
                                           phase=0)
        piy_element = self._get_mw_element(length=self.rabi_period / 2,
                                           increment=0,
                                           amp=self.microwave_amplitude,
                                           freq=self.microwave_frequency,
                                           phase=90)
        tauhalf_element = self._get_idle_element(length=real_start_tau / 2, increment=tau_step / 2)
        tau_element = self._get_idle_element(length=real_start_tau, increment=tau_step)

        # Create block and append to created_blocks list
        xy8_block = PulseBlock(name=name)
        xy8_block.append(pihalf_element)
        xy8_block.append(tauhalf_element)
        for n in range(xy8_order):
            xy8_block.append(pix_element)
            xy8_block.append(tau_element)
            xy8_block.append(piy_element)
            xy8_block.append(tau_element)
            xy8_block.append(pix_element)
            xy8_block.append(tau_element)
            xy8_block.append(piy_element)
            xy8_block.append(tau_element)
            xy8_block.append(piy_element)
            xy8_block.append(tau_element)
            xy8_block.append(pix_element)
            xy8_block.append(tau_element)
            xy8_block.append(piy_element)
            xy8_block.append(tau_element)
            xy8_block.append(pix_element)
            if n != xy8_order - 1:
                xy8_block.append(tau_element)
        xy8_block.append(tauhalf_element)
        xy8_block.append(pihalf_element)
        xy8_block.append(laser_element)
        xy8_block.append(delay_element)
        xy8_block.append(waiting_element)
        if alternating:
            xy8_block.append(pihalf_element)
            xy8_block.append(tauhalf_element)
            for n in range(xy8_order):
                xy8_block.append(pix_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(pix_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(pix_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(pix_element)
                if n != xy8_order - 1:
                    xy8_block.append(tau_element)
            xy8_block.append(tauhalf_element)
            xy8_block.append(pi3half_element)
            xy8_block.append(laser_element)
            xy8_block.append(delay_element)
            xy8_block.append(waiting_element)
        created_blocks.append(xy8_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((xy8_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = num_of_points * 2 if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    def generate_xy8_freq(self, name='xy8_freq', freq_start=0.1e6, freq_step=0.01e6,
                          num_of_points=50, xy8_order=4, alternating=True):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # get frequency array for measurement ticks
        freq_array = freq_start + np.arange(num_of_points) * freq_step
        # get tau array from freq array
        tau_array = 1 / (2 * freq_array)
        # calculate "real" tau array (finite pi-pulse length)
        real_tau_array = tau_array - self.rabi_period / 2
        np.clip(real_tau_array, 0, None, real_tau_array)
        # Convert back to frequency in order to account for clipped values
        freq_array = 1 / (2 * (real_tau_array + self.rabi_period / 2))

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time, increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        pihalf_element = self._get_mw_element(length=self.rabi_period / 4,
                                              increment=0,
                                              amp=self.microwave_amplitude,
                                              freq=self.microwave_frequency,
                                              phase=0)
        # Use a 180 deg phase shiftet pulse as 3pihalf pulse if microwave channel is analog
        if self.microwave_channel.startswith('a'):
            pi3half_element = self._get_mw_element(length=self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=180)
        else:
            pi3half_element = self._get_mw_element(length=3 * self.rabi_period / 4,
                                                   increment=0,
                                                   amp=self.microwave_amplitude,
                                                   freq=self.microwave_frequency,
                                                   phase=0)
        pix_element = self._get_mw_element(length=self.rabi_period / 2,
                                           increment=0,
                                           amp=self.microwave_amplitude,
                                           freq=self.microwave_frequency,
                                           phase=0)
        piy_element = self._get_mw_element(length=self.rabi_period / 2,
                                           increment=0,
                                           amp=self.microwave_amplitude,
                                           freq=self.microwave_frequency,
                                           phase=90)

        # Create block and append to created_blocks list
        xy8_block = PulseBlock(name=name)
        for ii, tau in enumerate(real_tau_array):
            tauhalf_element = self._get_idle_element(length=tau / 2, increment=0)
            tau_element = self._get_idle_element(length=tau, increment=0)
            xy8_block.append(pihalf_element)
            xy8_block.append(tauhalf_element)
            for n in range(xy8_order):
                xy8_block.append(pix_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(pix_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(pix_element)
                xy8_block.append(tau_element)
                xy8_block.append(piy_element)
                xy8_block.append(tau_element)
                xy8_block.append(pix_element)
                if n != xy8_order - 1:
                    xy8_block.append(tau_element)
            xy8_block.append(tauhalf_element)
            xy8_block.append(pihalf_element)
            xy8_block.append(laser_element)
            xy8_block.append(delay_element)
            xy8_block.append(waiting_element)
            if alternating:
                xy8_block.append(pihalf_element)
                xy8_block.append(tauhalf_element)
                for n in range(xy8_order):
                    xy8_block.append(pix_element)
                    xy8_block.append(tau_element)
                    xy8_block.append(piy_element)
                    xy8_block.append(tau_element)
                    xy8_block.append(pix_element)
                    xy8_block.append(tau_element)
                    xy8_block.append(piy_element)
                    xy8_block.append(tau_element)
                    xy8_block.append(piy_element)
                    xy8_block.append(tau_element)
                    xy8_block.append(pix_element)
                    xy8_block.append(tau_element)
                    xy8_block.append(piy_element)
                    xy8_block.append(tau_element)
                    xy8_block.append(pix_element)
                    if n != xy8_order - 1:
                        xy8_block.append(tau_element)
                xy8_block.append(tauhalf_element)
                xy8_block.append(pi3half_element)
                xy8_block.append(laser_element)
                xy8_block.append(delay_element)
                xy8_block.append(waiting_element)
        created_blocks.append(xy8_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=True)
        block_ensemble.append((xy8_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))

        # add metadata to invoke settings later on
        number_of_lasers = num_of_points * 2 if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = freq_array
        block_ensemble.measurement_information['units'] = ('Hz', '')
        block_ensemble.measurement_information['labels'] = ('Frequency', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
        
    def generate_rfrabi(self, name='rfrabi',rf_freq=100e6, tau_start=1.0e-9, tau_step=10.0e-9, num_of_points=50, abs_phase=0):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        
        # get tau array for measurement ticks
        tau_array = tau_start + np.arange(num_of_points) * tau_step     
                                          
        awgtrig_element = self._get_awgtrig_element()
        
        rf_rabi_element = self._get_rf_element(length = tau_start,
                                                increment = tau_step,
                                                amp = rf_volt,
                                                freq = rf_freq,
                                                phase = 0)

        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        laser_element = self._get_laser_gate_element(length=self.laser_length,
                                                     increment=0)
        delay_element = self._get_delay_gate_element()

        # Create block and append to created_blocks list
        rabi_block = PulseBlock(name=name)
        # rabi_block.append(awgtrig_element)
        rabi_block.append(rf_rabi_element)
        rabi_block.append(waiting_element)
        rabi_block.append(laser_element)
        rabi_block.append(delay_element)
        rabi_block.append(waiting_element)
        created_blocks.append(rabi_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((rabi_block.name, num_of_points - 1))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
        # add metadata to invoke settings later on
        block_ensemble.measurement_information['alternating'] = False
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = tau_array
        block_ensemble.measurement_information['units'] = ('s', '')
        block_ensemble.measurement_information['labels'] = ('Tau', 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = num_of_points
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # Append ensemble to created_ensembles list
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences
        
    def generate_doubleq(self, name='doubleq', tau_start = 1e-9, tau_step = 10e-9, num_of_points = 20, fixed_freq = 100e6, range_freq = 10e6, d_freq = 500e3, d_phase=10, mw_tau=20e-9, type = rfvariables.time, alternating = False):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()
        
        rf_volt = dBmtoV(self.rf_power)
        rf_period = self.rf_rabi_period
        t_rf = rf_period/2
        iq_freq = self.IQ_freq
        
        # get measurement array for measurement ticks
        vartype = type.value
        
        if vartype == 'time':
            rf_array = tau_start + np.arange(num_of_points) * tau_step
            unit = 's'
            sname = 'tau'
            
        if vartype == 'freq':
            
            num_of_points = int(2*range_freq/d_freq)
            rf_array = (fixed_freq - range_freq) + np.arange(num_of_points) * d_freq
            unit = 'Hz'
            sname = 'freq'    
            
        if vartype == 'phase':
            
            num_of_points = int(360./d_phase)
            rf_array = np.arange(num_of_points+1) * d_phase
            unit = '°'
            sname = 'phase'   

        # create the elements
        waiting_element = self._get_idle_element(length=self.wait_time,
                                                 increment=0)
        awgtrig_element = self._get_awgtrig_element()
        laser_element = self._get_laser_gate_element(length=self.laser_length, increment=0)
        delay_element = self._get_delay_gate_element()
        
        mw_tau1_element = self._get_idle_element(length = mw_tau, increment = 0)
        
        doubleq_block = PulseBlock(name=name)
        # creates phase synchronous IQ mw elements
        def mw_func(block_name=doubleq_block, length='pi2', phase_add = 0):
            pulse_dic = {'pi2': 1/4, 'pi': 1/2}
            acc_phase = np.mod((block_name.init_length_s)*iq_freq*360,360)
            
            mw_phase_element = self._get_mw_element(length=pulse_dic[length]*self.rabi_period, 
                                                    increment = 0, 
                                                    amp = self.microwave_amplitude, 
                                                    freq = iq_freq, 
                                                    phase = acc_phase + phase_add)
            return mw_phase_element
        
        # Create block and append to created_blocks list
        

        # rfsuper_block.append(awgtrig_element)
        for var in rf_array:
            

            if vartype == 'time':
                mw_tau2_element = self._get_idle_element(length = mw_tau + var, increment = 0)
            else:
                mw_tau2_element = self._get_idle_element(length = mw_tau + t_rf, increment = 0)
                
                        
            rf_element = self._get_rf_element(length=var if vartype == 'time' else t_rf,
                                                increment = 0,
                                                amp = rf_volt,
                                                freq = var if vartype == 'freq' else fixed_freq,
                                                phase = var if vartype =='phase' else 0)
                                                
            doubleq_block.append(mw_func(doubleq_block,'pi2',0))
            doubleq_block.append(mw_tau1_element)
            doubleq_block.append(rf_element)
            doubleq_block.append(mw_func(doubleq_block,'pi',0))
            doubleq_block.append(mw_tau2_element)
            doubleq_block.append(mw_func(doubleq_block,'pi2',0))
            doubleq_block.append(waiting_element)
            doubleq_block.append(laser_element)
            doubleq_block.append(delay_element)
            doubleq_block.append(waiting_element)
            if alternating:               
                doubleq_block.append(mw_func(doubleq_block,'pi2',0))
                doubleq_block.append(mw_tau2_element)
                doubleq_block.append(mw_func(doubleq_block,'pi',0))
                doubleq_block.append(mw_tau2_element)
                doubleq_block.append(mw_func(doubleq_block,'pi2',0))
                doubleq_block.append(waiting_element)
                doubleq_block.append(laser_element)
                doubleq_block.append(delay_element)
                doubleq_block.append(waiting_element)


        created_blocks.append(doubleq_block)

        # Create block ensemble
        block_ensemble = PulseBlockEnsemble(name=name, rotating_frame=False)
        block_ensemble.append((doubleq_block.name, 0))

        # Create and append sync trigger block if needed
        if self.sync_channel:
            sync_block = PulseBlock(name='sync_trigger')
            sync_block.append(self._get_sync_element())
            created_blocks.append(sync_block)
            block_ensemble.append((sync_block.name, 0))
            
        if self.awgtrig_channel:
            awgtrig_block = PulseBlock(name='awgtrig_trigger')
            awgtrig_block.append(self._get_awgtrig_element())
            created_blocks.append(awgtrig_block)
            block_ensemble.insert(0,(awgtrig_block.name, 0))    
            
        # add metadata to invoke settings later on
        number_of_lasers = 2 * num_of_points if alternating else num_of_points
        block_ensemble.measurement_information['alternating'] = alternating
        block_ensemble.measurement_information['laser_ignore_list'] = list()
        block_ensemble.measurement_information['controlled_variable'] = rf_array
        block_ensemble.measurement_information['units'] = (unit, '')
        block_ensemble.measurement_information['labels'] = (sname, 'Signal')
        block_ensemble.measurement_information['number_of_lasers'] = number_of_lasers
        block_ensemble.measurement_information['counting_length'] = self._get_ensemble_count_length(
            ensemble=block_ensemble, created_blocks=created_blocks)

        # append ensemble to created ensembles
        created_ensembles.append(block_ensemble)
        return created_blocks, created_ensembles, created_sequences

    ################################################################################################
    #                             Generation methods for sequences                                 #
    ################################################################################################
    def generate_t1_sequencing(self, name='t1_seq', tau_start=1.0e-6, tau_max=1.0e-3,
                               num_of_points=10):
        """

        """
        created_blocks = list()
        created_ensembles = list()
        created_sequences = list()

        # Get logarithmically spaced steps in multiples of tau_start.
        # Note that the number of points and the position of the last point can change here.
        k_array = np.unique(
            np.rint(np.logspace(0., np.log10(tau_max / tau_start), num_of_points)).astype(int))
        # get tau array for measurement ticks
        tau_array = k_array * tau_start

        # Create the readout PulseBlockEnsemble
        # Get necessary PulseBlockElements
        laser_element = self._get_laser_gate_element(length=self.laser_length,  increment=0)
        delay_element = self._get_delay_gate_element()
        # Create PulseBlock and append PulseBlockElements
        readout_block = PulseBlock(name='{0}_readout'.format(name))
        readout_block.append(laser_element)
        readout_block.append(delay_element)
        created_blocks.append(readout_block)
        # Create PulseBlockEnsemble and append block to it
        readout_ensemble = PulseBlockEnsemble(name='{0}_readout'.format(name), rotating_frame=False)
        readout_ensemble.append((readout_block.name, 0))
        created_ensembles.append(readout_ensemble)

        if self.sync_channel:
            # Create the last readout PulseBlockEnsemble including a sync trigger
            # Get necessary PulseBlockElements
            sync_element = self._get_sync_element()
            # Create PulseBlock and append PulseBlockElements
            sync_readout_block = PulseBlock(name='{0}_readout_sync'.format(name))
            sync_readout_block.append(laser_element)
            sync_readout_block.append(delay_element)
            sync_readout_block.append(sync_element)
            created_blocks.append(sync_readout_block)
            # Create PulseBlockEnsemble and append block to it
            sync_readout_ensemble = PulseBlockEnsemble(name='{0}_readout_sync'.format(name),
                                                       rotating_frame=False)
            sync_readout_ensemble.append((sync_readout_block.name, 0))
            created_ensembles.append(sync_readout_ensemble)

        # Create the tau/waiting PulseBlockEnsemble
        # Get tau PulseBlockElement
        tau_element = self._get_idle_element(length=tau_start, increment=0)
        # Create PulseBlock and append PulseBlockElements
        tau_block = PulseBlock(name='{0}_tau'.format(name))
        tau_block.append(tau_element)
        created_blocks.append(tau_block)
        # Create PulseBlockEnsemble and append block to it
        tau_ensemble = PulseBlockEnsemble(name='{0}_tau'.format(name), rotating_frame=False)
        tau_ensemble.append((tau_block.name, 0))
        created_ensembles.append(tau_ensemble)

        # Create the PulseSequence and append the PulseBlockEnsemble names as sequence steps
        # together with the necessary parameters.
        t1_sequence = PulseSequence(name=name, rotating_frame=False)
        count_length = 0.0
        for k in k_array:
            t1_sequence.append(tau_ensemble.name)
            t1_sequence[-1].repetitions = int(k) - 1
            count_length += k * self._get_ensemble_count_length(ensemble=tau_ensemble,
                                                                created_blocks=created_blocks)

            if self.sync_channel and k == k_array[-1]:
                t1_sequence.append(sync_readout_ensemble.name)
            else:
                t1_sequence.append(readout_ensemble.name)
            count_length += self._get_ensemble_count_length(ensemble=readout_ensemble,
                                                            created_blocks=created_blocks)
        # Make the sequence loop infinitely by setting the go_to parameter of the last sequence
        # step to the first step.
        t1_sequence[-1].go_to = 1

        # Trigger the calculation of parameters in the PulseSequence instance
        t1_sequence.refresh_parameters()

        # add metadata to invoke settings later on
        t1_sequence.measurement_information['alternating'] = False
        t1_sequence.measurement_information['laser_ignore_list'] = list()
        t1_sequence.measurement_information['controlled_variable'] = tau_array
        t1_sequence.measurement_information['units'] = ('s', '')
        t1_sequence.measurement_information['number_of_lasers'] = len(tau_array)
        t1_sequence.measurement_information['counting_length'] = count_length

        # Append PulseSequence to created_sequences list
        created_sequences.append(t1_sequence)
        return created_blocks, created_ensembles, created_sequences

