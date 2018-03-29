# -*- coding: utf-8 -*-
from functools import partial
from pkg_resources import get_distribution
from logging import getLogger
from cornice.resource import resource
from openprocurement.api.utils import (
    error_handler,
)

from openprocurement.contracting.core.traversal import factory
from openprocurement.contracting.core.models import Contract


contractingresource = partial(
    resource,
    error_handler=error_handler,
    factory=factory
)

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def extract_contract(request):
    db = request.registry.db
    contract_id = request.matchdict['contract_id']
    doc = db.get(contract_id)
    if doc is not None and doc.get('doc_type') == 'contract':
        request.errors.add('url', 'contract_id', 'Archived')
        request.errors.status = 410
        raise error_handler(request.errors)
    elif doc is None or doc.get('doc_type') != 'Contract':
        request.errors.add('url', 'contract_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.contract_from_data(doc)


def contract_from_data(request, data, raise_error=True, create=True):
    if create:
        return Contract(data)
    return Contract
