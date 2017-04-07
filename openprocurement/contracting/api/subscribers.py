# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from openprocurement.api.events import ErrorDesctiptorEvent


@subscriber(ErrorDesctiptorEvent)
def contract_error_handler(event):
    if 'contract' in event.request.validated:
        event.params['CONTRACT_REV'] = event.request.validated['contract'].rev
        event.params['CONTRACTID'] = event.request.validated['contract'].contractID
        event.params['CONTRACT_STATUS'] = event.request.validated['contract'].status
