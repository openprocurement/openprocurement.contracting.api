# -*- coding: utf-8 -*-
import unittest
from email.header import Header
from openprocurement.contracting.api.tests.base import BaseContractContentWebTest

from openprocurement.api.tests.document import MockConnection


class ContractDocumentResourceTest(BaseContractContentWebTest):
    s3_connection = False
    initial_auth = ('Basic', ('broker', ''))

    def test_not_found(self):
        response = self.app.get('/contracts/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.post('/contracts/some_id/documents', status=404, upload_files=[
                                 ('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(self.contract_id, self.contract_token), status=404, upload_files=[
                                 ('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/contracts/some_id/documents/some_id', status=404, upload_files=[
                                ('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.put('/contracts/{}/documents/some_id'.format(
            self.contract_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

        response = self.app.get('/contracts/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'contract_id'}
        ])

        response = self.app.get('/contracts/{}/documents/some_id'.format(
            self.contract_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_contract_document(self):
        response = self.app.get('/contracts/{}/documents'.format(self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json, {"data": []})

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token), upload_files=[('file', u'укр.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u'description': u"Can't add document in current (draft) contract status",
                                                    u'location': u'body', u'name': u'data'}])

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, self.contract_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token), upload_files=[('file', u'укр.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        self.assertEqual(response.json["data"]["documentOf"], "contract")
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/contracts/{}/documents'.format(self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

        if self.s3_connection:
            response = self.app.get('/contracts/{}/documents/{}?download={}'.format(
                self.contract_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertEqual(response.location, 'http://s3/{}/{}/{}/{}'.format('bucket', self.contract_id, doc_id, key))
        else:
            response = self.app.get('/contracts/{}/documents/{}?download=some_id'.format(
                self.contract_id, doc_id), status=404)
            self.assertEqual(response.status, '404 Not Found')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['status'], 'error')
            self.assertEqual(response.json['errors'], [
                {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
            ])

            response = self.app.get('/contracts/{}/documents/{}?download={}'.format(
                self.contract_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

        response = self.app.get('/contracts/{}/documents/{}'.format(
            self.contract_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token), upload_files=[('file', u'укр.doc'.encode("ascii", "xmlcharrefreplace"), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertNotIn('acc_token', response.headers['Location'])

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, self.contract_token),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'terminated')

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token),
            upload_files=[('file', u'укр.doc'.encode("ascii", "xmlcharrefreplace"), 'contentX')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u'description': u"Can't add document in current (terminated) contract status",
                                                    u'location': u'body', u'name': u'data'}])


    def test_put_contract_document(self):
        from six import BytesIO
        from urllib import quote
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, self.contract_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n'''.format(u'\uff07')
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/contracts/{}/documents'.format(self.contract_id)), environ)
        req.environ['wsgi.input'] = BytesIO(body.encode('utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "could not decode params")

        body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename*=utf-8''{}\nContent-Type: application/msword\n\ncontent\n'''.format(quote('укр.doc'))
        environ = self.app._make_environ()
        environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
        environ['REQUEST_METHOD'] = 'POST'
        req = self.app.RequestClass.blank(self.app._remove_fragment('/contracts/{}/documents?acc_token={}'.format(self.contract_id, self.contract_token)), environ)
        req.environ['wsgi.input'] = BytesIO(body.encode(req.charset or 'utf8'))
        req.content_length = len(body)
        response = self.app.do_request(req)
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/contracts/{}/documents/{}?acc_token={}'.format(
            self.contract_id, doc_id, self.contract_token), upload_files=[('file', 'name  name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        if self.s3_connection:
            response = self.app.get('/contracts/{}/documents/{}?download={}'.format(
                self.contract_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertEqual(response.location, 'http://s3/{}/{}/{}/{}'.format('bucket', self.contract_id, doc_id, key))
        else:
            response = self.app.get('/contracts/{}/documents/{}?download={}'.format(
                self.contract_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content2')

        response = self.app.get('/contracts/{}/documents/{}'.format(
            self.contract_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name name.doc', response.json["data"]["title"])
        dateModified2 = response.json["data"]['dateModified']
        self.assertTrue(dateModified < dateModified2)
        self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])

        response = self.app.get('/contracts/{}/documents?all=true'.format(self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        dateModified = response.json["data"]['dateModified']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.get('/contracts/{}/documents'.format(self.contract_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
        self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

        response = self.app.put('/contracts/{}/documents/{}?acc_token={}'.format(self.contract_id, doc_id, self.contract_token), status=404, upload_files=[
                                ('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/contracts/{}/documents/{}?acc_token={}'.format(
            self.contract_id, doc_id, self.contract_token), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        if self.s3_connection:
            response = self.app.get('/contracts/{}/documents/{}?download={}'.format(
                self.contract_id, doc_id, key))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertEqual(response.location, 'http://s3/{}/{}/{}/{}'.format('bucket', self.contract_id, doc_id, key))
        else:
            response = self.app.get('/contracts/{}/documents/{}?download={}'.format(
                self.contract_id, doc_id, key))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content3')

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, self.contract_token),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'terminated')

        response = self.app.put('/contracts/{}/documents/{}?acc_token={}'.format(
            self.contract_id, doc_id, self.contract_token), 'contentX', content_type='application/msword', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u'description': u"Can't update document in current (terminated) contract status",
                                                    u'location': u'body', u'name': u'data'}])

    def test_patch_contract_document(self):
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, self.contract_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token), upload_files=[('file', str(Header(u'укр.doc', 'utf-8')), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        self.assertEqual(response.json["data"]["documentOf"], "contract")
        self.assertNotIn("documentType", response.json["data"])

        response = self.app.patch_json('/contracts/{}/documents/{}?acc_token={}'.format(self.contract_id, doc_id, self.contract_token), {"data": {
            "description": "document description",
            "documentType": 'notice'
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertIn("documentType", response.json["data"])
        self.assertEqual(response.json["data"]["documentType"], 'notice')

        response = self.app.patch_json('/contracts/{}/documents/{}?acc_token={}'.format(self.contract_id, doc_id, self.contract_token), {"data": {
            "documentType": None
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertNotIn("documentType", response.json["data"])

        response = self.app.get('/contracts/{}/documents/{}'.format(self.contract_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, self.contract_token),
                                       {"data": {"status": "terminated"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'terminated')

        response = self.app.patch_json('/contracts/{}/documents/{}?acc_token={}'.format(self.contract_id, doc_id, self.contract_token), {"data": {
            "description": "document description X",
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u'description': u"Can't update document in current (terminated) contract status",
                                                    u'location': u'body', u'name': u'data'}])

    def test_contract_change_document(self):
        response = self.app.patch_json('/contracts/{}?acc_token={}'.format(self.contract_id, self.contract_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token), upload_files=[('file', str(Header(u'укр.doc', 'utf-8')), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(u'укр.doc', response.json["data"]["title"])
        self.assertEqual(response.json["data"]["documentOf"], "contract")
        self.assertNotIn("documentType", response.json["data"])

        response = self.app.patch_json('/contracts/{}/documents/{}?acc_token={}'.format(self.contract_id, doc_id, self.contract_token), {"data": {
            "documentOf": "change",
            "relatedItem": '1234' * 8,
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "relatedItem", "description": ["relatedItem should be one of changes"]}])

        response = self.app.post_json('/contracts/{}/changes?acc_token={}'.format(self.contract['id'], self.contract_token),
                                      {'data': {'rationale': u'причина зміни укр',
                                                'rationale_en': 'change cause en'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        change = response.json['data']

        response = self.app.patch_json('/contracts/{}/documents/{}?acc_token={}'.format(self.contract_id, doc_id, self.contract_token), {"data": {
            "documentOf": "change",
            "relatedItem": change['id'],
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual(response.json["data"]["documentOf"], 'change')
        self.assertEqual(response.json["data"]["relatedItem"], change['id'])

        response = self.app.patch_json('/contracts/{}/changes/{}?acc_token={}'.format(self.contract['id'], change['id'], self.contract_token),
                                        {'data': {'status': 'active'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post('/contracts/{}/documents?acc_token={}'.format(
            self.contract_id, self.contract_token), upload_files=[('file', str(Header(u'укр2.doc', 'utf-8')), 'content2')])
        self.assertEqual(response.status, '201 Created')
        doc_id = response.json["data"]['id']

        response = self.app.patch_json('/contracts/{}/documents/{}?acc_token={}'.format(self.contract_id, doc_id, self.contract_token), {"data": {
            "documentOf": "change",
            "relatedItem": change['id'],
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "data", "description": "Can't add document to 'active' change"}])

class ContractDocumentWithS3ResourceTest(ContractDocumentResourceTest):
    s3_connection = True

    def setUp(self):
        super(ContractDocumentWithS3ResourceTest, self).setUp()
        # Create mock s3 connection
        connection = MockConnection()
        self.app.app.registry.s3_connection = connection
        bucket_name = 'bucket'
        if bucket_name not in [b.name for b in connection.get_all_buckets()]:
            connection.create_bucket(bucket_name)
        self.app.app.registry.bucket_name = bucket_name


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContractDocumentResourceTest))
    suite.addTest(unittest.makeSuite(ContractDocumentWithS3ResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
