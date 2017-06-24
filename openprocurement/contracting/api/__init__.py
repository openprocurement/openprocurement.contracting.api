# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution, iter_entry_points
from openprocurement.contracting.api.utils import isContract

PKG = get_distribution(__package__)

LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init contracting plugin.')
    from openprocurement.contracting.api.models import Contract
    from openprocurement.contracting.api.utils import contract_from_data, extract_contract, register_contract_contractType
    from openprocurement.contracting.api.design import add_design
    add_design()
    config.registry.contract_contractTypes = {}
    config.add_route_predicate('contractType', isContract)
    config.add_directive('add_contract_contractType',
                         register_contract_contractType)
    config.add_contract_contractType(Contract)
    config.add_request_method(extract_contract, 'contract', reify=True)
    config.add_request_method(contract_from_data)
    config.scan("openprocurement.contracting.api.views")

    # search for plugins
    settings = config.get_settings()
    plugins = settings.get('plugins') and settings['plugins'].split(',')
    for entry_point in iter_entry_points('openprocurement.contracting.api.plugins'):
        if not plugins or entry_point.name in plugins:
            plugin = entry_point.load()
            plugin(config)
