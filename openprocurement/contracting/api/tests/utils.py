# -*- coding: utf-8 -*-
import unittest

from mock import MagicMock, patch
from pyramid.exceptions import URLDecodeError

from openprocurement.contracting.api.tests.base import error_handler
from openprocurement.contracting.api.utils import (
    extract_contract_adapter,
    extract_contract,
    contract_from_data,
    contract_serialize,
    save_contract
)


class TestApiFucntions(unittest.TestCase):
    """Testing all functions inside utils.py"""

    def setUp(self):
        self.contract_id = '1' * 32
        self.doc = {
            self.contract_id: {'id': 'fake_id', 'doc_type': 'contract'}}
        self.request = MagicMock()
        self.request.validated = {'contract_src': None}
        self.contract_mock = MagicMock()
        self.request.validated['contract'] = self.contract_mock
        self.db_mock = MagicMock()
        self.db_mock.configure_mock(**{'db': self.doc})
        self.request.configure_mock(**{'registry': self.db_mock})

    @patch('openprocurement.contracting.api.utils.error_handler')
    def test_extract_contract_adapter_410_error(self, mocker_error_handler):
        mocker_error_handler.side_effect = error_handler

        with self.assertRaises(Exception) as cm:
            extract_contract_adapter(self.request, self.contract_id)
        self.assertEqual(cm.exception.message.status, 410)
        cm.exception.message.add.assert_called_once_with('url', 'contract_id',
                                                         'Archived')

    @patch('openprocurement.contracting.api.utils.error_handler')
    def test_extract_contract_adapter_404_error(self, mocker_error_handler):
        mocker_error_handler.side_effect = error_handler
        self.doc[self.contract_id]['doc_type'] = 'Tender'

        with self.assertRaises(Exception) as cm:
            extract_contract_adapter(self.request, self.contract_id)
        self.assertEqual(cm.exception.message.status, 404)
        cm.exception.message.add.assert_called_once_with('url', 'contract_id',
                                                         'Not Found')

    def test_extract_contract_adapter_success(self):
        self.doc[self.contract_id]['doc_type'] = 'Contract'
        self.request.contract_from_data.return_value = True

        self.assertEqual(
            extract_contract_adapter(self.request, self.contract_id), True)

    @patch('openprocurement.contracting.api.utils.decode_path_info')
    def test_extract_contract_URLDecodeError(self, mocker_decode_path_info):
        error = UnicodeDecodeError('', '', 0, 0, '')
        mocker_decode_path_info.side_effect = error

        with self.assertRaises(Exception) as cm:
            extract_contract(self.request)
        self.assertEqual(type(cm.exception), URLDecodeError)

    @patch('openprocurement.contracting.api.utils.decode_path_info')
    def test_extract_contract_KeyError(self, mocker_decode_path_info):
        mocker_decode_path_info.side_effect = KeyError()

        self.assertEqual(extract_contract(self.request), None)

    @patch('openprocurement.contracting.api.utils.extract_contract_adapter')
    @patch('openprocurement.contracting.api.utils.decode_path_info')
    def test_extract_contract_success(self, mocker_decode_path_info,
                                      mocker_extract_contract_adapter):
        mocker_decode_path_info.return_value = \
            '2.3/tenders/7dc086c4a213492ab9c43b95b43bd817/' \
            'contracts/bebdbaf7777d4bd39756f3e8872c1f46'
        mocker_extract_contract_adapter.return_value = True

        self.assertEqual(extract_contract(self.request), True)

    @patch('openprocurement.contracting.api.utils.error_handler')
    def test_contract_from_data_415_error(self, mocker_error_handler):
        mocker_error_handler.side_effect = error_handler
        self.request.registry.configure_mock(
            **{'contract_contractTypes': {'common': None}})

        with self.assertRaises(Exception) as cm:
            contract_from_data(self.request, dict())
        self.assertEqual(cm.exception.message.status, 415)
        cm.exception.message.add.assert_called_once_with('data',
                                                         'contractType',
                                                         'Not implemented')

    def test_contract_from_data_success(self):
        test_mock = MagicMock()
        test_mock.return_value = test_mock
        self.request.registry.configure_mock(**{'contract_contractTypes':
                                                    {'common': test_mock}})

        self.assertEqual(contract_from_data(self.request, dict()), test_mock)
        test_mock.assert_called_once_with(dict())

    def test_contract_serialize(self):
        self.contract_mock.serialize.return_value = {
            'id': self.contract_id, 'status': 'active'}
        self.request.contract_from_data.return_value = self.contract_mock

        self.assertEqual(contract_serialize(self.request, None, ['id']),
                         {'id': self.contract_id})

    @patch('openprocurement.contracting.api.utils.set_modetest_titles')
    @patch('openprocurement.contracting.api.utils.get_revision_changes')
    def test_save_contract_return_None(self, mocker_get_revision_changes,
                                       mocker_set_modetest_titles):
        mocker_get_revision_changes.return_value = None
        mocker_set_modetest_titles.return_value = None
        self.contract_mock.configure_mock(**{'mode': u'test'})

        self.assertEqual(save_contract(self.request), None)

    @patch('openprocurement.contracting.api.utils.get_revision_changes')
    def test_save_contract_return_True(self, mocker_get_revision_changes):
        mocker_get_revision_changes.return_value = [{'id': self.contract_id}]
        self.contract_mock.store.return_value = True
        self.request.configure_mock(**{'authenticated_userid': 'Quinta'})
        self.contract_mock.configure_mock(**{'rev': self.contract_id,
                                             'mode': u'prod'})

        self.assertEqual(save_contract(self.request), True)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestApiFucntions))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
