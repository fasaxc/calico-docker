# Copyright 2015 Metaswitch Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from tests.st.test_base import TestBase
from tests.st.utils.docker_host import DockerHost
from tests.st.utils.workload import NET_NONE


class TestNoOrchestratorSingleHost(TestBase):
    def test_single_host(self):
        """
        Test mainline functionality without using an orchestrator plugin
        """
        with DockerHost('host', dind=False) as host:
            # TODO ipv6 too
            host.calicoctl("profile add TEST_GROUP")

            # Create a workload on each host.
            workload1 = host.create_workload("workload1")
            workload2 = host.create_workload("workload2")

            # TODO - find a better home for this assertion
            # # Attempt to configure the nodes with the same profiles.  This will
            # # fail since we didn't use the driver to create the nodes.
            # with self.assertRaises(CalledProcessError):
            #     host.calicoctl("profile TEST_GROUP member add %s" % workload1)
            # with self.assertRaises(CalledProcessError):
            #     host.calicoctl("profile TEST_GROUP member add %s" % workload2)

            # Add the nodes to Calico networking.
            host.calicoctl("container add %s 192.168.1.1" % workload1)
            host.calicoctl("container add %s 192.168.1.2" % workload2)

            # Now add the profiles - one using set and one using append
            host.calicoctl("container %s profile set TEST_GROUP" % workload1)
            host.calicoctl("container %s profile append TEST_GROUP" % workload2)

            # TODO - assert on output of endpoint show and endpoint profile
            # show commands.

            # Check it works
            workload1.assert_can_ping("192.168.1.2", retries=3)
            workload2.assert_can_ping("192.168.1.1", retries=3)

            # Test the teardown commands
            host.calicoctl("profile remove TEST_GROUP")
            host.calicoctl("container remove %s" % workload1)
            host.calicoctl("container remove %s" % workload2)
            host.calicoctl("pool remove 192.168.0.0/16")
            host.calicoctl("node stop")
