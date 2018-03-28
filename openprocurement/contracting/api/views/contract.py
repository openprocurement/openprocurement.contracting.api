# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    APIResourceListing,
)
from openprocurement.contracting.api.utils import (
    contractingresource,
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
