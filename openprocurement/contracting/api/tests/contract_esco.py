# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.contracting.api.tests.base import (
    test_contract_data,
    BaseWebTest,
)
from openprocurement.contracting.api.tests.contract_esco_blanks import (
    # ContractESCOTest
    simple_add_esco_contract,
)
from openprocurement.contracting.api.tests.contract_blanks import (
    # ContractESCOResourceTest
    contract_type_check,
)


class ContractESCOTest(BaseWebTest):
    initial_data = deepcopy(test_contract_data)
    initial_data['contractType'] = 'esco.EU'

    test_simple_add_contract = snitch(simple_add_esco_contract)


class ContractESCOResourceTest(BaseWebTest):
    """ esco contract resource test """
    initial_data = deepcopy(test_contract_data)
    initial_data['contractType'] = 'esco.EU'

    contract_type = 'esco.EU'
    test_contract_type_check = snitch(contract_type_check)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractESCOTest))
    suite.addTest(unittest.makeSuite(ContractESCOResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
