# -*- coding: utf-8 -*-
from functools import partial
from pkg_resources import get_distribution
from logging import getLogger
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError
from cornice.resource import resource
from schematics.exceptions import ModelValidationError

from openprocurement.api.utils import (
    get_now,
    error_handler,
    context_unpack,
    set_modetest_titles,
    get_revision_changes
)
from openprocurement.api.models.auction_models.models import Revision
from openprocurement.contracting.api.traversal import factory


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)

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
        raise error_handler(request)
    elif doc is None or doc.get('doc_type') != 'Contract':
        request.errors.add('url', 'contract_id', 'Not Found')
        request.errors.status = 404
        raise error_handler(request)

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
        raise error_handler(request)
    if model is not None and create:
        model = model(data)
    return model


def contract_serialize(request, contract_data, fields):
    contract = request.contract_from_data(contract_data, raise_error=False)
    contract.__parent__ = request.context
    return dict([(i, j) for i, j in contract.serialize("view").items() if i in fields])


def save_contract(request):
    """ Save contract object to database
    :param request:
    :return: True if Ok
    """
    contract = request.validated['contract']

    if contract.mode == u'test':
        set_modetest_titles(contract)
    patch = get_revision_changes(contract.serialize("plain"),
                                 request.validated['contract_src'])
    if patch:
        contract.revisions.append(
            Revision({'author': request.authenticated_userid,
                      'changes': patch, 'rev': contract.rev}))
        old_date_modified = contract.dateModified
        contract.dateModified = get_now()
        try:
            contract.store(request.registry.db)
        except ModelValidationError, e:  # pragma: no cover
            for i in e.message:
                request.errors.add('body', i, e.message[i])
            request.errors.status = 422
        except Exception, e:  # pragma: no cover
            request.errors.add('body', 'data', str(e))
        else:
            LOGGER.info('Saved contract {}: dateModified {} -> {}'.format(
                contract.id, old_date_modified and old_date_modified.isoformat(),
                contract.dateModified.isoformat()),
                extra=context_unpack(request, {'MESSAGE_ID': 'save_contract'},
                                     {'CONTRACT_REV': contract.rev}))
            return True
