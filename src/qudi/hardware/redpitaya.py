import asyncio
import numpy as np
import pyrpl.async_utils as pyrpl_async_utils
import concurrent.futures
from qudi.core.module import Base
from qudi.core.configoption import ConfigOption

from qudi.interface.simple_redpitaya_interface import SimpleRedPitayaInterface

try:
    from pyrpl import Pyrpl
except ImportError:
    Pyrpl = None

class RedPitaya(SimpleRedPitayaInterface):
    """RedPitaya hardware control module."""
    _modclass = 'redpitaya'
    _modtype = 'hardware'

    # Configuration options
    hostname = ConfigOption('hostname', '192.168.1.100', missing='warn')  # RedPitaya hostname or IP address
    config = ConfigOption('config', 'global_config', missing='warn')  # Pitaya config file to use, default to global config.
    
    def on_activate(self):
        """ Activate module.  """
        if Pyrpl is None:
            self.log.error('Pyrpl not installed. Cannot activate RedPitaya module.')
            return False

        try:
            self.pyrpl = Pyrpl(hostname=self.hostname, config=self.config, gui=False) # Initialize Pyrpl connection to RedPitaya
            self.rp = self.pyrpl.rp
            
            # Select IQ channels
            self.iq0 = self.rp.iq0
            self.iq1 = self.rp.iq1
            self.pid0 = self.rp.pid0
            self.pid1 = self.rp.pid1

            quadrature_factor = 1  #Leave as 1 incase I want to see this later...
            bandwidth = [3E5, 4E5] # 2 Lowpass filters on demodulated signal, use to remove 2f component from signal

            self.iq0.setup(output_direct='off',
                           quadrature_factor=quadrature_factor,
                           bandwidth = bandwidth,
                           output_signal='output_direct')
            self.iq1.setup(output_direct='off',
                           quadrature_factor=quadrature_factor,
                           bandwidth = bandwidth,
                           output_signal='output_direct')

            # Pyrpl currently has no D gain register; its derivative stage is disabled.
            self.pid0.setup(input='iq0', output_direct='out1', p=0, i=0)
            self.pid1.setup(input='iq1', output_direct='out2', p=0, i=0)

            self.log.info('RedPitaya activated on {}'.format(self.hostname))
            return True
        except Exception as e:
            self.log.exception('Failed to connect to RedPitaya: {}'.format(e))
            return False

    def on_deactivate(self):
        """ Deactivate module."""
        try:
            if hasattr(self, 'pyrpl'):
                del self.pyrpl
                self.log.info('RedPitaya deactivated')
        except Exception as e:
            self.log.exception('Error closing RedPitaya: {}'.format(e))


# ------------------ Get IQ channel 0 values ------------------

    def get_iq0_frequency(self):
        """ Get IQ0 demodulator frequency in Hz. """
        try:
            return float(self.iq0.frequency)
        except Exception as e:
            self.log.exception('Failed to get IQ0 frequency: {}'.format(e))
            return None
    
    def get_iq0_phase(self):
        """ Get IQ0 demodulator phase in degrees. """
        try:
            return float(self.iq0.phase)
        except Exception as e:
            self.log.exception('Failed to get IQ0 phase: {}'.format(e))
            return None        
    
    def get_iq0_amplitude(self):
        """ Get IQ demodulator amplitude. """
        try:
            return float(self.iq0.amplitude)
        except Exception as e:
            self.log.exception('Failed to get IQ0 amplitude: {}'.format(e))
            return None

    def get_iq0_gain(self):
        """ Get IQ0 demodulator gain. """
        try:
            return float(self.iq0.gain)
        except Exception as e:
            self.log.exception('Failed to get IQ0 gain: {}'.format(e))
            return None

    # def get_iq0_bandwidth(self):
    #     """ Get IQ0 demodulator bandwidth. """
    #     try:
    #         return float(self.iq0.bandwidth)
    #     except Exception as e:
    #         self.log.exception('Failed to get IQ0 bandwidth: {}'.format(e))
    #         return None
    
    def get_iq0_acbandwidth(self):
        """ Get IQ0 demodulator AC bandwidth. """
        try:
            return float(self.iq0.acbandwidth)
        except Exception as e:
            self.log.exception('Failed to get IQ0 AC bandwidth: {}'.format(e))
            return None
        
    def get_iq0_input(self):
        """ Get IQ0 input channel. """
        try:
            return str(self.iq0.input)
        except Exception as e:
            self.log.exception('Failed to get IQ0 input: {}'.format(e))
            return None
        
    def get_iq0_output_signal(self):
        """ Get IQ0 output signal. """
        try:
            return str(self.iq0.output_signal)
        except Exception as e:
            self.log.exception('Failed to get IQ0 output signal: {}'.format(e))
            return None

    def get_iq0_modulation_at_2f(self):
        """ Get whether IQ0 modulation at 2f is enabled. """
        try:
            value = getattr(self.iq0, 'modulation_at_2f', None)
            if isinstance(value, str):
                return value.lower() == 'on'
            return bool(value)
        except Exception as e:
            self.log.exception('Failed to get IQ0 modulation_at_2f: {}'.format(e))
            return None

    def get_iq0_filter_frequency(self):
        """ Get the IQ0 bandpass filter frequency. """
        try:
            bandwidth = getattr(self.iq0, 'bandwidth', None)
            if isinstance(bandwidth, (list, tuple)) and len(bandwidth) >= 1:
                return float(bandwidth[0])
            return None
        except Exception as e:
            self.log.exception('Failed to get IQ0 filter frequency: {}'.format(e))
            return None

    def get_iq0_pid_p(self):
        """Get the proportional gain of the PID connected to IQ0."""
        try:
            return float(self.pid0.p)
        except Exception as e:
            self.log.exception('Failed to get IQ0 PID proportional gain: {}'.format(e))
            return None

# ------------------ Set IQ channel 0 values ------------------

    def set_iq0_frequency(self, frequency):
        """ Set IQ0 demodulator frequency in Hz. """
        try:
            self.iq0.frequency = float(frequency)
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 frequency: {}'.format(e))
            return False
        
    def set_iq0_phase(self, phase):
        """ Set IQ0 demodulator phase in degrees. """
        try:
            self.iq0.phase = float(phase)
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 phase: {}'.format(e))
            return False     

    def set_iq0_amplitude(self, amplitude):
        """ Set IQ0 demodulator amplitude. """
        try:
            self.iq0.amplitude = float(amplitude)
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 amplitude: {}'.format(e))
            return False

    def set_iq0_gain(self, gain):
        """ Set IQ0 demodulator gain. """
        try:
            self.iq0.gain = float(gain)
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 gain: {}'.format(e))
            return False        

    # def set_iq0_bandwidth(self, bandwidth):
    #     """ Set IQ0 demodulator bandwidth. """
    #     try:
    #         self.iq0.bandwidth = float(bandwidth)
    #         return True
    #     except Exception as e:
    #         self.log.exception('Failed to set IQ0 bandwidth: {}'.format(e))
    #         return False
        
    def set_iq0_acbandwidth(self, acbandwidth):
        """ Set IQ0 demodulator AC bandwidth. """
        try:
            self.iq0.acbandwidth = float(acbandwidth)
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 AC bandwidth: {}'.format(e))
            return False
        
    def set_iq0_input(self, input_channel):
        """ Set IQ0 input channel. """
        try:
            self.iq0.input = str(input_channel)
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 input: {}'.format(e))
            return False
    
    def set_iq0_output_signal(self, output_signal):
        """ Set IQ0 output signal. """
        try:
            self.iq0.output_signal = str(output_signal)
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 output signal: {}'.format(e))
            return False
    def set_iq1_modulation_at_2f(self, enabled):
        """ Set whether IQ1 modulation at 2f is enabled. """
        try:
            self.iq1.modulation_at_2f = 'on' if bool(enabled) else 'off'
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ1 modulation_at_2f: {}'.format(e))
            return False

    def set_iq1_filter_frequency(self, frequency):
        """ Set the IQ1 bandpass filter frequency for both filters. """
        try:
            self.iq1.bandwidth = (float(frequency), float(frequency))
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ1 filter frequency: {}'.format(e))
            return False
    def set_iq0_modulation_at_2f(self, enabled):
        """ Set whether IQ0 modulation at 2f is enabled. """
        try:
            self.iq0.modulation_at_2f = 'on' if bool(enabled) else 'off'
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 modulation_at_2f: {}'.format(e))
            return False

    def set_iq0_filter_frequency(self, frequency):
        """ Set the IQ0 bandpass filter frequency for both filters. """
        try:
            self.iq0.bandwidth = (float(frequency), float(frequency))
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 filter frequency: {}'.format(e))
            return False

    def set_iq0_pid_p(self, gain):
        """Set the proportional gain of the PID connected to IQ0."""
        try:
            self.pid0.p = float(gain)
            self.pid0.i = 0
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ0 PID proportional gain: {}'.format(e))
            return False

    #Add

# ------------------ Read IQ channel 1 values ------------------

    def get_iq1_frequency(self):
        """ Get iq1 demodulator frequency in Hz. """
        try:
            return float(self.iq1.frequency)
        except Exception as e:
            self.log.exception('Failed to get iq1 frequency: {}'.format(e))
            return None
    
    def get_iq1_phase(self):
        """ Get iq1 demodulator phase in degrees. """
        try:
            return float(self.iq1.phase)
        except Exception as e:
            self.log.exception('Failed to get iq1 phase: {}'.format(e))
            return None        
    
    def get_iq1_amplitude(self):
        """ Get IQ demodulator amplitude. """
        try:
            return float(self.iq1.amplitude)
        except Exception as e:
            self.log.exception('Failed to get iq1 amplitude: {}'.format(e))
            return None

    def get_iq1_gain(self):
        """ Get iq1 demodulator gain. """
        try:
            return float(self.iq1.gain)
        except Exception as e:
            self.log.exception('Failed to get iq1 gain: {}'.format(e))
            return None

    # def get_iq1_bandwidth(self):
    #     """ Get iq1 demodulator bandwidth. """
    #     try:
    #         return float(self.iq1.bandwidth)
    #     except Exception as e:
    #         self.log.exception('Failed to get iq1 bandwidth: {}'.format(e))
    #         return None
    
    def get_iq1_acbandwidth(self):
        """ Get iq1 demodulator AC bandwidth. """
        try:
            return float(self.iq1.acbandwidth)
        except Exception as e:
            self.log.exception('Failed to get iq1 AC bandwidth: {}'.format(e))
            return None
        
    def get_iq1_input(self):
        """ Get iq1 input channel. """
        try:
            return str(self.iq1.input)
        except Exception as e:
            self.log.exception('Failed to get iq1 input: {}'.format(e))
            return None
        
    def get_iq1_output_signal(self):
        """ Get iq1 output signal. """
        try:
            return str(self.iq1.output_signal)
        except Exception as e:
            self.log.exception('Failed to get iq1 output signal: {}'.format(e))
            return None
    def get_iq1_modulation_at_2f(self):
        """ Get whether IQ1 modulation at 2f is enabled. """
        try:
            value = getattr(self.iq1, 'modulation_at_2f', None)
            if isinstance(value, str):
                return value.lower() == 'on'
            return bool(value)
        except Exception as e:
            self.log.exception('Failed to get IQ1 modulation_at_2f: {}'.format(e))
            return None

    def get_iq1_filter_frequency(self):
        """ Get the IQ1 bandpass filter frequency. """
        try:
            bandwidth = getattr(self.iq1, 'bandwidth', None)
            if isinstance(bandwidth, (list, tuple)) and len(bandwidth) >= 1:
                return float(bandwidth[0])
            return None
        except Exception as e:
            self.log.exception('Failed to get IQ1 filter frequency: {}'.format(e))
            return None

    def get_iq1_pid_p(self):
        """Get the proportional gain of the PID connected to IQ1."""
        try:
            return float(self.pid1.p)
        except Exception as e:
            self.log.exception('Failed to get IQ1 PID proportional gain: {}'.format(e))
            return None

# ------------------ Set IQ channel 1 values ------------------

    def set_iq1_frequency(self, frequency):
        """ Set iq1 demodulator frequency in Hz. """
        try:
            self.iq1.frequency = float(frequency)
            return True
        except Exception as e:
            self.log.exception('Failed to set iq1 frequency: {}'.format(e))
            return False
        
    def set_iq1_phase(self, phase):
        """ Set iq1 demodulator phase in degrees. """
        try:
            self.iq1.phase = float(phase)
            return True
        except Exception as e:
            self.log.exception('Failed to set iq1 phase: {}'.format(e))
            return False     

    def set_iq1_amplitude(self, amplitude):
        """ Set iq1 demodulator amplitude. """
        try:
            self.iq1.amplitude = float(amplitude)
            return True
        except Exception as e:
            self.log.exception('Failed to set iq1 amplitude: {}'.format(e))
            return False

    def set_iq1_gain(self, gain):
        """ Set iq1 demodulator gain. """
        try:
            self.iq1.gain = float(gain)
            return True
        except Exception as e:
            self.log.exception('Failed to set iq1 gain: {}'.format(e))
            return False        

    # def set_iq1_bandwidth(self, bandwidth):
    #     """ Set iq1 demodulator bandwidth. """
    #     try:
    #         self.iq1.bandwidth = float(bandwidth)
    #         return True
    #     except Exception as e:
    #         self.log.exception('Failed to set iq1 bandwidth: {}'.format(e))
    #         return False
        
    def set_iq1_acbandwidth(self, acbandwidth):
        """ Set iq1 demodulator AC bandwidth. """
        try:
            self.iq1.acbandwidth = float(acbandwidth)
            return True
        except Exception as e:
            self.log.exception('Failed to set iq1 AC bandwidth: {}'.format(e))
            return False
        
    def set_iq1_input(self, input_channel):
        """ Set iq1 input channel. """
        try:
            self.iq1.input = str(input_channel)
            return True
        except Exception as e:
            self.log.exception('Failed to set iq1 input: {}'.format(e))
            return False
    
    def set_iq1_output_signal(self, output_signal):
        """ Set iq1 output signal. """
        try:
            self.iq1.output_signal = str(output_signal)
            return True
        except Exception as e:
            self.log.exception('Failed to set iq1 output signal: {}'.format(e))
            return False

    def set_iq1_pid_p(self, gain):
        """Set the proportional gain of the PID connected to IQ1."""
        try:
            self.pid1.p = float(gain)
            self.pid1.i = 0
            return True
        except Exception as e:
            self.log.exception('Failed to set IQ1 PID proportional gain: {}'.format(e))
            return False

# ------------------ Get Scope control methods ------------------

    def get_scope_duration(self):
        """ Get scope acquisition window duration in seconds. """
        try:
            return float(self.rp.scope.duration)
        except Exception as e:
            self.log.exception('Failed to get scope duration: {}'.format(e))
            return None

    def get_scope_input1(self):
        """ Get scope channel 1 input source. """
        try:
            return str(self.rp.scope.input1)
        except Exception as e:
            self.log.exception('Failed to get scope input1: {}'.format(e))
            return None

    def get_scope_input2(self):
        """ Get scope channel 2 input source. """
        try:
            return str(self.rp.scope.input2)
        except Exception as e:
            self.log.exception('Failed to get scope input2: {}'.format(e))
            return None

    def get_scope_input2(self):
        """ Get scope channel 2 input source. """
        try:
            return str(self.rp.scope.input2)
        except Exception as e:
            self.log.exception('Failed to get scope input2: {}'.format(e))
            return None

    def get_scope_trigger_sources(self):
        """Get supported scope trigger sources."""
        try:
            sources = list(getattr(self.rp.scope, 'trigger_sources', []))
            # Filter out ASG outputs which should not be available as trigger sources
            filtered = [s for s in sources if not (isinstance(s, str) and s.startswith('asg'))]
            return filtered
        except Exception as e:
            self.log.exception('Failed to get scope trigger sources: {}'.format(e))
            return None

    def get_scope_trigger_source(self):
        """Get currently selected scope trigger source."""
        try:
            return str(self.rp.scope.trigger_source)
        except Exception as e:
            self.log.exception('Failed to get scope trigger source: {}'.format(e))
            return None

    def get_scope_threshold(self):
        """Get current scope trigger threshold."""
        try:
            return float(self.rp.scope.threshold)
        except Exception as e:
            self.log.exception('Failed to get scope trigger threshold: {}'.format(e))
            return None

    def get_scope_data(self):
        """Get current scope data [ch1, ch2].

        Run the pyrpl blocking call inside a worker thread that creates
        and uses its own asyncio event loop. This isolates pyrpl's
        asyncio helpers from any running qasync/main loop and avoids
        CancelledError / stack overflow on Windows.
        """

        def _worker_call():
            loop = None
            created_loop = False
            old_loop = None
            old_ensure_future = None
            try:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    created_loop = True
                except Exception:
                    loop = None

                old_loop = getattr(pyrpl_async_utils, 'LOOP', None)
                old_ensure_future = getattr(pyrpl_async_utils, 'ensure_future', None)

                if loop is not None:
                    pyrpl_async_utils.LOOP = loop

                    def _ensure_future(coro):
                        return asyncio.ensure_future(coro, loop=loop)

                    pyrpl_async_utils.ensure_future = _ensure_future

                # call the blocking API (which internally uses async helpers)
                data = self.rp.scope.single()
                return np.asarray(data)
            finally:
                # restore pyrpl async utils state
                if old_ensure_future is not None:
                    pyrpl_async_utils.ensure_future = old_ensure_future
                else:
                    try:
                        delattr(pyrpl_async_utils, 'ensure_future')
                    except Exception:
                        pass

                if old_loop is not None:
                    pyrpl_async_utils.LOOP = old_loop
                else:
                    if hasattr(pyrpl_async_utils, 'LOOP'):
                        try:
                            delattr(pyrpl_async_utils, 'LOOP')
                        except Exception:
                            pass

                if created_loop and loop is not None:
                    try:
                        asyncio.set_event_loop(None)
                    except Exception:
                        pass
                    try:
                        loop.close()
                    except Exception:
                        pass

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as exc:
                fut = exc.submit(_worker_call)
                data = fut.result()
                return data
        except Exception as e:
            self.log.exception('Failed to get scope data in worker thread: {}'.format(e))
            return None

# ------------------ Set Scope control methods ------------------
  

    def set_scope_duration(self, duration):
        """ Set scope acquisition window duration in seconds. """
        try:
            self.rp.scope.duration = float(duration)
            return True
        except Exception as e:
            self.log.exception('Failed to set scope duration: {}'.format(e))
            return False

    def set_scope_input1(self, input_source):
        """ Set scope channel 1 input source. """
        try:
            self.rp.scope.input1 = str(input_source)
            return True
        except Exception as e:
            self.log.exception('Failed to set scope input1: {}'.format(e))
            return False

    def set_scope_input2(self, input_source):
        """ Set scope channel 2 input source. """
        try:
            self.rp.scope.input2 = str(input_source)
            return True
        except Exception as e:
            self.log.exception('Failed to set scope input2: {}'.format(e))
            return False

    def set_scope_trigger_source(self, trigger_source):
        """Set scope trigger source."""
        try:
            # Use the scope.setup API to properly configure the trigger
            ts = str(trigger_source)
            try:
                # prefer setup which applies the full configuration
                self.rp.scope.setup(trigger_source=ts)
            except Exception:
                # fall back to setting the attribute directly if setup not available
                self.rp.scope.trigger_source = ts
            return True
        except Exception as e:
            self.log.exception('Failed to set scope trigger source: {}'.format(e))
            return False

    def set_scope_threshold(self, threshold):
        """Set scope trigger threshold."""
        try:
            self.rp.scope.threshold = float(threshold)
            return True
        except Exception as e:
            self.log.exception('Failed to set scope threshold: {}'.format(e))
            return False

    def apply_scope_setup(self, **kwargs):
        """Apply scope configuration atomically using rp.scope.setup().
        
        Supported kwargs: duration, input1, input2, trigger_source, threshold, 
        """
        try:
            # Filter and map kwargs to pyrpl scope.setup parameters
            setup_kwargs = {}
            if 'duration' in kwargs:
                setup_kwargs['duration'] = float(kwargs['duration'])
            if 'input1' in kwargs:
                setup_kwargs['input1'] = str(kwargs['input1'])
            if 'input2' in kwargs:
                setup_kwargs['input2'] = str(kwargs['input2'])
            if 'trigger_source' in kwargs:
                setup_kwargs['trigger_source'] = str(kwargs['trigger_source'])
            if 'threshold' in kwargs:
                setup_kwargs['threshold'] = float(kwargs['threshold'])
            
            self.rp.scope.setup(**setup_kwargs)
            return True
        except Exception as e:
            self.log.exception('Failed to apply scope setup: {}'.format(e))
            return False

# ---------- Add ASG calls here for AC and DC ASG calls -------