# -*- coding: utf-8 -*-
"""The Raspberry bmp thread

Server files using the http protocol

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

import logging
logger = logging.getLogger(__name__)
import os

from janitoo.thread import JNTBusThread
from janitoo.component import JNTComponent

from ina219 import INA219

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_WEB_CONTROLLER = 0x1030
COMMAND_WEB_RESOURCE = 0x1031
COMMAND_DOC_RESOURCE = 0x1032

assert(COMMAND_DESC[COMMAND_WEB_CONTROLLER] == 'COMMAND_WEB_CONTROLLER')
assert(COMMAND_DESC[COMMAND_WEB_RESOURCE] == 'COMMAND_WEB_RESOURCE')
assert(COMMAND_DESC[COMMAND_DOC_RESOURCE] == 'COMMAND_DOC_RESOURCE')
##############################################################

from janitoo_raspberry_i2c import OID

def make_ina219(**kwargs):
    return INA219Component(**kwargs)

class INA219Component(JNTComponent):
    """ A generic component for gpio """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.ina219'%OID)
        name = kwargs.pop('name', "Input")
        product_name = kwargs.pop('product_name', "INA219")
        product_type = kwargs.pop('product_type', "Cuurent and power sensor")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

        uuid="addr"
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The I2C address of the INA219 component',
            label='Addr',
            default=0x40,
        )
        uuid="shunt_ohms"
        self.values[uuid] = self.value_factory['config_float'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The shunt of the INA219 component',
            label='shunt',
            default=0.1,
        )
        uuid="max_expected_amps"
        self.values[uuid] = self.value_factory['config_float'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The max current expected for the INA219 component',
            label='Max amps',
            units='A',
            default=0.2,
        )
        uuid="voltage"
        self.values[uuid] = self.value_factory['sensor_voltage'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The voltage',
            label='Voltage',
            get_data_cb=self.read_voltage,
            units='V',
       )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value
        uuid="current"
        self.values[uuid] = self.value_factory['sensor_current'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The current',
            label='Current',
            units='mA',
            get_data_cb=self.read_current,
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value
        uuid="power"
        self.values[uuid] = self.value_factory['sensor_power'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The power',
            label='Power',
            get_data_cb=self.read_power,
            units='mW',
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value

        self.sensor = None

    def read_power(self, node_uuid, index):
        self._bus.i2c_acquire()
        try:
            return self.sensor.power()
        except Exception:
            logger.exception('[%s] - Exception when retrieving value', self.__class__.__name__)
            ret = None
        finally:
            self._bus.i2c_release()
        return ret

    def read_current(self, node_uuid, index):
        self._bus.i2c_acquire()
        try:
            return self.sensor.current()
        except Exception:
            logger.exception('[%s] - Exception when retrieving value', self.__class__.__name__)
            ret = None
        finally:
            self._bus.i2c_release()
        return ret

    def read_voltage(self, node_uuid, index):
        self._bus.i2c_acquire()
        try:
            return self.sensor.voltage()
        except Exception:
            logger.exception('[%s] - Exception when retrieving value', self.__class__.__name__)
            ret = None
        finally:
            self._bus.i2c_release()
        return ret

    def check_heartbeat(self):
        """Check that the component is 'available'

        """
        return self.sensor is not None

    def start(self, mqttc):
        """Start the bus
        """
        JNTComponent.start(self, mqttc)
        self._bus.i2c_acquire()
        try:
            self.sensor = INA219(self.values["shunt_ohms"].data, self.values["max_expected_amps"].data, log_level=logger.getEffectiveLevel())
            self.sensor.configure(self.sensor.RANGE_16V, self.sensor.GAIN_AUTO)
            self.sensor.wake()
        except Exception:
            logger.exception("[%s] - Can't start component", self.__class__.__name__)
        finally:
            self._bus.i2c_release()

    def stop(self):
        """
        """
        if self.sensor is not None:
            self.sensor.sleep()
        JNTComponent.stop(self)
        self.sensor = None
