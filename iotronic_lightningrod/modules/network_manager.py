# Copyright 2017 MDSLAB - University of Messina
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import asyncio
from iotronic_lightningrod.modules import Module
from iotronic_lightningrod.modules import utils

import iotronic_lightningrod.wampmessage as WM

from oslo_config import cfg
from oslo_log import log as logging
import subprocess
import random
import time
LOG = logging.getLogger(__name__)

Port = []

class NetworkManager(Module.Module):

    def __init__(self, board, session):

        super(NetworkManager, self).__init__("NetworkManager", board)

    def finalize(self):
        pass

    def restore(self):
        pass

    async def test_function(self):
        import random
        s = random.uniform(0.5, 1.5)
        await asyncio.sleep(s)
        result = "DEVICE test result: TEST!"
        LOG.info(result)
        return result

    async def add(self, x, y):
        c = x + y
        LOG.info("DEVICE add result: " + str(c))
        return c

    async def Create_VIF(self, r_tcp_port):
        port_socat = random.randint(10000, 20000)
        LOG.info(str(port_socat))
        i = 0
        while i < len(Port):
            if Port[i] == port_socat:
                i = 0
                port_socat = random.randint(10000, 20000)
            i += 1
        Port.insert(0, port_socat)
        LOG.info(str(port_socat))

        LOG.debug('Creating virtual interface on the board')
        try:

            p2 = subprocess.Popen(
                'socat -d -d TCP-L:' + str(port_socat) + ',bind=localhost,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=iot3,up &'
                    , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            time.sleep(7)

            p1 = subprocess.Popen(
                'wstun -r' + str(r_tcp_port) + ':localhost:' + str(port_socat) + ' ws://192.168.17.105:8080 &'
                , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #return 1
        except:
            LOG.error('Error while creating the virtual interface')
            return 0

