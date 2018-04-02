# -*- coding: utf-8 -*-
from functools import partial
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError
from cornice.resource import resource

from openprocurement.api.utils import error_handler
from openprocurement.contracting.api.traversal import factory


contractingresource = partial(
    resource,
    error_handler=error_handler,
    factory=factory
)

def extract_contract_adapter(request, contract_id):
    db = request.registry.db
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


def extract_contract(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ['PATH_INFO'] or '/')
    except KeyError:
        path = '/'
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

    contract_id = ""
    # extract contract id
    parts = path.split('/')
    if len(parts) < 4 or parts[3] != 'contracts':
        return

    contract_id = parts[4]
    return extract_contract_adapter(request, contract_id)


def contract_from_data(request, data, raise_error=True, create=True):
    contractType = data.get('contractType', 'common')
    model = request.registry.contract_contractTypes.get(contractType)
    if model is None and raise_error:
        request.errors.add('data', 'contractType', 'Not implemented')
        request.errors.status = 415
        raise error_handler(request.errors)
    if model is not None and create:
        model = model(data)
    return model
