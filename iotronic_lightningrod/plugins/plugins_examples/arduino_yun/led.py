# Copyright 2017 MDSLAB - University of Messina
#    All Rights Reserved.
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

from iotronic_lightningrod.plugins import Plugin
from iotronic_lightningrod.plugins import pluginApis as API

from oslo_log import log as logging
LOG = logging.getLogger(__name__)

# User imports
device = API.getBoardGpio()


class Worker(Plugin.Plugin):

    def __init__(self, uuid, name, q_result, params=None):
        super(Worker, self).__init__(uuid, name, q_result, params)

    def run(self):
        LOG.info("Input parameters: " + str(self.params))

        device._setGPIOs("D13", "out", str(self.params['pin']))

        LOG.info("Plugin " + self.name + " process completed!")
        self.q_result.put("Led D13: " + str(self.params['pin']))
