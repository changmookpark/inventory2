import unittest
import pprint
from mongoengine import connect, disconnect
from spaceone.core import config, utils
from spaceone.core.transaction import Transaction
from spaceone.core.unittest.result import print_data

from spaceone.inventory.model import CloudService
from spaceone.inventory.service import CloudServiceService, CloudServiceTagService, CloudServiceTypeService
from spaceone.core.unittest.runner import RichTestRunner
import logging
_LOGGER = logging.getLogger(__name__)

class TestCloudServiceTagService(unittest.TestCase):
    pp = pprint.PrettyPrinter(indent=4)

    @classmethod
    def setUpClass(cls):
        _LOGGER.info(f'\n\n\ncloud servie test start ------------')
        config.init_conf(package='spaceone.inventory')
        # config.set_service_config()
        # config.set_global(MOCK_MODE=True)
        # connect('test', host='mongomock://localhost')
        config.set_service_config()

        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'inventory',
            'resource': 'CloudService'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all data_sources')
        # cloud_service_vos = CloudService.objects.filter()
        # cloud_service_vos.delete()

    def test_create_cloud_service_contain_list_of_dict_tags_by_collector(self):
        params = {
            'cloud_service_type': 'Instance',
            'provider': 'aws',
            'data': {},
            'tags': [
                {'key': 'a.b.c',
                 'value': 'd'},
                {'key': 'b.c.d',
                 'value': 'e'}
            ],
            "region_code": "ap-northeast-2",
            'cloud_service_group': 'EC2',
            'domain_id': utils.generate_id('domain'),

        }

        metadata = {
            'verb': 'create',
            'collector_id': utils.generate_id('collector'),
            'job_id': utils.generate_id('job'),
            'plugin_id': utils.generate_id('plugin'),
            'secret.service_account_id': utils.generate_id('sa'),
        }

        # cloud_svc_service = CloudServiceService(metadata=metadata)
        # cloud_svc_vo = cloud_svc_service.create(params.copy())
        # print(f'cloud_svc_vo {cloud_svc_vo}')

        params['domain_id'] = 'domain-9dae4c8bc793'
        cloud_svc_tag_service = CloudServiceTagService(metadata=metadata)
        cloud_svc_tag_vos = cloud_svc_tag_service.list({'domain_id': params['domain_id']})
        # print(f'cloud_svc_tag_vos {cloud_svc_tag_vos}')
        # print_data(cloud_svc_vo.to_dict(), 'test_create_cloud_service')
        for tag in cloud_svc_tag_vos[0]:
            print(f'\ttag {tag}')
            print_data(tag.to_dict(), 'test_cloud_service_tag')

        #----------------------------------
        # type test
        # ----------------------------------
        domain_id = 'domain-9dae4c8bc793'
        cloud_svc_type_service = CloudServiceTypeService(metadata=metadata)
        #cloud_svc_type_vos = cloud_svc_type_service.list({'domain_id': params['domain_id']})
        cloud_svc_type_vos = cloud_svc_type_service.list({'domain_id': domain_id})
        print(f'cloud_svc_type_vos {cloud_svc_type_vos}')
        for typ in cloud_svc_type_vos[0]:
            print(f'type {typ}')

        print(f'pprint ----------')
        self.pp.pprint(cloud_svc_type_vos)

        # self.assertIsInstance(cloud_svc_vo, CloudService)
        # self.assertEqual(params['cloud_service_type'], cloud_svc_vo.cloud_service_type)
        # self.assertEqual(cloud_svc_vo.tags[0].provider, params['provider'])
        # self.assertEqual(cloud_svc_vo.tags[0].type, 'MANAGED')



if __name__ == '__main__':
#    unittest.main()
    unittest.main(testRunner=RichTestRunner)
