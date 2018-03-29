# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution, iter_entry_points


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init contracting.api plugin.')
    from openprocurement.contracting.api.utils import contract_from_data, extract_contract
    from openprocurement.contracting.api.design import add_design
    add_design()
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
