# -*- coding: utf-8 -*-
from openprocurement.api.traversal import get_item

from pyramid.security import (
    ALL_PERMISSIONS,
    Allow,
    Everyone,
)


class Root(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Everyone, 'view_listing'),
        (Allow, Everyone, 'view_contract'),
        (Allow, 'g:contracting', 'create_contract'),
        (Allow, 'g:Administrator', 'edit_contract'),
        (Allow, 'g:admins', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request
        self.db = request.registry.db
