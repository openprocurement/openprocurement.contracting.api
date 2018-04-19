# -*- coding: utf-8 -*-

import os
import unittest

from openprocurement.contracting.api.traversal import Root, factory
from openprocurement.contracting.api.tests.base import BaseWebTest

from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Everyone,
)
from mock import MagicMock
from munch import munchify


class TraversalTest(BaseWebTest):
    test_data = {
        "status": "cancelled",
        "id": '123456789',
        "documents": [{
            "id": "document_id", 'name': 'document',
        }],
        "changes": [{
            "id": "change_id",
            "rationale": 'rationale'
        }]
    }
    relative_to = os.path.dirname(__file__)
    test_ctl = [
        # (Allow, Everyone, ALL_PERMISSIONS),
        (Allow, Everyone, 'view_listing'),
        (Allow, Everyone, 'view_contract'),
        (Allow, 'g:contracting', 'create_contract'),
        (Allow, 'g:Administrator', 'edit_contract'),
        (Allow, 'g:admins', ALL_PERMISSIONS)
    ]

    def test_root(self):
        ctl = Root.__acl__
        self.assertEqual(ctl, TraversalTest.test_ctl)

    def test_factory(self):
        request = MagicMock()
        request.method = 'POST'
        request.validated = {'contract_src': {}}
        request.matchdict = {}
        response = factory(request)
        self.assertEqual(response.__acl__, TraversalTest.test_ctl)
        self.assertEqual(response.request.matchdict, {})

        request.contract = MagicMock()
        request.contract.serialize.return_value = None
        request.matchdict = {'contract_id': 'id'}
        response = factory(request)
        self.assertEqual(response, request.contract)

        request.contract = munchify(TraversalTest.test_data)
        request.method = 'GET'
        request.matchdict = {
            'contract_id': 'id',
            'document_id': 'document_id'
        }
        response = factory(request)
        self.assertEqual(response.id, self.test_data['documents'][0]['id'])

        request.matchdict = {
            'contract_id': 'id',
            'change_id': 'change_id',

        }
        response = factory(request)
        self.assertEqual(response.id, self.test_data['changes'][0]['id'])

        request.matchdict = {
            'contract_id': 'id',
        }
        response = factory(request)
        self.assertEqual(response.id, self.test_data['id'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TraversalTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
