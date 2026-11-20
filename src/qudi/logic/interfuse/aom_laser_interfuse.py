# -*- coding: utf-8 -*-

"""
This file contains the Qudi Interfuse between a laser interface and analog output of a confocal_scanner_interface
 to control an analog driven AOM (Acousto-optic modulator).

---

"""
import numpy as np
from scipy.interpolate import interp1d

from qudi.core.connector import Connector
from qudi.core.configoption import ConfigOption
from qudi.core.module import LogicBase
from qudi.interface.simple_laser_interface import SimpleLaserInterface, ControlMode, ShutterState, LaserState


class LaserAomInterfuse(LogicBase, SimpleLaserInterface):
    """ This interfuse can be used to control the laser power after an AOM driven by an analog ouput on a confocal
    scanner hardware (the 4th analog output 'a')

    The hardware module should be configured accordingly (range 0 to 1, voltage 0 to 1V for example)

    This module needs a calibration file for the AOM. This is a 2D array with the first column the relative power
    (power over maximum power) and the second column the associated voltage.
    This data is interpolated to define the power/voltage function
    """

    # connector to the confocal scanner hardware that has analog output feature
    scanner = Connector(interface='ConfocalScannerInterface')

    # max power the AOM can deliver (in Watt)
    _max_power = ConfigOption('max_power', missing='error')

    # calibration file which can be read by numpy loadtxt with two columns :
    # relative power (0.0 to 1.0), voltage (V)
    _calibration_file = ConfigOption('calibration_file', missing='error')
    _power_to_voltage = None
    _power = 0
    _laser_on = LaserState.OFF

    def on_activate(self):
        """ Activate module.
        """
        self._scanner = self.scanner()
        if 'a' not in self._scanner.get_scanner_axes():
            self.log.error('Scanner does not have an "a" axe configured. Can not use it to control an AOM.')

        calibration_data = np.loadtxt(self._calibration_file)
        power_rel_to_voltage = interp1d(calibration_data[:, 0], calibration_data[:, 1])
        self._power_to_voltage = lambda power: power_rel_to_voltage(power/self._max_power)

    def on_deactivate(self):
        """ Deactivate module.
        """
        pass

    def get_power_range(self):
        """ Return optical power range

            @return (float, float): power range
        """
        return 0, self._max_power

    def get_power(self):
        """ Return laser power

            @return float: Laser power in watts
        """
        return self._power

    def get_power_setpoint(self):
        """ Return optical power setpoint.

            @return float: power setpoint in watts
        """
        return self._power

    def set_power(self, power):
        """ Set power setpoint.

            @param float power: power setpoint

            @return float: actual new power setpoint
        """
        mini, maxi = self.get_power_range()
        if mini <= power <= maxi:
            self._power = power
            if self._laser_on == LaserState.ON:
                voltage = self._power_to_voltage(power)
            else:
                voltage = self._power_to_voltage(0)
            if self._scanner.module_state() == 'locked':
                self.log.error('Output device of the voltage for the AOM is locked, cannot set voltage.')
            else:
                if self._scanner.scanner_set_position(a=voltage) < 0:
                    self.log.error('Could not set the voltage for the AOM because the scanner failed.')
        return self._power

    def get_current_unit(self):
        """ Get unit for laser current.

            @return str: unit
        """
        return '%'

    def get_current_range(self):
        """ Get laser current range.

            @return (float, float): laser current range
        """
        return 0, 100

    def get_current(self):
        """ Get current laser current

            @return float: laser current in current curent units
        """
        return 0

    def get_current_setpoint(self):
        """ Get laser curent setpoint

            @return float: laser current setpoint
        """
        return 0

    def set_current(self, current):
        """ Set laser current setpoint

            @prarm float current: desired laser current setpoint

            @return float: actual laser current setpoint
        """
        return 0

    def allowed_control_modes(self):
        """ Get supported control modes

            @return list(): list of supported ControlMode
        """
        return [ControlMode.POWER]

    def get_control_mode(self):
        """ Get the currently active control mode

            @return ControlMode: active control mode
        """
        return ControlMode.POWER

    def set_control_mode(self, control_mode):
        """ Set the active control mode

            @param ControlMode control_mode: desired control mode

            @return ControlMode: actual active ControlMode
        """
        return ControlMode.POWER

    def on(self):
        """ Turn on laser.

            @return LaserState: actual laser state
        """
        return self.set_laser_state(LaserState.ON)

    def off(self):
        """ Turn off laser.

            @return LaserState: actual laser state
        """
        return self.set_laser_state(LaserState.OFF)

    def get_laser_state(self):
        """ Get laser state

            @return LaserState: actual laser state
        """
        return self._laser_on

    def set_laser_state(self, state):
        """ Set laser state.

            @param LaserState state: desired laser state

            @return LaserState: actual laser state
        """
        self._laser_on = state
        self.set_power(self._power)

    def get_shutter_state(self):
        """ Get laser shutter state

            @return ShutterState: actual laser shutter state
        """
        return ShutterState.NOSHUTTER

    def set_shutter_state(self, state):
        """ Set laser shutter state.

            @param ShutterState state: desired laser shutter state

            @return ShutterState: actual laser shutter state
        """
        return ShutterState.NOSHUTTER

    def get_temperatures(self):
        """ Get all available temperatures.

            @return dict: dict of temperature namce and value in degrees Celsius
        """
        return {}

    def set_temperatures(self, temps):
        """ Set temperatures for lasers with tunable temperatures.

            @return {}: empty dict, dummy not a tunable laser
        """
        return {}

    def get_temperature_setpoints(self):
        """ Get temperature setpoints.

            @return dict: temperature setpoints for temperature tunable lasers
        """
        return {}

    def get_extra_info(self):
        """ Multiple lines of dignostic information

            @return str: much laser, very useful
        """
        return ""

    def set_max_power(self, maxi):
        """ Function to redefine the max power if the value has changed """
        self._max_power = maxi

