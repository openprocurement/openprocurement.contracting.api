# -*- coding: utf-8 -*-
import unittest

from mock import patch, MagicMock
from pyramid.request import Request

from openprocurement.contracting.api.tests.base import error_handler
from openprocurement.contracting.api.validation import validate_contract_data


class TestValidationFucntions(unittest.TestCase):
    """The point of this test cases if test specific functions behavior
       so all functions that are called inside tested functions are patched."""

    def setUp(self):
        self.expected_result = True
        self.request = Request(dict())
        self.request.validated = dict()
        self.model = MagicMock()
        self.request.contract_from_data = self.model
        self.request.errors = MagicMock()

    @patch('openprocurement.contracting.api.validation.validate_data')
    @patch('openprocurement.contracting.api.validation.validate_json_data')
    @patch('openprocurement.contracting.api.validation.update_logging_context')
    def test_validate_contract_data_no_error(self,
                                             mocker_update_logging_context,
                                             mocker_validate_json_data,
                                             mocker_validate_data):
        mocker_update_logging_context.return_value = True
        mocker_validate_json_data.return_value = {'id': 'fake_id'}
        mocker_validate_data.return_value = self.expected_result

        self.assertEquals(validate_contract_data(self.request),
                          self.expected_result)

    @patch('openprocurement.contracting.api.validation.error_handler')
    @patch('openprocurement.contracting.api.validation.validate_json_data')
    @patch('openprocurement.contracting.api.validation.update_logging_context')
    def test_validate_contract_data_with_error(self,
                                               mocker_update_logging_context,
                                               mocker_validate_json_data,
                                               mocker_error_handler):
        mocker_update_logging_context.return_value = True
        mocker_validate_json_data.return_value = {'id': 'fake_id'}
        checked_accreditation = MagicMock(return_value=False)
        mocker_error_handler.side_effect = error_handler
        self.request.check_accreditation = checked_accreditation

        with self.assertRaises(Exception) as cm:
            validate_contract_data(self.request)
        self.assertEqual(cm.exception.message.status, 403)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestValidationFucntions))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
