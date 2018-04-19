# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResourceListing,
)
from openprocurement.contracting.api.utils import (
    contractingresource,
    contract_serialize,
    save_contract
)
from openprocurement.contracting.api.design import (
    FIELDS,
    contracts_by_dateModified_view,
    contracts_real_by_dateModified_view,
    contracts_test_by_dateModified_view,
    contracts_by_local_seq_view,
    contracts_real_by_local_seq_view,
    contracts_test_by_local_seq_view,
)
from openprocurement.contracting.api.validation import validate_contract_data

VIEW_MAP = {
    u'': contracts_real_by_dateModified_view,
    u'test': contracts_test_by_dateModified_view,
    u'_all_': contracts_by_dateModified_view,
}

CHANGES_VIEW_MAP = {
    u'': contracts_real_by_local_seq_view,
    u'test': contracts_test_by_local_seq_view,
    u'_all_': contracts_by_local_seq_view,
}

FEED = {
    u'dateModified': VIEW_MAP,
    u'changes': CHANGES_VIEW_MAP,
}


@contractingresource(name='Contracts',
                     path='/contracts',
                     description="Contracts")
class ContractsResource(APIResourceListing):
    """ Contract resource used only for contract listing """

    def __init__(self, request, context):
        super(ContractsResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = contract_serialize
        self.object_name_for_listing = 'Contracts'
        self.log_message_id = 'contract_list_custom'

    @json_view(content_type="application/json", permission='create_contract',
               validators=(validate_contract_data,))
    def post(self):
        contract = self.request.validated['contract']
        for i in self.request.validated['json_data'].get('documents', []):
            doc = type(contract).documents.model_class(i)
            doc.__parent__ = contract
            contract.documents.append(doc)

        # set_ownership(contract, self.request) TODO
        self.request.validated['contract'] = contract
        self.request.validated['contract_src'] = {}
        if save_contract(self.request):
            self.LOGGER.info('Created contract {} ({})'.format(contract.id, contract.contractID),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_create'},
                                                  {'contract_id': contract.id, 'contractID': contract.contractID or ''}))
            self.request.response.status = 201
            return {
                'data': contract.serialize("view"),
                'access': {
                    'token': contract.owner_token
                }
            }
