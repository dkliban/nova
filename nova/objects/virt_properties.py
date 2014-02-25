#    Copyright 2013 Red Hat, Inc
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

from nova.image import glance
from nova.objects import base
from nova.objects import fields
from nova import utils


class VirtProperties(base.NovaObject):
    VERSION = '1.0'

    fields = {
        'hw_architecture': fields.StringField(nullable=True),
        'hw_cdrom_bus': fields.StringField(nullable=True),
        'hw_disk_bus': fields.StringField(nullable=True),
        'hw_floppy_bus': fields.StringField(nullable=True),
        'hw_qemu_guest_agent': fields.StringField(nullable=True),
        'hw_rng': fields.StringField(nullable=True),
        'hw_scsi_model': fields.StringField(nullable=True),
        'hw_video_model': fields.StringField(nullable=True),
        'hw_video_ram': fields.StringField(nullable=True),
        'hw_vif_model': fields.StringField(nullable=True),
        'hw_watchdog_action': fields.StringField(nullable=True),
        'hw_os_command_line': fields.StringField(nullable=True),
        'hw_owner_id': fields.StringField(nullable=True),
        'hw_adaptertype': fields.StringField(nullable=True),
        'hw_disktype': fields.StringField(nullable=True),
        # Probably need to change this
        'hw_image_version': fields.IntegerField(nullable=True),
        'hw_linked_clone': fields.StringField(nullable=True),
        'os_type': fields.StringField(nullable=True),
        'hw_auto_disk_config': fields.BooleanField(nullable=True),
        'hw_ipxe_boot': fields.StringField(nullable=True),
        'hw_device_id': fields.StringField(nullable=True),
        'img_compression_level': fields.StringField(nullable=True),
        'img_use_agent': fields.StringField(nullable=True),
        'os_skip_agent_inject_ssh': fields.StringField(nullable=True),
        'os_skip_agent_inject_files_at_boot': fields.StringField(
            nullable=True),
        'cache_in_nova': fields.StringField(nullable=True),
        'vm_mode': fields.StringField(nullable=True),
        'bittorrent': fields.StringField(nullable=True)
    }

    property_map = {
        'hw_architecture': ['architecture'],
        'hw_os_command_line': ['os_command_line'],
        'hw_owner_id': ['owner_id'],
        'hw_adaptertype': ['vmware_adaptertype'],
        'hw_disktype': ['vmware_disktype'],
        'hw_image_version': ['vmware_image_version'],
        'hw_linked_clone': ['vmware_linked_clone'],
        'os_type': ['vmware_ostype', 'os_type'],
        'hw_auto_disk_config': ['auto_disk_config'],
        'hw_ipxe_boot': ['ipxe_boot'],
        'hw_device_id': ['xenapi_device_id'],
        'img_compression_level': ['xenapi_image_compression_level'],
        'img_use_agent': ['xenapi_use_agent'],
        'os_skip_agent_inject_ssh': ['xenapi_skip_agent_inject_ssh'],
        'os_skip_agent_inject_files_at_boot':
            ['xenapi_skip_agent_inject_files_at_boot'],
        'cache_in_nova': ['cache_in_nova'],
        'vm_mode': ['vm_mode'],
        'bittorrent': ['bittorrent']
        }

    def __init__(self, *args, **kwargs):
        super(VirtProperties, self).__init__(*args, **kwargs)
        for key in self.fields:
            if key not in kwargs:
                self[key] = None

    def _migrate_old_property(self, image_props, key):
        for old_key in self.property_map.get(key, []):
            if old_key in image_props:
                # NOTE(danms): This needs data migration
                return image_props[old_key]
        return None

    def _from_image_properties(self, image_props):
        for key in self.fields:
            if key in image_props:
                self[key] = image_props[key]
            else:
                self[key] = self._migrate_old_property(image_props, key)

    def iteritems(self):
        for key in self.fields:
            if self[key] is not None:
                print "Yielding %s,%s" % (key, self[key])
                yield (key, self[key])
            else:
                print "Nothing for %s" % key

    @classmethod
    def from_image_properties(cls, image_props):
        obj = cls()
        obj._from_image_properties(image_props)
        return obj

    @classmethod
    def from_image_metadata(cls, image_meta):
        return cls.from_image_properties(image_meta.get('properties', {}))

    @classmethod
    def from_instance(cls, instance):
        sysmeta = utils.instance_sys_meta(instance)
        properties = {}
        for key in [p for p in sysmeta.keys() if p.startswith('image_')]:
            image_key = key.split('_', 1)[1]
            properties[image_key] = sysmeta[key]
        return cls.from_image_properties(properties)

    @classmethod
    def get_by_image_id(cls, image_id):
        (image_service, image_id) = glance.get_remote_image_service(
                context, image_id)
        image_meta = image_service.show(context, image_id)
        obj = cls()
        obj.from_image_props(image_meta.get('properties', {}))
        return obj
