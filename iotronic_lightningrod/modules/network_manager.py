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
from urllib.parse import urlparse
import iotronic_lightningrod.wampmessage as WM

from oslo_log import log as logging
import subprocess
import random
import time

LOG = logging.getLogger(__name__)

Port = []

interface = ""

class NetworkManager(Module.Module):

    def __init__(self, board, session):

        super(NetworkManager, self).__init__("NetworkManager", board)
        self.url_ip = urlparse(board.wamp_config["url"])[1].split(':')[0]
        self.wagent_url = "ws://" + self.url_ip + ":8080"

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

        LOG.info("Creation of the VIF ")

        port_socat = random.randint(10000, 20000)

        i = 0
        while i < len(Port):
            if Port[i] == port_socat:
                i = 0
                port_socat = random.randint(10000, 20000)
            i += 1
        Port.insert(0, port_socat)

        LOG.debug("Creation of the VIF iotronic"+str(r_tcp_port))

        #LOG.debug('Creating virtual interface on the board')

        try:
            p2 = subprocess.Popen('socat -d -d TCP-L:' + str(port_socat) + ',bind=localhost,reuseaddr,forever,interval=10 TUN,tun-type=tap,tun-name=iotronic' + str(r_tcp_port) + ',up  '
                                  , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

#ws://192.168.17.105:8080
            p1 = subprocess.Popen(
                'wstun -r' + str(r_tcp_port) + ':localhost:' + str(port_socat) + ' '+str(self.wagent_url)
                , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            LOG.debug('Creation of the VIF succeded: iotronic')

            global interface
            interface = 'iotronic'+str(r_tcp_port)
            message = 'creation de WS tun et SOCAT'
            w_msg = WM.WampSuccess(message)

        except:

            LOG.error('Error while creating the virtual interface')
            message = 'Error while the creation'
            w_msg = WM.WampError(message)

        return w_msg.serialize()

    async def Configure_VIF(self, port_mac, ip_add, cidr):

        LOG.info("Configuration of the VIF")

        try:
            LOG.debug("Configuration of the VIF "+interface)

            p3 = subprocess.Popen("ip link set dev " + interface + " address " + str(port_mac)
                                  , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            time.sleep(1)

            p5 = subprocess.Popen("ip address add " + str(ip_add)+ "/" +str(cidr)+ " dev " + interface, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            #p5 = subprocess.Popen("ip link set " + interface + " up" , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            message = 'IP address assigned'
            w_msg = WM.WampSuccess(message)

            LOG.info("Configuration succeded")

        except Exception as e:

            LOG.error(str(e))
            message = 'Error while the configuration'
            w_msg = WM.WampError(message)

        return w_msg.serialize()

    async def Remove_VIF(self, VIF_name):

        LOG.info("Removing a VIF from the board")

        try:
            LOG.info("Removing VIF")
            LOG.debug("Removing VIF :" + str(VIF_name))
            LOG.info(VIF_name[8:])

            p1 = subprocess.Popen(
                    "kill $(ps aux | grep -e '-r'" +VIF_name[8:]+ " | awk '{print $2}')"
                    , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            p1 = subprocess.Popen(
                "kill $(ps aux | grep -e 'dhclient " + VIF_name + "' | awk '{print $2}')"
                , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            message = 'VIF removed'
            w_msg = WM.WampSuccess(message)

            LOG.info("VIF removed")
        except Exception as e:

            LOG.error(str(e))
            message = 'Error while removing the VIF'
            w_msg = WM.WampError(message)

        return w_msg.serialize()