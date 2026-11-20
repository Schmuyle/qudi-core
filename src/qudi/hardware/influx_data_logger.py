# -*- coding: utf-8 -*-
"""
A module to control the QO Raspberry Pi based H-Bridge hardware.

"""

from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.data_logger_interface import DataLoggerInterface

from influxdb import InfluxDBClient

class InfluxLogger(DataLoggerInterface):
    """ Log instrument values to InfluxDB.

    Example config for copy-paste:

    influx_data_logger:
        module.Class: 'influx_data_logger.InfluxLogger'
        user: 'client_user'
        password: 'client_password'
        dbname: 'db_name'
        host: 'localhost'
        port: 8086
        dataseries: 'data_series_name'
        field: 'field_name'
        criterion: 'criterion_name'

    """

    user = ConfigOption('user', missing='error')
    pw = ConfigOption('password', missing='error')
    dbname = ConfigOption('dbname', missing='error')
    host = ConfigOption('host', missing='error')
    port = ConfigOption('port', 8086)
    series = ConfigOption('dataseries', missing='error')
    field = ConfigOption('field', missing='error')
    cr = ConfigOption('criterion', missing='error')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_channels = {}

    def on_activate(self):
        """ Activate module.
        """
        self.connect_db()

    def on_deactivate(self):
        """ Deactivate module.
        """
        del self.conn

    def connect_db(self):
        """ Connect to Influx database """
        self.conn = InfluxDBClient(self.host, self.port, self.user, self.pw, self.dbname)

    def get_log_channels(self):
        """ Get number of logging channels

            @return int: number of channels
        """
        return self.log_channels

    def set_log_channels(self, channelspec):
        """ Set number of logging channels.

            @param channelspec dict: name, spec
        """
        for name, spec in channelspec.items():
            if spec is None and name in self.log_channels:
                self.log_channels.pop(name)
            elif name in self.log_channels:
                pass
            else:
                pass
                if True:
                    pass

    def log_to_channel(self, channel, values):
        """ Log values to a specific channel.

            @param channel str: channel name
            @param values list: data to be logged
        """
        if channel in self.log_channels.keys() and len(values) == len(self.log_channels[channel][values]):
            conn.write_points(format_data(channel, values, channeltags))

    def format_data(self, channel_name, values, tags):
        """ Format data according to InfluxDB JSON API.

            @param channel_name str: channel name
            @param values list: data
            @param tags list(str): list of tags
        """
        return [{
             'measurement': channel_name,
             'fields': values,
             'tags': tags
            }]

