#    Copyright 2013 IBM Corp
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

from nova import db
from nova import exception
from nova.objects import base
from nova.objects import fields
from nova.openstack.common import jsonutils


class ComputeNode(base.NovaPersistentObject, base.NovaObject):
    # Version 1.0: Initial version
    # Version 1.1: Added get_by_service_id()
    # Version 1.2: String attributes updated to support unicode
    # Version 1.3: Added stats field
    VERSION = '1.3'

    fields = {
        'id': fields.IntegerField(read_only=True),
        'service_id': fields.IntegerField(),
        'vcpus': fields.IntegerField(),
        'memory_mb': fields.IntegerField(),
        'local_gb': fields.IntegerField(),
        'vcpus_used': fields.IntegerField(),
        'memory_mb_used': fields.IntegerField(),
        'local_gb_used': fields.IntegerField(),
        'hypervisor_type': fields.StringField(),
        'hypervisor_version': fields.IntegerField(),
        'hypervisor_hostname': fields.StringField(nullable=True),
        'free_ram_mb': fields.IntegerField(nullable=True),
        'free_disk_gb': fields.IntegerField(nullable=True),
        'current_workload': fields.IntegerField(nullable=True),
        'running_vms': fields.IntegerField(nullable=True),
        'cpu_info': fields.StringField(nullable=True),
        'disk_available_least': fields.IntegerField(nullable=True),
        'metrics': fields.StringField(nullable=True),
        'stats': fields.DictOfNullableStringsField(nullable=True),
        }

    def obj_make_compatible(self, primitive, target_version):
        target_version = (int(target_version.split('.')[0]),
                          int(target_version.split('.')[1]))
        if target_version < (1, 3) and 'stats' in primitive:
            # pre 1.3 version does not have a stats field
            del primitive['stats']

    @staticmethod
    def _from_db_object(context, compute, db_compute):

        fields = set(compute.fields) - set(['stats'])
        for key in fields:
            compute[key] = db_compute[key]

        stats = db_compute['stats']
        if stats:
            compute['stats'] = jsonutils.loads(stats)

        compute._context = context
        compute.obj_reset_changes()
        return compute

    @base.remotable_classmethod
    def get_by_id(cls, context, compute_id):
        db_compute = db.compute_node_get(context, compute_id)
        return cls._from_db_object(context, cls(), db_compute)

    @base.remotable_classmethod
    def get_by_service_id(cls, context, service_id):
        db_compute = db.compute_node_get_by_service_id(context, service_id)
        return cls._from_db_object(context, cls(), db_compute)

    def _convert_stats_to_db_format(self, updates):
        stats = updates.pop('stats', None)
        if stats is not None:
            updates['stats'] = jsonutils.dumps(stats)

    @base.remotable
    def create(self, context):
        if self.obj_attr_is_set('id'):
            raise exception.ObjectActionError(action='create',
                                              reason='already created')
        updates = self.obj_get_changes()
        updates.pop('id', None)
        self._convert_stats_to_db_format(updates)

        db_compute = db.compute_node_create(context, updates)
        self._from_db_object(context, self, db_compute)

    @base.remotable
    def save(self, context, prune_stats=False):
        # NOTE(belliott) ignore prune_stats param, no longer relevant

        updates = self.obj_get_changes()
        updates.pop('id', None)
        self._convert_stats_to_db_format(updates)

        db_compute = db.compute_node_update(context, self.id, updates)
        self._from_db_object(context, self, db_compute)

    @base.remotable
    def destroy(self, context):
        db.compute_node_delete(context, self.id)

    @property
    def service(self):
        # NOTE(danms): avoid a circular import here
        if not hasattr(self, '_cached_service'):
            from nova.objects import service
            self._cached_service = service.Service.get_by_id(self._context,
                                                             self.service_id)
        return self._cached_service


class ComputeNodeList(base.ObjectListBase, base.NovaObject):
    # Version 1.0: Initial version
    #              ComputeNode <= version 1.2
    # Version 1.1 ComputeNode version 1.3
    # Version 1.2 Add get_by_service()
    VERSION = '1.2'
    fields = {
        'objects': fields.ListOfObjectsField('ComputeNode'),
        }
    child_versions = {
        '1.0': '1.2',
        # NOTE(danms): ComputeNode was at 1.2 before we added this
        '1.1': '1.3',
        '1.2': '1.3',
        }

    @base.remotable_classmethod
    def get_all(cls, context):
        db_computes = db.compute_node_get_all(context)
        return base.obj_make_list(context, ComputeNodeList(), ComputeNode,
                                  db_computes)

    @base.remotable_classmethod
    def get_by_hypervisor(cls, context, hypervisor_match):
        db_computes = db.compute_node_search_by_hypervisor(context,
                                                           hypervisor_match)
        return base.obj_make_list(context, ComputeNodeList(), ComputeNode,
                                  db_computes)

    @base.remotable_classmethod
    def _get_by_service(cls, context, service_id):
        db_service = db.service_get(context, service_id,
                                    with_compute_node=True)
        return base.obj_make_list(context, ComputeNodeList(), ComputeNode,
                                  db_service['compute_node'])

    @classmethod
    def get_by_service(cls, context, service):
        return cls._get_by_service(context, service.id)
