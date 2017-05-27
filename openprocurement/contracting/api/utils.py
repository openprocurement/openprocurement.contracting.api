# -*- coding: utf-8 -*-
from functools import partial
from pkg_resources import get_distribution
from logging import getLogger
from cornice.resource import resource
from schematics.exceptions import ModelValidationError
from pyramid.exceptions import URLDecodeError
from pyramid.compat import decode_path_info
from openprocurement.api.utils import (
    error_handler, get_revision_changes, context_unpack, apply_data_patch,
    generate_id, set_modetest_titles, get_now,
)
from openprocurement.api.models import Revision

from openprocurement.contracting.api.traversal import factory
from openprocurement.contracting.api.models import Contract, ESCOContract


contractingresource = partial(resource, error_handler=error_handler,
                              factory=factory)

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


class isContract(object):
    """ Route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'contractType = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.contract is not None:
            c_type = getattr(request.contract, 'contractType', None) or "common"  # BBB old contract wo contractType attr
            return c_type == self.val
        return False


def extract_contract_by_id(request, contract_id):
    db = request.registry.db
    doc = db.get(contract_id)
    if doc is None or doc.get('doc_type') != 'Contract':
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
    return extract_contract_by_id(request, contract_id)


def register_contract_contractType(config, model):
    """Register a contract contractType.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The contract model class
    """
    contract_type = model.contractType.default or 'common'
    config.registry.contract_contractTypes[contract_type] = model


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


def contract_serialize(request, contract_data, fields):
    contract = request.contract_from_data(contract_data, raise_error=False)
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


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated['data'] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_contract(request)


def set_ownership(item, request):
    item.owner_token = generate_id()
