import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)


class RegionConfigManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cloud_service_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='identity')

    def list_available_region(self, params, query):
        # domain_id = 'domain-7025b8c87722'
        # params = {
        #     'service_account_id': 'global',
        #     'domain_id': 'domain-7025b8c87722',
        #     'provider': 'aws',
        #     'project_id': 'default'
        # }
        # query = {
        #     'filter': [
        #         {'k': 'service_account_id', 'v': params['service_account_id'], 'o': 'eq'},
        #         {'k': 'domain_id', 'v': params['domain_id'], 'o': 'eq'},
        #         {'k': 'provider', 'v': params['provider'], 'o': 'eq'},
        #         {'k': 'project_id', 'v': params['project_id'], 'o': 'eq'},
        #     ]
        # }

        # for test ---------------------
        # params = {
        #     'options': {
        #         'service_account_id': 'global',
        #         'domain_id': 'domain-7025b8c87722',
        #         'provider': 'aws',
        #         'project_id': 'default'
        #     }
        # }

        option_data = params
        _LOGGER.debug(f'option_data data ---------------------------')
        _LOGGER.debug(option_data)

        domain_id = option_data['domain_id']
        project_id = option_data['project_id']
        provider = option_data['provider']
        service_account_id = option_data['service_account_id']
        _LOGGER.debug(f'domain_id data {service_account_id}')
        _LOGGER.debug(f'project_id data {project_id}')
        _LOGGER.debug(f'provider data {provider}')
        _LOGGER.debug(f'service_account_id data {service_account_id}')
        query = {
            'filter': [
                {'k': 'service_account_id', 'v': service_account_id, 'o': 'eq'},
                {'k': 'domain_id', 'v': domain_id, 'o': 'eq'},
                {'k': 'provider', 'v': provider, 'o': 'eq'},
                {'k': 'project_id', 'v': project_id, 'o': 'eq'},
            ]
        }
        _LOGGER.debug(f'self.cloud_service_connector.config info {self.cloud_service_connector.config}')
        _LOGGER.debug(f'self.cloud_service_connector.client.api_resources info {self.cloud_service_connector.client.api_resources}')
        return self.cloud_service_connector.dispatch('ServiceAccount.list_available_region', {'domain_id': domain_id, 'query': query})