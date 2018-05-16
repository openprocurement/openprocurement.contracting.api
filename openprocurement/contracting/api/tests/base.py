# -*- coding: utf-8 -*-
import os
import unittest
import warnings
import webtest

import zope.deferredimport

from base64 import b64encode
from urllib import urlencode
from uuid import uuid4

from requests.models import Response
from couchdb_schematics.document import SchematicsDocument
from schematics.transforms import whitelist
from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    Contract as BaseContract,
    Document as BaseDocument,
    plain_role,
    ListType,
    Revision,
    IsoDateTimeType,
    schematics_default_role
)
from openprocurement.api.constants import VERSION, SESSION

warnings.simplefilter("default")
zope.deferredimport.initialize()
zope.deferredimport.deprecated(
    "Import from openprocurement.contracting.core.tests.base instead",
    BaseContractWebTest='openprocurement.contracting.core.tests.base:BaseContractWebTest',
)

class PrefixedRequestClass(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseWebTest(unittest.TestCase):
    """Base Web Test to test openprocurement.contractning.api.

    It setups the database before each test and delete it after.
    """
    initial_auth = ('Basic', ('token', ''))
    docservice = False
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        self.app = webtest.TestApp(
            "config:tests.ini", relative_to=self.relative_to)
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = self.initial_auth
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()

    def setUpDS(self):
        self.app.app.registry.docservice_url = 'http://localhost'
        test = self

        def request(method, url, **kwargs):
            response = Response()
            if method == 'POST' and '/upload' in url:
                url = test.generate_docservice_url()
                response.status_code = 200
                response.encoding = 'application/json'
                response._content = '{{"data":{{"url":"{url}","hash":"md5:{md5}","format":"application/msword",\
                                     "title":"name.doc"}},"get_url":"{url}"}}'.format(url=url, md5='0'*32)
                response.reason = '200 OK'
            return response

        self._srequest = SESSION.request
        SESSION.request = request

    def generate_docservice_url(self):
        uuid = uuid4().hex
        key = self.app.app.registry.docservice_key
        keyid = key.hex_vk()[:8]
        signature = b64encode(key.signature("{}\0{}".format(uuid, '0' * 32)))
        query = {'Signature': signature, 'KeyID': keyid}
        return "http://localhost/get/{}?{}".format(uuid, urlencode(query))

    def tearDownDS(self):
        SESSION.request = self._srequest

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.couchdb_server[self.db.name]


def error_handler(variable):
    exception = Exception()
    exception.message = variable
    return exception


class Document(BaseDocument):
    documentOf = StringType(required=True, choices=['contract'],
                            default='contract')


class Contract(SchematicsDocument, BaseContract):
    contractType = StringType(default='common')
    mode = StringType(choices=['test'])
    dateModified = IsoDateTimeType()
    create_accreditation = 1
    documents = ListType(ModelType(Document), default=list())
    revisions = ListType(ModelType(Revision), default=list())
    owner_token = StringType(default=lambda: uuid4().hex)

    class Options:
        roles = {
            'plain': plain_role,
            'create': (whitelist('id', )),
            'view': (whitelist('id', )),
            'default': schematics_default_role,
        }
