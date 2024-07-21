import copy

from spaceone.core.service import *
from spaceone.core import utils
# from spaceone.inventory.model.cloud_service_model import CloudService
from spaceone.inventory.model.performance_model import Performance
from spaceone.inventory.manager.performance_manager import PerformanceManager
from spaceone.inventory.manager.cloud_service_tag_manager import CloudServiceTagManager
from spaceone.inventory.manager.region_manager import RegionManager
from spaceone.inventory.manager.identity_manager import IdentityManager
from spaceone.inventory.manager.resource_group_manager import ResourceGroupManager
from spaceone.inventory.manager.change_history_manager import ChangeHistoryManager
from spaceone.inventory.manager.collection_state_manager import CollectionStateManager
from spaceone.inventory.manager.note_manager import NoteManager
from spaceone.inventory.error import *

_KEYWORD_FILTER = ['performance_id', 'name', 'ip_addresses', 'cloud_service_group', 'cloud_service_type', 'resource_id']


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class PerformanceService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.performance_mgr: PerformanceManager = self.locator.get_manager('PerformanceManager')
        self.region_mgr: RegionManager = self.locator.get_manager('RegionManager')
        self.identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
        self.tag_mgr: CloudServiceTagManager = self.locator.get_manager('CloudServiceTagManager')
        self.collector_id = self.transaction.get_meta('collector_id')
        self.job_id = self.transaction.get_meta('job_id')
        self.plugin_id = self.transaction.get_meta('plugin_id')
        self.service_account_id = self.transaction.get_meta('secret.service_account_id')

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'authorization.require_project_id': True
    })
    @check_required(['cloud_service_type', 'cloud_service_group', 'provider', 'data', 'domain_id'])
    def create(self, params):
        """
        Args:
            params (dict): {
                    'cloud_service_type': 'str',
                    'cloud_service_group': 'str',
                    'provider': 'str',
                    'name': 'str',
                    'account': 'str',
                    'instance_type': 'str',
                    'instance_size': 'float',
                    'ip_addresses': 'list',
                    'data': 'dict',
                    'metadata': 'dict',
                    'reference': 'dict',
                    'tags': 'list or dict',
                    'region_code': 'str',
                    'project_id': 'str',
                    'domain_id': 'str'
                }

        Returns:
            cloud_service_vo (object)

        """

        # ch_mgr: ChangeHistoryManager = self.locator.get_manager('ChangeHistoryManager')

        domain_id = params['domain_id']
        project_id = params.get('project_id')
        secret_project_id = self.transaction.get_meta('secret.project_id')

        params['provider'] = params.get('provider', self.transaction.get_meta('secret.provider'))

        if params['provider'] is None:
            raise ERROR_REQUIRED_PARAMETER(key='provider')

        if 'tags' in params:
            tag_type = self._get_tag_type_from_meta()
            params['tags'] = self._create_tag(params, tag_type)

        if 'instance_size' in params:
            if not isinstance(params['instance_size'], float):
                raise ERROR_INVALID_PARAMETER_TYPE(key='instance_size', type='float')

        if project_id:
            self.identity_mgr.get_project(project_id, domain_id)
        elif secret_project_id:
            params['project_id'] = secret_project_id

        params['ref_cloud_service_type'] = self._make_performance_type_key(params)

        if 'region_code' in params:
            params['ref_region'] = self._make_region_key(params, params['provider'])

        params['collection_info'] = self._get_collection_info()

        if 'metadata' in params:
            params['metadata'] = self._change_metadata_path(params['metadata'])

        performance_vo = self.performance_mgr.create_performance(params)

        # Create New History
        # ch_mgr.add_new_history(performance_vo, params)

        # Create Collection State
        # state_mgr: CollectionStateManager = self.locator.get_manager('CollectionStateManager')
        # state_mgr.create_collection_state(performance_vo.performance_id, 'inventory.Performance', domain_id)

        # Create New CloudServiceTag Resources
        if 'tags' in params:
            self.tag_mgr.create_performance_tags_by_new_tags(performance_vo, params['tags'])

        return performance_vo

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['performance_id', 'domain_id'])
    def update(self, params):
        """
        Args:
            params (dict): {
                    'performance_id': 'str',
                    'name': 'str',
                    'account': 'str',
                    'instance_type': 'str',
                    'instance_size': 'float',
                    'ip_addresses': 'list',
                    'data': 'dict',
                    'metadata': 'dict',
                    'reference': 'dict',
                    'tags': 'list or dict',
                    'region_code': 'str',
                    'project_id': 'str',
                    'domain_id': 'str',
                    'release_project': 'bool',
                    'release_region': 'bool'
                }

        Returns:
            performance_vo (object)

        """

        # ch_mgr: ChangeHistoryManager = self.locator.get_manager('ChangeHistoryManager')

        project_id = params.get('project_id')
        secret_project_id = self.transaction.get_meta('secret.project_id')

        performance_id = params['performance_id']
        domain_id = params['domain_id']
        # release_region = params.get('release_region', False)
        # release_project = params.get('release_project', False)
        # new_tags = None
        # tag_type = self._get_tag_type_from_meta()

        # if 'ip_addresses' in params and params['ip_addresses'] is None:
        #     del params['ip_addresses']

        performance_vo: Performance = self.performance_mgr.get_performance(performance_id, domain_id)
        old_performance_data = dict(performance_vo.to_dict())

        # if 'tags' in params:
        #     new_tags = self._create_tag(params, tag_type)
        #
        #     new_tags_dict: dict = self._change_tags_to_dict(new_tags)
        #     old_tags_dict: dict = self._change_tags_to_dict(old_performance_data['tags'], tag_type=tag_type)
        #
        #     if new_tags_dict != old_tags_dict:
        #         params['tags'] = self._merge_tags(new_tags, old_performance_data['tags'], tag_type=tag_type)
        #     elif 'tags' in params:
        #         del params['tags']

        # params['collection_info'] = self._get_collection_info(old_performance_data.get('collection_info', {}))

        # if 'metadata' in params:
        #     params['metadata'] = self._change_metadata_path(params['metadata'])

        params = self.performance_mgr.merge_data(params, old_performance_data)

        performance_vo = self.performance_mgr.update_performance_by_vo(params, performance_vo)

        # Create New CloudServiceTag Resources
        # if 'tags' in params:
        #     self.tag_mgr.delete_tags_by_tag_type(domain_id, performance_id, tag_type)
        #     self.tag_mgr.create_performance_tags_by_new_tags(performance_vo, new_tags)

        # Create Update History
        # ch_mgr.add_update_history(performance_vo, params, old_performance_data)

        # Update Collection History
        state_mgr: CollectionStateManager = self.locator.get_manager('CollectionStateManager')
        state_vo = state_mgr.get_collection_state(performance_id, domain_id)
        if state_vo:
            state_mgr.reset_collection_state(state_vo)
        else:
            state_mgr.create_collection_state(performance_id, 'inventory.Performance', domain_id)

        if 'project_id' in params:
            note_mgr: NoteManager = self.locator.get_manager('NoteManager')

            # Update Project ID from Notes
            note_vos = note_mgr.filter_notes(performance_id=performance_id, domain_id=domain_id)
            note_vos.update({'project_id': params['project_id']})

        return performance_vo

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['performance_id', 'domain_id'])
    def delete(self, params):
        """
        Args:
            params (dict): {
                    'performance_id': 'str',
                    'domain_id': 'str'
                }

        Returns:
            None

        """

        # ch_mgr: ChangeHistoryManager = self.locator.get_manager('ChangeHistoryManager')

        performance_id = params['performance_id']
        domain_id = params['domain_id']

        performance_vo: Performance = self.performance_mgr.get_performance(performance_id, domain_id)

        self.performance_mgr.delete_performance_by_vo(performance_vo)

        # Create Update History
        # ch_mgr.add_delete_history(performance_vo)

        # Cascade Delete Collection State
        state_mgr: CollectionStateManager = self.locator.get_manager('CollectionStateManager')
        state_mgr.delete_collection_state_by_resource_id(performance_id, domain_id)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['performance_id', 'domain_id'])
    def get(self, params):
        """
        Args:
            params (dict): {
                    'performance_id': 'str',
                    'domain_id': 'str',
                    'only': 'list'
                }

        Returns:
            cloud_service_vo (object)

        """

        return self.performance_mgr.get_performance(params['performance_id'], params['domain_id'],
                                                    only=params.get('only'))

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['domain_id'])
    @append_query_filter(['performance_id', 'name', 'state', 'account', 'instance_type', 'cloud_service_type',
                          'cloud_service_group', 'provider', 'region_code', 'resource_group_id', 'project_id',
                          'project_group_id', 'domain_id', 'user_projects', 'ip_address'])
    @append_keyword_filter(_KEYWORD_FILTER)
    def list(self, params):
        """
        Args:
            params (dict): {
                    'performance_id': 'str',
                    'name': 'str',
                    'state': 'str',
                    'account': 'str',
                    'instance_type': 'str',
                    'cloud_service_type': 'str',
                    'cloud_service_group': 'str',
                    'provider': 'str',
                    'region_code': 'str',
                    'resource_group_id': 'str',
                    'project_id': 'str',
                    'project_group_id': 'str',
                    'domain_id': 'str',
                    'query': 'dict (spaceone.api.core.v1.Query)',
                    'user_projects': 'list', // from meta
                    'ip_address': 'str'
                }

        Returns:
            results (list)
            total_count (int)

        """

        query = params.get('query', {})
        query = self._append_resource_group_filter(query, params['domain_id'])
        query = self._change_project_group_filter(query, params['domain_id'])
        query = self._change_tags_filter(query, params['domain_id'])
        query = self._change_only_tags(query)

        return self.performance_mgr.list_performances(query)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['resource_group_id', 'domain_id', 'user_projects'])
    @append_keyword_filter(_KEYWORD_FILTER)
    def stat(self, params):
        """
        Args:
            params (dict): {
                'resource_group_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'user_projects': 'list', // from meta
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        query = self._append_resource_group_filter(query, params['domain_id'])
        query = self._change_project_group_filter(query, params['domain_id'])

        allow_delete_state = params.get('allow_delete_state', False)
        return self.performance_mgr.stat_performances(query, allow_delete_state)

    def _append_resource_group_filter(self, query, domain_id):
        change_filter = []

        for condition in query.get('filter', []):
            key = condition.get('k', condition.get('key'))
            value = condition.get('v', condition.get('value'))
            operator = condition.get('o', condition.get('operator'))

            if key == 'resource_group_id':
                performance_ids = None

                if operator in ['not', 'not_contain', 'not_in', 'not_contain_in']:
                    resource_group_operator = 'not_in'
                else:
                    resource_group_operator = 'in'

                if operator in ['eq', 'not', 'contain', 'not_contain']:
                    performance_ids = self._ger_performance_ids_from_resource_group_id(value, domain_id)
                elif operator in ['in', 'not_in', 'contain_in', 'not_contain_in'] and isinstance(value, list):
                    performance_ids = []
                    for v in value:
                        performance_ids += self._ger_performance_ids_from_resource_group_id(v, domain_id)

                if performance_ids is not None:
                    change_filter.append({
                        'k': 'performance_id',
                        'v': list(set(performance_ids)),
                        'o': resource_group_operator
                    })

            else:
                change_filter.append(condition)

        query['filter'] = change_filter
        return query

    def _ger_performance_ids_from_resource_group_id(self, resource_group_id, domain_id):
        resource_type = 'inventory.Performance'
        rg_mgr: ResourceGroupManager = self.locator.get_manager('ResourceGroupManager')

        resource_group_filters = rg_mgr.get_resource_group_filter(resource_group_id, resource_type, domain_id,
                                                                  _KEYWORD_FILTER)
        performance_ids = []
        for resource_group_query in resource_group_filters:
            resource_group_query['distinct'] = 'performance_id'
            result = self.performance_mgr.stat_performances(resource_group_query)
            performance_ids += result.get('results', [])
        return performance_ids

    def _change_project_group_filter(self, query, domain_id):
        change_filter = []

        project_group_query = {
            'filter': [],
            'only': ['project_group_id']
        }

        for condition in query.get('filter', []):
            key = condition.get('key', condition.get('k'))
            value = condition.get('value', condition.get('v'))
            operator = condition.get('operator', condition.get('o'))

            if not all([key, operator]):
                raise ERROR_DB_QUERY(reason='filter condition should have key, value and operator.')

            if key == 'project_group_id':
                project_group_query['filter'].append(condition)
            else:
                change_filter.append(condition)

        if len(project_group_query['filter']) > 0:
            identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
            response = identity_mgr.list_project_groups(project_group_query, domain_id)
            project_group_ids = []
            project_ids = []
            for project_group_info in response.get('results', []):
                project_group_ids.append(project_group_info['project_group_id'])

            for project_group_id in project_group_ids:
                response = identity_mgr.list_projects_in_project_group(project_group_id, domain_id, True,
                                                                       {'only': ['project_id']})
                for project_info in response.get('results', []):
                    if project_info['project_id'] not in project_ids:
                        project_ids.append(project_info['project_id'])

            change_filter.append({'k': 'project_id', 'v': project_ids, 'o': 'in'})

        query['filter'] = change_filter
        return query

    @staticmethod
    def _change_only_tags(query):
        change_only_tags = []
        if 'only' in query:

            for key in query.get('only', []):
                if key.startswith('tags.'):
                    change_only_tags.append('tags')
                else:
                    change_only_tags.append(key)
            query['only'] = change_only_tags
        return query

    @staticmethod
    def _make_performance_type_key(resource_data):
        return f'{resource_data["domain_id"]}.{resource_data["provider"]}.' \
               f'{resource_data["cloud_service_group"]}.{resource_data["cloud_service_type"]}'

    @staticmethod
    def _make_region_key(resource_data, provider):
        return f'{resource_data["domain_id"]}.{provider}.{resource_data["region_code"]}'

    def _change_metadata_path(self, metadata):
        plugin_id = self.transaction.get_meta('plugin_id')

        if plugin_id:
            metadata = {
                plugin_id: copy.deepcopy(metadata)
            }
        else:
            metadata = {
                'MANUAL': copy.deepcopy(metadata)
            }

        return metadata

    def _get_collection_info(self, collection_info=None):
        if collection_info is None:
            collection_info = {}

        collector_id = self.transaction.get_meta('collector_id')
        secret_id = self.transaction.get_meta('secret.secret_id')
        service_account_id = self.transaction.get_meta('secret.service_account_id')

        all_collectors = collection_info.get('collectors', [])
        all_service_accounts = collection_info.get('service_accounts', [])
        all_secrets = collection_info.get('secrets', [])

        if collector_id:
            all_collectors.append(collector_id)

        if service_account_id:
            all_service_accounts.append(service_account_id)

        if secret_id:
            all_secrets.append(secret_id)

        return {
            'collectors': sorted(list(set(all_collectors))),
            'service_accounts': sorted(list(set(all_service_accounts))),
            'secrets': sorted(list(set(all_secrets))),
        }

    @staticmethod
    def _merge_tags(new_tags, old_tags, tag_type):
        tags = []
        for tag in old_tags:
            if tag['type'] != tag_type:
                tags.append({
                    'key': tag['key'],
                    'value': tag['value'],
                    'type': tag['type'],
                    'provider': tag['provider']
                })
        for new_tag in new_tags:
            tags.append(new_tag)

        from operator import itemgetter
        return sorted(tags, key=itemgetter('type'))

    @staticmethod
    def _create_tag(params: dict, tag_type: str):
        if isinstance(params['tags'], list):
            dot_tags = utils.tags_to_dict(params['tags'])

        if isinstance(params['tags'], dict):
            dot_tags = params['tags']

        tags = []
        for key, value in dot_tags.items():
            tags.append({
                'key': key,
                'value': value,
                'type': tag_type,
                'provider': params.get('provider')
            })
        return tags

    @staticmethod
    def _change_tags_to_dict(tags: list, tag_type=None) -> dict:
        tags_dict = {}
        for tag in tags:
            if tag_type and tag_type == tag['type']:
                tags_dict[tag['key']] = tag['value']
            else:
                tags_dict[tag['key']] = tag['value']

        return tags_dict

    def _get_tag_type_from_meta(self):
        if self.collector_id and self.job_id and self.service_account_id and self.plugin_id:
            tag_type = 'MANAGED'
        else:
            tag_type = 'CUSTOM'
        return tag_type

    def _change_tags_filter(self, query, domain_id):
        change_filter = []

        for condition in query.get('filter', []):
            key = condition.get('k', condition.get('key'))
            value = condition.get('v', condition.get('value'))
            operator = condition.get('o', condition.get('operator'))

            if key.startswith('tags.'):
                tag_key = key.replace('tags.', '')

                if operator in ['not', 'not_contain', 'not_in', 'not_contain_in']:
                    if operator == 'not':
                        operator = 'eq'
                    elif operator == 'not_contain':
                        operator = 'contain'
                    elif operator == 'not_in':
                        operator = 'in'
                    elif operator == 'not_contain_in':
                        operator = 'contain_in'

                cloud_svc_ids = self._ger_performance_ids_from_tag(tag_key, value, operator, domain_id)

                if cloud_svc_ids is not None:
                    change_filter.append({
                        'k': 'performance_id',
                        'v': list(set(cloud_svc_ids)),
                        'o': 'in'
                    })
            else:
                change_filter.append(condition)

        query['filter'] = change_filter
        return query

    def _ger_performance_ids_from_tag(self, key, value, operator, domain_id):
        cst_mgr: CloudServiceTagManager = self.locator.get_manager('CloudServiceTagManager')

        performance_ids = []
        query = {
            'filter': self._create_cloud_svc_tag_filter(key, value, operator, domain_id),
            'only': ['performance_id']
        }

        cst_vos, total_count = cst_mgr.list_cloud_svc_tags(query)
        for cst_vo in cst_vos:
            performance_ids.append(cst_vo.performance_id)

        return performance_ids

    @staticmethod
    def _create_cloud_svc_tag_filter(key, value, operator, domain_id):
        return [{
            'k': 'key',
            'v': key,
            'o': 'eq'
        }, {
            'k': 'value',
            'v': value,
            'o': operator
        }, {
            'k': 'domain_id',
            'v': domain_id,
            'o': 'eq'
        }]
