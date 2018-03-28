# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.contracting.api.tests.base import (
    BaseWebTest
)
from openprocurement.contracting.api.tests.contract_blanks import (
    # ContractResourceTest
    empty_listing,
)


class ContractResourceTest(BaseWebTest):
    """ contract resource test """

    test_empty_listing = snitch(empty_listing)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
