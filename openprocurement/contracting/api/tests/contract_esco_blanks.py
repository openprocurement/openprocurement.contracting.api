# -*- coding: utf-8 -*-
from openprocurement.contracting.api.models import ESCOContract

# ContractEscoTest


def simple_add_esco_contract(self):
    u = ESCOContract(self.initial_data)
    u.contractID = "UA-C"

    assert u.id == self.initial_data['id']
    assert u.doc_id == self.initial_data['id']
    assert u.rev is None

    u.store(self.db)

    assert u.id == self.initial_data['id']
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.contractID == fromdb['contractID']
    assert u.doc_type == "Contract"

    u.delete_instance(self.db)
