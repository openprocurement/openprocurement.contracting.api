# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError

from openprocurement.api.utils import update_logging_context, error_handler
from openprocurement.api.validation import validate_json_data, validate_data
from openprocurement.contracting.api.models import Contract, Change
from openprocurement.api.models import validate_coordinate


def validate_items_delivery_location(request):
    """
    NOTE: validation for items delivery locaion is disabled on models level.
    Related to time difference:
        {{ tender}} <- {{ validation activation }} <- {{ contract}}
             ^---------< one contracting process >---------^
    see: https://app.asana.com/0/153268966093617/200894405797627 
    """
    contract = request.validated['data']
    items = contract.get('items', [])
    if items:
        for item in items:
            if item.get('deliveryLocation'):
                validators = [validate_coordinate(*args) for args in
                              [(-90, 90, 'latitude'), (-180, 180, 'longitude')]]
                errors = {}
                for validate, l in zip(validators, ('latitude', 'longitude')):
                    try:
                        validate(item['deliveryLocation'].get(l, ''))
                    except ValidationError as e:
                        errors[l] = e.message
                if errors:
                    request.errors.status = 422
                    request.errors.add('body', 'items', [{"deliveryLocation": errors}])
                    raise error_handler(request.errors)


def validate_contract_data(request):
    update_logging_context(request, {'contract_id': '__new__'})
    data = request.validated['json_data'] = validate_json_data(request)
    if data is None:
        return
    model = request.contract_from_data(data, create=False)
    if hasattr(request, 'check_accreditation') and not request.check_accreditation(model.create_accreditation):
        request.errors.add('contract', 'accreditation', 'Broker Accreditation level does not permit contract creation')
        request.errors.status = 403
        return
    return validate_data(request, model, data=data)


def validate_patch_contract_data(request):
    return validate_data(request, Contract, True)


def validate_change_data(request):
    update_logging_context(request, {'change_id': '__new__'})
    data = validate_json_data(request)
    if data is None:
        return
    return validate_data(request, Change, data=data)


def validate_patch_change_data(request):
    return validate_data(request, Change, True)
