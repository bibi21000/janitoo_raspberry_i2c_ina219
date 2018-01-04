# -*- coding: utf-8 -*-

"""Unittests for Janitoo-Roomba Server.
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

import warnings
warnings.filterwarnings("ignore")

import sys, os
import time, datetime
import unittest
import threading
import logging
from pkg_resources import iter_entry_points

from janitoo_nosetests.server import JNTTServer, JNTTServerCommon
from janitoo_nosetests.thread import JNTTThread, JNTTThreadCommon
from janitoo_nosetests.component import JNTTComponent, JNTTComponentCommon

from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC

class TestINA219Component(JNTTComponent, JNTTComponentCommon):
    """Test the component
    """
    component_name = "rpii2c.ina219"


class TestINA219Thread(JNTTThreadRun, JNTTThreadRunCommon):
    """Test the datarrd thread
    """
    thread_name = "rpii2c"
    conf_file = "tests/data/janitoo_raspberry_i2c_ina219.conf"

    def test_101_check_values(self):
        self.skipRasperryTest()
        self.wait_for_nodeman()
        time.sleep(5)
        self.assertValueOnBus('ina1','power')
        self.assertValueOnBus('ina1','current')
        self.assertValueOnBus('ina1','voltage')

    def test_102_get_values(self):
        self.onlyRasperryTest()
        self.wait_for_nodeman()
        time.sleep(5)
        power = self.thread.bus.nodeman.find_value('ina1','power').data
        print(power)
        current = self.thread.bus.nodeman.find_value('ina1','current').data
        print(current)
        voltage = self.thread.bus.nodeman.find_value('ina1','voltage').data
        print(voltage)
        self.assertNotEqual(power, None)
        self.assertNotEqual(current, None)
        self.assertNotEqual(voltage, None)
        self.assertNotInLogfile('^ERROR ')
        
