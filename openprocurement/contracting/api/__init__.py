# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution

PKG = get_distribution(__package__)

LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init contracting plugin.')
    from openprocurement.contracting.api.models import CommonContract
    from openprocurement.contracting.api.utils import contract_from_data, extract_contract, register_contract_contractType
    from openprocurement.contracting.api.design import add_design
    add_design()
    config.registry.contract_contractTypes = {}
    config.add_directive('add_contract_contractType',
                         register_contract_contractType)
    config.add_contract_contractType(CommonContract)
    config.add_request_method(extract_contract, 'contract', reify=True)
    config.add_request_method(contract_from_data)
    config.scan("openprocurement.contracting.api.views")


def includeme_esco(config):
    LOGGER.info('Init esco contracting plugin.')
    from openprocurement.contracting.api.models import ESCOContract
    config.add_contract_contractType(ESCOContract)
    # Should be uncommented when esco contracts will be moved to own package
    # config.scan("openprocurement.contracting.api.views")
