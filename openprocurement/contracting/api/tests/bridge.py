# -*- coding: utf-8 -*-

import unittest
from openprocurement.contracting.api.tests.base import BaseWebTest
from openprocurement.contracting.api.databridge import generate_req_id, ContractingDataBridge
from mock import Mock
from munch import Munch


tenders_data = [
    Munch({'status': 'active.awarded',
           'lots': [Munch({'status': 'active',
                           'description': u'Банани',
                           'title': u'Банани',
                           'minimalStep': Munch({'currency': 'UAH',
                                                 'amount': 210,
                                                 'valueAddedTaxIncluded': True}),
                           'auctionPeriod': Munch({'startDate': '2016-04-29T13:48:15+03:00',
                                                   'endDate': '2016-04-29T14:15:15.778119+03:00'}),
                           'value': Munch({'currency': 'UAH',
                                           'amount': 14600,
                                           'valueAddedTaxIncluded': True}),
                           'auctionUrl': 'https://auction.openprocurement.org/tenders/e340de0f2b984eada30c0433a40591e0_438a5b08bf9f4c1c973a87fd34ba5a2d',
                           'id': '438a5b08bf9f4c1c973a87fd34ba5a2d'})], 'dateModified': '2016-05-06T15:26:48.702640+03:00',
           'id': 'e340de0f2b984eada30c0433a40591e0'}),

    Munch({'status': 'complete',
           'dateModified': '2016-05-06T15:20:18.294057+03:00',
           'id': '9591a5d52be641f08026330ddb197cd8'}),

    Munch({'status': 'active.auction',
           'lots': [Munch({'status': 'active',
                           'description': u'жирність не меньше 72%',
                           'title': u'масло вершкове',
                           'minimalStep': Munch({'currency': 'UAH',
                                                 'amount': 340,
                                                 'valueAddedTaxIncluded': True}),
                           'auctionPeriod': Munch({'startDate': '2016-05-06T15:39:03+03:00'}),
                           'value': Munch({'currency': 'UAH',
                                           'amount': 68000,
                                           'valueAddedTaxIncluded': True}),
                           'auctionUrl': 'https://auction.openprocurement.org/tenders/1a95bd78ec5440ceb1c6d4d81b806ca5_d6c6cba98a0744bd8a315c2530cc8e90',
                           'id': 'd6c6cba98a0744bd8a315c2530cc8e90'})],
           'dateModified': '2016-05-06T15:39:43.278754+03:00',
           'id': '1a95bd78ec5440ceb1c6d4d81b806ca5'}),
    Munch({'status': 'active.qualification',
           'lots': [Munch({'status': 'active',
                           'description': u'Детальний опис  лоту та технічні (якісні) вимоги до пропонованого Учасниками товару містяться в документації, що додається окремим файлом.',
                           'title': u'Виробничий одяг',
                           'minimalStep': Munch({'currency': 'UAH',
                                                 'amount': 300,
                                                 'valueAddedTaxIncluded': True}),
                           'auctionPeriod': Munch({'startDate': '2016-05-05T15:39:20+03:00',
                                                   'endDate': '2016-05-05T16:00:21.643780+03:00'}),
                           'value': Munch({'currency': 'UAH',
                                           'amount': 55600,
                                           'valueAddedTaxIncluded': True}),
                           'auctionUrl': 'https://auction.openprocurement.org/tenders/3639115f895b4e508eb2ebc1215c148e_f03fb012b4e5405d827a14106987f5db',
                           'id': 'f03fb012b4e5405d827a14106987f5db'})],
           'id': '701a78db57814a32ad14dbb74519ae07'}),
    Munch({'status': 'active.awarded',
           'lots': [Munch({'status': 'complete',
                           'description': u'батарея акумуляторна свинцова статерна 6ст-90 для вантажних автомобілів та тракторів.Доставку здійснює Постачальник.',
                           'title': u'акумуляторна батарея 6 ст-90',
                           'minimalStep': Munch({'currency': 'UAH',
                                                 'amount': 350,
                                                 'valueAddedTaxIncluded': True}),
                           'auctionPeriod': Munch({'startDate': '2016-05-11T15:30:43+03:00',
                                                   'shouldStartAfter': '2016-05-10T14:20:00+03:00'}),
                           'value': Munch({'currency': 'UAH',
                                           'amount': 11670,
                                           'valueAddedTaxIncluded': True}),
                           'id': '4a562178b4c1468aa97c501f02576cc9'}),
                    Munch({'status': 'active',
                           'description': u'батарея акумуляторна 6ст-130 для навантажувача Балкан-кар.Доставку здійснює Постачальник.',
                           'title': u'батарея акумуляторна  6 ст-130',
                           'minimalStep': Munch({'currency': 'UAH',
                                                 'amount': 100,
                                                 'valueAddedTaxIncluded': True}),
                           'auctionPeriod': Munch({'startDate': '2016-05-11T11:27:01+03:00',
                                                   'shouldStartAfter': '2016-05-10T14:20:00+03:00'}),
                           'value': Munch({'currency': 'UAH',
                                           'amount': 3200,
                                           'valueAddedTaxIncluded': True}),
                           'id': '2e7bab34b24246dd8693d6da4e6a3e4e'})],
           'dateModified': '2016-05-06T14:22:00.616442+03:00',
           'id': '701a78db57814a33ad10dbb74519ae07'}),

    Munch({'status': 'complete',
           'dateModified': '2016-05-06T15:28:18.382092+03:00',
           'id': 'c094dc11a6844d2db8000fcf06dd827b'}),
]


class BridgeTest(BaseWebTest):

    def setUp(self):
        self.config = {'loggers': {'': {'handlers': ['console'], 'level': 'DEBUG'}, 'openprocurement.contracting.api.databridge': {'handlers': ['console'], 'propagate': False, 'level': 'DEBUG'}}, 'main': {'tenders_api_server': 'http://0.0.0.0:6543', 'contracting_api_server': 'http://0.0.0.0:6543', 'tenders_api_version': '2.3', 'contracting_api_version': '0', 'api_token': 'contracting_secret'}, 'version': 1, 'formatters': {'simple': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}}, 'handlers': {'console': {'formatter': 'simple', 'class': 'logging.StreamHandler', 'stream': 'ext://sys.stdout', 'level': 'DEBUG'}}}
        self.bridge = ContractingDataBridge(self.config)
        self.client = self.bridge.client
        self.tenders_client_forward = self.bridge.tenders_client_forward
        # Mock tenders data from db for old tenders
        self.tenders_client_backward = Mock(params={'feed': 'changes', 'offset': 'e18b858d39400e8d5616943e9857bd96', 'descending': 1, 'mode': '_all_', 'opt_fields': 'status,lots'},
                                            headers={'Cookie': 'SERVER_ID=ddf2a8db848a4b07a6c96a89de980404a7b987dc03307ca8401de95736f64ea0312df337dd8da351f52eeed712cc27c98ff3269c8ad00a156416a774d8a5cd32; Path=/', 'Content-Type': 'application/json', 'X-Client-Request-ID': 'contracting-data-bridge-req-7208c2d3-4662-4837-9fc1-328d42e5a871'})

    def tearDown(self):
        return

    def test_generate_req_id(self):
        self.assertIn('contracting-data-bridge-req-', generate_req_id())
        self.assertTrue(64, len(generate_req_id()))

    def test_get_tender_contracts_backward_tender_complete(self):
        get_tenders = Mock(return_value=tenders_data[0:2])
        self.tenders_client_backward.attach_mock(get_tenders, 'get_tenders')
        tender_complete = self.bridge.get_tenders(self.tenders_client_backward).next()
        self.assertEqual(tender_complete.status, 'complete')

    def test_get_tender_contracts_backward_tender_multilot(self):
        get_tenders = Mock(return_value=tenders_data[3:5])
        self.tenders_client_backward.attach_mock(get_tenders, 'get_tenders')
        tender_multilot = self.bridge.get_tenders(self.tenders_client_backward).next()
        self.assertEqual(len(tender_multilot.lots), 2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BridgeTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
