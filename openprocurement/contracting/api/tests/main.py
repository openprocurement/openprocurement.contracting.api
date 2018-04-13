# -*- coding: utf-8 -*-

import unittest

from openprocurement.contracting.api.tests import (
    contract, traversal, utils, validation
)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(contract.suite())
    suite.addTest(traversal.suite())
    suite.addTest(utils.suite())
    suite.addTest(validation.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
