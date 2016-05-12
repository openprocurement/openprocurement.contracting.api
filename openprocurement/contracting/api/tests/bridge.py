# -*- coding: utf-8 -*-

import unittest
from openprocurement.contracting.api import databridge
from mock import Mock
from munch import Munch
import gevent
from gevent.queue import Queue

test_tender_data_with_contracts = [
    Munch({'status': 'complete',
           'id': '9591a5d52be641f08026330ddb197cd8',
           'owner': 'quintagroup.ua',
           'contracts': [Munch({'status': 'active',
                                'awardID': '6b55fa3b869f4c0ca48b1bd7228b1f70',
                                'id': 'f56f3a7f0d92226585c5565dd594d66f',
                                'contractID': 'UA-2016-04-15-000195-b-b1'})]}),
    Munch({'status': 'complete',
           'owner': 'netcast.com.ua',
           'id': 'c094dc11a6444d2db8000hcf06dd827b',
           'contracts': [Munch({'status': 'active',
                                'awardID': '6b55fa8b869f4c0ca48b2bd7228b1f70',
                                'id': 'f56f3a7f0d92426585c5565dd594d66f',
                                'contractID': 'UA-2016-04-15-000195-b-b1'})]}),
    Munch({'status': 'complete',
           'owner': 'prom.ua',
           'id': 'af9f3e04669d43d5abb07d37fb8007a7',
           'lots': [Munch({'status': 'complete',
                           'title': u'послуги з повірки лічильників теплової енергії Katra SKM-1U',
                           'id': 'e6903f5202eb488aa1e7fda08e0c8ff5'})],
           'contracts': [Munch({'status': 'non-active',
                                'awardID': '6b55fa8b869f4c0ca48b2bd7228b1f70',
                                'id': 'f56f4a7f0d92426588c4165dd594d66f',
                                'contractID': 'UA-2016-04-25-000195-b-b1'})]}),
    Munch({'status': 'complete',
           'id': '9591a5d53be641f08026330ddb197cd8'
           }),
    Munch({'status': 'active.awarded',
           'lots': [Munch({'status': 'complete',
                           'title': u'акумуляторна батарея 6 ст-90',
                           'id': '4a562178b4c1468aa97c501f02576cc9'
                           }),
                    Munch({'status': 'active',
                           'title': u'батарея акумуляторна  6 ст-130',
                           'id': '2e7bab34b24246dd8693d6da4e6a3e4e'}
                          )],
           'id': '701a78db57814a33ad10dbb74519ae07'
           })
]

test_tenders_data = [
    Munch({'status': 'active.awarded',
           'lots': [Munch({'status': 'active',
                           'title': u'Банани',
                           'id': '438a5b08bf9f4c1c973a87fd34ba5a2d'})],
           'id': 'e340de0f2b984eada30c0433a40591e0'}),
    Munch({'status': 'complete',
           'id': '9591a5d52be641f08026330ddb197cd8',
           }),
    Munch({'status': 'complete',
           'id': '9591a5d53be641f08026330ddb197cd8'
           }),
    Munch({'id': '1a95bd78ec5440ceb1c6d4d81b806ca5',
           'status': 'active.auction',
           'lots': [Munch({'status': 'active',
                           'title': u'масло вершкове',
                           'id': 'd6c6cba98a0744bd8a315c2530cc8e90'})]
           }),
    Munch({'id': '701a78db57814a32ad14dbb74519ae07',
           'status': 'active.qualification',
           'lots': [Munch({'status': 'active',
                           'title': u'Виробничий одяг',
                           'id': 'f03fb012b4e5405d827a14106987f5db'})]}),
    Munch({'status': 'active.awarded',
           'lots': [Munch({'status': 'complete',
                           'title': u'акумуляторна батарея 6 ст-90',
                           'id': '4a562178b4c1468aa97c501f02576cc9'
                           }),
                    Munch({'status': 'active',
                           'title': u'батарея акумуляторна  6 ст-130',
                           'id': '2e7bab34b24246dd8693d6da4e6a3e4e'}
                          )],
           'id': '701a78db57814a33ad10dbb74519ae07'
           }),
    Munch({'status': 'complete',
           'id': 'c094dc11a6444d2db8000hcf06dd827b'
           }),
    Munch({'status': 'complete',
           'id': 'af9f3e04669d43d5abb07d37fb8007a7',
           'lots': [Munch({'status': 'complete',
                           'title': u'послуги з повірки лічильників теплової енергії Katra SKM-1U',
                           'id': 'e6903f5202eb488aa1e7fda08e0c8ff5'})]
           })
]

test_contracts_data = [Munch({'tender_token': '8c23c1905f7d4afbada967f91e88880a', 'contractID': 'UA-2016-04-15-000195-b-b1', 'owner': 'quintagroup.ua', 'awardID': '6b55fa3b869f4c0ca48b1bd7228b1f70', 'id': 'f56f3a7f0d92226585c5565dd594d66f', 'tender_id': '9591a5d52be641f08026330ddb197cd8'}),
                       Munch({'tender_token': 'ad09fc3ec8a64f0c845f46f37494b315', 'contractID': 'UA-2016-04-15-000195-b-b1', 'owner': 'netcast.com.ua', 'awardID': '6b55fa8b869f4c0ca48b2bd7228b1f70', 'id': 'f56f3a7f0d92426585c5565dd594d66f', 'tender_id': 'c094dc11a6444d2db8000hcf06dd827b'})]

test_tenders_queue = [Munch({'status': 'complete', 'owner': 'quintagroup.ua', 'contracts': [Munch({'status': 'active', 'awardID': '6b55fa3b869f4c0ca48b1bd7228b1f70', 'id': 'f56f3a7f0d92226585c5565dd594d66f', 'contractID': 'UA-2016-04-15-000195-b-b1'})], 'id': '9591a5d52be641f08026330ddb197cd8'}),
                      Munch({'status': 'complete', 'id': '9591a5d53be641f08026330ddb197cd8'}),
                      Munch({'status': 'active.awarded', 'lots': [Munch({'status': 'complete', 'id': '4a562178b4c1468aa97c501f02576cc9', 'title': u'акумуляторна батарея 6 ст-90'}), Munch({'status': 'active', 'id': '2e7bab34b24246dd8693d6da4e6a3e4e', 'title': u'батарея акумуляторна  6 ст-130'})], 'id': '701a78db57814a33ad10dbb74519ae07'}),
                      Munch({'status': 'complete', 'owner': 'netcast.com.ua', 'contracts': [Munch({'status': 'active', 'awardID': '6b55fa8b869f4c0ca48b2bd7228b1f70', 'id': 'f56f3a7f0d92426585c5565dd594d66f', 'contractID': 'UA-2016-04-15-000195-b-b1'})], 'id': 'c094dc11a6444d2db8000hcf06dd827b'}),
                      Munch({'status': 'complete', 'owner': 'prom.ua', 'lots': [Munch({'status': 'complete', 'id': 'e6903f5202eb488aa1e7fda08e0c8ff5', 'title': u'послуги з повірки лічильників теплової енергії Katra SKM-1U'})], 'contracts': [Munch({'status': 'non-active', 'awardID': '6b55fa8b869f4c0ca48b2bd7228b1f70', 'id': 'f56f4a7f0d92426588c4165dd594d66f', 'contractID': 'UA-2016-04-25-000195-b-b1'})], 'id': 'af9f3e04669d43d5abb07d37fb8007a7'})]

test_handicap_contracts_queue = [Munch({'status': 'active', 'awardID': '6b55fa3b869f4c0ca48b1bd7228b1f70', 'tender_id': '9591a5d52be641f08026330ddb197cd8', 'id': 'f56f3a7f0d92226585c5565dd594d66f', 'contractID': 'UA-2016-04-15-000195-b-b1'}),
                                 Munch({'status': 'active', 'awardID': '6b55fa8b869f4c0ca48b2bd7228b1f70', 'tender_id': 'c094dc11a6444d2db8000hcf06dd827b', 'id': 'f56f3a7f0d92426585c5565dd594d66f', 'contractID': 'UA-2016-04-15-000195-b-b1'})]


class BaseBridgeTest(unittest.TestCase):

    tenders_queue = []
    handicap_contracts_queue = []
    contracts_put_queue = []
    contracts_retry_put_queue = []

    def setUp(self):
        self.config = {'main': {'tenders_api_server': 'http://0.0.0.0:6543',
                                'contracting_api_server': 'http://0.0.0.0:6543',
                                'tenders_api_version': '2.3',
                                'contracting_api_version': '0',
                                'api_token': 'contracting'}}
        databridge.ContractingClient = Mock()
        databridge.TendersClient = Mock()
        self.bridge = databridge.ContractingDataBridge(self.config)
        self.bridge.tenders_client_backward = Mock(get_tenders=Mock(return_value=test_tenders_data),
                                                   headers={'X-Client-Request-ID': ''},
                                                   get_tender=lambda id: Munch({'data': [tender for tender in test_tender_data_with_contracts if id in tender.values()][0]}))
        self.bridge.tenders_client_forward = Mock(get_tenders=Mock(return_value=test_tenders_data[0:6]))
        for tender in self.tenders_queue:
            self.bridge.tenders_queue.put(tender)
        for tender in self.handicap_contracts_queue:
            self.bridge.handicap_contracts_queue.put(tender)
        for tender in self.contracts_put_queue:
            self.bridge.contracts_put_queue.put(tender)
        for tender in self.contracts_retry_put_queue:
            self.bridge.contracts_retry_put_queue.put(tender)

    def tearDown(self):
        self.bridge.tenders_queue = Queue()
        self.bridge.handicap_contracts_queue = Queue()
        self.bridge.contracts_put_queue = Queue()
        self.bridge.contracts_retry_put_queue = Queue()


class BridgeBackward(BaseBridgeTest):

    def test_get_tenders_contract_backward(self):
        self.assertEqual(len(self.bridge.tenders_queue), 0)
        backward_gevent = gevent.spawn(self.bridge.get_tender_contracts_backward)
        backward_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.tenders_queue), 5)


class BridgeForward(BaseBridgeTest):

    def test_get_tenders_contract_forward(self):
        self.assertEqual(len(self.bridge.tenders_queue), 0)
        forward_gevent = gevent.spawn(self.bridge.get_tender_contracts_forward)
        forward_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.tenders_queue), 3)


class BridgeGetContracts(BaseBridgeTest):
    tenders_queue = test_tenders_queue

    def resourse_error(self, id):
        raise databridge.ResourceNotFound('error in get_tender_contracts')

    def test_get_tender_contracts(self):
        self.assertEqual(len(self.bridge.tenders_queue), 5)
        self.bridge.contracting_client = Mock(get_contract=self.resourse_error)
        get_tender_contracts_gevent = gevent.spawn(self.bridge.get_tender_contracts)
        get_tender_contracts_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.handicap_contracts_queue), 2)

    def test_get_tender_exist_contracts(self):
        self.bridge.contracting_client = Mock(get_contract=Mock())
        get_tender_contracts_gevent = gevent.spawn(self.bridge.get_tender_contracts)
        get_tender_contracts_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.handicap_contracts_queue), 0)


class BrigdePrepairContracts(BaseBridgeTest):
    handicap_contracts_queue = test_handicap_contracts_queue

    def exception_error(self, id):
        raise Exception('error in prepare_contract_data')

    def test_prepare_contract_data(self):
        self.assertEqual(len(self.bridge.handicap_contracts_queue), 2)
        self.bridge.client = Mock(extract_credentials=lambda tender_id: Munch({'data': Munch({'id': tender_id,
                                                                                              'mode': 'mode for test',
                                                                                              'owner': [x.owner for x in test_tender_data_with_contracts if x.id == tender_id][0],
                                                                                              'tender_token': databridge.uuid4().hex})}))
        prepare_contract_data_gevent = gevent.spawn(self.bridge.prepare_contract_data)
        prepare_contract_data_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.contracts_put_queue), 2)

    def test_prepare_contract_data_except(self):
        self.assertEqual(len(self.bridge.handicap_contracts_queue), 2)
        self.bridge.client = Mock(extract_credentials=self.exception_error)
        prepare_contract_data_gevent = gevent.spawn(self.bridge.prepare_contract_data)
        prepare_contract_data_gevent.join(timeout=2)
        self.assertEqual(len(self.bridge.handicap_contracts_queue), 1)
        self.assertEqual(len(self.bridge.contracts_put_queue), 0)


class BridgePutContracts(BaseBridgeTest):
    contracts_put_queue = test_contracts_data

    def test_put_contracts(self):
        self.bridge.contracting_client = Mock(create_contract=Mock(return_value="Contract created"))
        put_contracts_gevent = gevent.spawn(self.bridge.put_contracts)
        put_contracts_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.contracts_put_queue), 0)

    def test_put_contracts_exception(self):
        self.bridge.contracting_client = Mock(create_contract='error')
        put_contracts_gevent = gevent.spawn(self.bridge.put_contracts)
        put_contracts_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.contracts_put_queue), 0)
        self.assertEqual(len(self.bridge.contracts_retry_put_queue), 2)


class BridgePutContractsRetry(BaseBridgeTest):
    contracts_retry_put_queue = test_contracts_data

    def test_retry_put_contract(self):
        self.assertEqual(len(self.bridge.contracts_retry_put_queue), 2)
        self.bridge.contracting_client = Mock(create_contract=Mock(return_value="Contract created"))
        retry_put_contracts_gevent = gevent.spawn(self.bridge.retry_put_contracts)
        retry_put_contracts_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.contracts_retry_put_queue), 0)

    def test_retry_put_contract_exc(self):
        self.assertEqual(len(self.bridge.contracts_retry_put_queue), 2)
        self.bridge.contracting_client = Mock(create_contract='error')
        retry_put_contracts_gevent = gevent.spawn(self.bridge.retry_put_contracts)
        retry_put_contracts_gevent.join(timeout=1)
        self.assertEqual(len(self.bridge.contracts_retry_put_queue), 2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseBridgeTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
