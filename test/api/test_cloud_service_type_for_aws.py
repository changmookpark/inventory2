import os
import unittest
import pprint
from google.protobuf.json_format import MessageToDict

from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner
import logging
_LOGGER = logging.getLogger(__name__)

class TestCloudServiceType(unittest.TestCase):
    # config = utils.load_yaml_from_file(os.environ.get('SPACEONE_CONFIG_FILE', './config.yml'))

    pp = pprint.PrettyPrinter(indent=4)
    identity_v1 = None
    inventory_v1 = None
    owner_id = None
    owner_pw = None
    owner_token = None

    @classmethod
    def setUpClass(cls):
        print(f'setUpClass start ---------')
        super(TestCloudServiceType, cls).setUpClass()
        # endpoints = cls.config.get('ENDPOINTS', {})
        # print('endpoints : ', endpoints)
        # cls.identity_v1 = pygrpc.client(endpoint=endpoints.get('identity', {}).get('v1'), version='v1', ssl_enabled=True)
        # cls.inventory_v1 = pygrpc.client(endpoint=endpoints.get('inventory', {}).get('v1'), version='v1')
        # psy aws
        # cls.identity_v1 = pygrpc.client(endpoint='10.101.147.165:50051')
        # ds server aws (inventory 10.107.195.94)
        # 해당 IP확인 - $ kubectl get pod -n spaceone -o wide
        #cls.identity_v1 = pygrpc.client(endpoint='172.17.0.19:50051')

        #-----------------------------
        # localhost
        cls.identity_v1 = pygrpc.client(endpoint='identity:50051')
        cls.inventory_v1 = pygrpc.client(endpoint='inventory:50056')
        #cls.inventory_v1 = pygrpc.client(endpoint='localhost:50051')

        _LOGGER.info(f'\n\n\ncloud test start ------------')

        cls._create_domain()
        cls._create_domain_owner()
        cls._issue_owner_token()

    @classmethod
    def tearDownClass(cls):
        print(f'tearDownClass start ---------')
        super(TestCloudServiceType, cls).tearDownClass()
        cls.identity_v1.DomainOwner.delete(
            {
                'domain_id': cls.domain.domain_id,
                'owner_id': cls.owner_id
            }, metadata=(('token', cls.owner_token),)
        )

        cls.identity_v1.Domain.delete(
            {
                'domain_id': cls.domain.domain_id
            }, metadata=(('token', cls.owner_token),)
        )

    @classmethod
    def _create_domain(cls):
        name = utils.random_string()
        params = {
            'name': name
        }
        cls.domain = cls.identity_v1.Domain.create(params)

    @classmethod
    def _create_domain_owner(cls):
        cls.owner_id = utils.random_string() + '@mz.co.kr'
        cls.owner_pw = utils.generate_password()

        params = {
            'owner_id': cls.owner_id,
            'password': cls.owner_pw,
            'domain_id': cls.domain.domain_id
        }

        owner = cls.identity_v1.DomainOwner.create(
            params
        )
        cls.domain_owner = owner

    @classmethod
    def _issue_owner_token(cls):
        token_param = {
            'user_type': 'DOMAIN_OWNER',
            'user_id': cls.owner_id,
            'credentials': {
                'password': cls.owner_pw
            },
            'domain_id': cls.domain.domain_id
        }

        issue_token = cls.identity_v1.Token.issue(token_param)
        cls.owner_token = issue_token.access_token

    def setUp(self):
        print(f'setUp start ---------')
        self.cloud_service_type = None
        self.cloud_service_types = []

    def tearDown(self):
        print(f'tearDown start ---------')
        for cloud_svc_type in self.cloud_service_types:
            self.inventory_v1.CloudServiceType.delete(
                {'cloud_service_type_id': cloud_svc_type.cloud_service_type_id,
                 'domain_id': self.domain.domain_id},
                metadata=(('token', self.owner_token),)
            )

    def _print_data(self, message, description=None):
        print(f'description data print')

        print()
        if description:
            print(f'[ {description} ]')

        print(f'MessageToDict')
        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

    def test_create_cloud_service_type(self, name=None, provider=None, group=None):
        """ Create Cloud Service Type
        """

        if name is None:
            name = utils.random_string()

        if provider is None:
            provider = utils.random_string()

        if group is None:
            group = utils.random_string()

        print(f'test 1 ---------------')

        params = {
            'name': name,
            'provider': provider,
            'group': group,
            'resource_type': 'inventory.Server',
            'is_primary': True,
            'is_major': True,
            'metadata': {
                'view': {
                    'search': [{
                        'name': 'Provider',
                        'key': 'provider'
                    }, {
                        'name': 'Project',
                        'key': 'project'
                    }]
                }
            },
            'domain_id': self.domain.domain_id
        }

        print(f'test 2------')
        # print(self.inventory_v1.CloudServiceType)
        self.cloud_service_type = self.inventory_v1.CloudServiceType.create(
            params, metadata=(('token', self.owner_token),)
        )
        print(f'test 3 self.cloud_service_type raw')
        print(f'test 4 print data')
        self._print_data(self.cloud_service_type, 'test_create_cloud_service_type')

        self.cloud_service_types.append(self.cloud_service_type)
        self.assertEqual(self.cloud_service_type.name, name)



if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)

