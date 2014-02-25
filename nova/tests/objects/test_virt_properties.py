#    Copyright 2014 Red Hat, Inc.
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

from nova.objects import virt_properties
from nova import test


# NOTE(danms): With no remotable methods, we don't need to use the usual
# objects test framework
class TestVirtProperties(test.NoDBTestCase):
    def test_normal_properties(self):
        props = {'os_type': 'foo',
                 # Fill sane values for the rest here
                 }
        virtprops = virt_properties.VirtProperties.from_image_properties(
            props)
        self.assertEqual('foo', virtprops.os_type)
        # Check the rest here

    def test_property_missing(self):
        props = {'os_type': 'foo'}
        virtprops = virt_properties.VirtProperties.from_image_properties(
            props)
        self.assertEqual(None, virtprops.hw_device_id)

    def test_os_type_migrations_vmware(self):
        props = {'vmware_ostype': 'foo'}
        virtprops = virt_properties.VirtProperties.from_image_properties(
            props)
        self.assertEqual('foo', virtprops.os_type)

    def test_device_id_migrations_xenapi(self):
        props = {'xenapi_device_id': 'foo'}
        virtprops = virt_properties.VirtProperties.from_image_properties(
            props)
        self.assertEqual('foo', virtprops.hw_device_id)
