# -*- coding: utf-8 -*-

import unittest
from openprocurement.contracting.api.tests.base import BaseWebTest
from openprocurement.contracting.api.databridge import generate_req_id, ContractingDataBridge


class BridgeTest(BaseWebTest):

    def setUp(self):
        self.config = {'loggers': {'': {'handlers': ['console'], 'level': 'DEBUG'}, 'openprocurement.contracting.api.databridge': {'handlers': ['console'], 'propagate': False, 'level': 'DEBUG'}}, 'main': {'tenders_api_server': 'http://0.0.0.0:6543', 'contracting_api_server': 'http://0.0.0.0:6543', 'tenders_api_version': '2.3', 'contracting_api_version': '0', 'api_token': 'contracting_secret'}, 'version': 1, 'formatters': {'simple': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}}, 'handlers': {'console': {'formatter': 'simple', 'class': 'logging.StreamHandler', 'stream': 'ext://sys.stdout', 'level': 'DEBUG'}}}
        self.bridge = ContractingDataBridge(self.config)
        self.client = self.bridge.client

    def tearDown(self):
        return

    def test_generate_req_id(self):
        self.assertIn('contracting-data-bridge-req-', generate_req_id())
        self.assertTrue(64, len(generate_req_id()))

    def test_get_tenders(self):
        self.bridge.get_tenders(self.client)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BridgeTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
