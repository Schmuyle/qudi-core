# -*- coding: utf-8 -*-
"""
A module to control the QO Raspberry Pi based H-Bridge hardware.

"""

from influxdb import InfluxDBClient

from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.process_interface import ProcessInterface


class InfluxDataClient(ProcessInterface):
    """ Retrieve live data from InfluxDB as if the measurement device was connected directly.

    Example config for copy-paste:

    influx_data_client:
        module.Class: 'influx_data_client.InfluxDataClient'
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
    port = ConfigOption('port', default=8086)
    series = ConfigOption('dataseries', missing='error')
    field = ConfigOption('field', missing='error')
    cr = ConfigOption('criterion', missing='error')

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

    def get_process_value(self):
        """ Return a measured value """
        q = 'SELECT last({0}) FROM {1} WHERE (time > now() - 10m AND {2})'.format(self.field, self.series, self.cr)
        res = self.conn.query(q)
        return list(res[('{0}'.format(self.series), None)])[0]['last']

    def get_process_unit(self):
        """ Return the unit that the value is measured in

            @return (str, str): a tuple of ('abreviation', 'full unit name')
        """
        return '°C', ' degrees Celsius'

