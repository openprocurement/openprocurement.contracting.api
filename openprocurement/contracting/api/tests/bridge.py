# -*- coding: utf-8 -*-

import unittest
import os
from simplejson import load
from openprocurement.contracting.api import databridge
from mock import Mock
from munch import munchify
import gevent
from gevent.queue import Queue


ROOT = os.path.dirname(__file__) + "/data/"
with open(ROOT + "tender_data.json") as tenders:
    data = load(tenders)

test_tender_data_with_contracts = munchify(data['test_tender_data_with_contracts'])
test_tenders_data = munchify(data['test_tenders_data'])
test_contracts_data = munchify(data['test_contracts_data'])
test_tenders_queue = munchify(data['test_tenders_queue'])
test_handicap_contracts_queue = munchify(data['test_handicap_contracts_queue'])


class BaseBridgeTest(unittest.TestCase):

    tenders_queue = []
    handicap_contracts_queue = []
    contracts_put_queue = []
    contracts_retry_put_queue = []

    def setUp(self):
        self.config = {"main": {"tenders_api_server": "http://0.0.0.0:6543",
                                "contracting_api_server": "http://0.0.0.0:6543",
                                "tenders_api_version": "2.3",
                                "contracting_api_version": "0",
                                "api_token": "contracting"}}
        databridge.ContractingClient = Mock()
        databridge.TendersClient = Mock()
        self.bridge = databridge.ContractingDataBridge(self.config)
        self.bridge.tenders_client_backward = Mock(get_tenders=Mock(return_value=test_tenders_data),
                                                   headers={"X-Client-Request-ID": ""},
                                                   get_tender=lambda id: munchify{"data": [tender for tender in test_tender_data_with_contracts if id in tender.values()][0]})
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
        backward_gevent = gevent.spawn(self.bridge.get_tender_contracts_backward)
        backward_gevent.join(timeout=1)
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[1]['id'])
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[2]['id'])
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[5]['id'])
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[6]['id'])
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[7]['id'])


class BridgeForward(BaseBridgeTest):

    def test_get_tenders_contract_forward(self):
        forward_gevent = gevent.spawn(self.bridge.get_tender_contracts_forward)
        forward_gevent.join(timeout=1)
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[1]['id'])
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[2]['id'])
        self.assertEqual(self.bridge.tenders_queue.get()['id'], test_tenders_data[5]['id'])


class BridgeGetContracts(BaseBridgeTest):
    tenders_queue = test_tenders_queue

    def resourse_error(self, id):
        raise databridge.ResourceNotFound("error in get_tender_contracts")

    def test_get_tender_contracts(self):
        self.bridge.contracting_client = Mock(get_contract=self.resourse_error)
        get_tender_contracts_gevent = gevent.spawn(self.bridge.get_tender_contracts)
        get_tender_contracts_gevent.join(timeout=1)
        self.assertEqual(self.bridge.handicap_contracts_queue.get()['id'], test_tender_data_with_contracts[0]['contracts'][0]['id'])
        self.assertEqual(self.bridge.handicap_contracts_queue.get()['id'], test_tender_data_with_contracts[1]['contracts'][0]['id'])

    def test_get_tender_exist_contracts(self):
        self.bridge.contracting_client = Mock(get_contract=Mock())
        get_tender_contracts_gevent = gevent.spawn(self.bridge.get_tender_contracts)
        get_tender_contracts_gevent.join(timeout=1)


class BrigdePrepairContracts(BaseBridgeTest):
    handicap_contracts_queue = test_handicap_contracts_queue

    def exception_error(self, id):
        raise Exception("error in prepare_contract_data")

    def test_prepare_contract_data(self):
        self.bridge.client = Mock(extract_credentials=lambda tender_id: munchify{"data": {"id": tender_id,
                                                                                          "mode": "mode for test",
                                                                                          "owner": [x.owner for x in test_tender_data_with_contracts if x.id == tender_id][0],
                                                                                          "tender_token": databridge.uuid4().hex}})
        prepare_contract_data_gevent = gevent.spawn(self.bridge.prepare_contract_data)
        prepare_contract_data_gevent.join(timeout=1)
        self.assertEqual(self.bridge.contracts_put_queue.get()['owner'], test_tender_data_with_contracts[0]['owner'])
        self.assertEqual(self.bridge.contracts_put_queue.get()['owner'], test_tender_data_with_contracts[1]['owner'])

    def test_prepare_contract_data_except(self):
        self.bridge.client = Mock(extract_credentials=self.exception_error)
        prepare_contract_data_gevent = gevent.spawn(self.bridge.prepare_contract_data)
        prepare_contract_data_gevent.join(timeout=2)
        self.assertEqual(self.bridge.handicap_contracts_queue.get()['id'], test_handicap_contracts_queue[1]['id'])


class BridgePutContracts(BaseBridgeTest):
    contracts_put_queue = test_contracts_data

    def test_put_contracts(self):
        self.bridge.contracting_client = Mock(create_contract=Mock(return_value="Contract created"))
        put_contracts_gevent = gevent.spawn(self.bridge.put_contracts)
        put_contracts_gevent.join(timeout=1)

    def test_put_contracts_exception(self):
        self.bridge.contracting_client = Mock(create_contract="error")
        put_contracts_gevent = gevent.spawn(self.bridge.put_contracts)
        put_contracts_gevent.join(timeout=1)
        self.assertEqual(self.bridge.contracts_retry_put_queue.get()['id'], test_contracts_data[0]['id'])
        self.assertEqual(self.bridge.contracts_retry_put_queue.get()['id'], test_contracts_data[1]['id'])


class BridgePutContractsRetry(BaseBridgeTest):
    contracts_retry_put_queue = test_contracts_data

    def test_retry_put_contract(self):
        self.bridge.contracting_client = Mock(create_contract=Mock(return_value="Contract created"))
        retry_put_contracts_gevent = gevent.spawn(self.bridge.retry_put_contracts)
        retry_put_contracts_gevent.join(timeout=1)

    def test_retry_put_contract_exc(self):
        self.bridge.contracting_client = Mock(create_contract="error")
        retry_put_contracts_gevent = gevent.spawn(self.bridge.retry_put_contracts)
        retry_put_contracts_gevent.join(timeout=1)
        self.assertEqual(self.bridge.contracts_retry_put_queue.get()['id'], test_contracts_data[0]['id'])
        self.assertEqual(self.bridge.contracts_retry_put_queue.get()['id'], test_contracts_data[1]['id'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BaseBridgeTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
