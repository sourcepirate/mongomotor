# -*- coding: utf-8 -*-

# Copyright 2016 Juca Crispim <juca@poraodojuca.net>

# This file is part of mongomotor.

# mongomotor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mongomotor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with mongomotor. If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase
from mongomotor import Document, connect, disconnect
from mongomotor.fields import StringField
from mongomotor.queryset import QuerySet
from tests import async_test


class QuerySetTest(TestCase):

    @classmethod
    def setUpClass(cls):
        connect()

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def setUp(self):
        class TestDoc(Document):
            a = StringField()

        self.test_doc = TestDoc

    @async_test
    def tearDown(self):
        yield from self.test_doc.drop_collection()

    @async_test
    def test_to_list(self):
        for i in range(4):
            d = self.test_doc(a=str(i))
            yield from d.save()

        collection = self.test_doc._collection
        qs = QuerySet(self.test_doc, collection)
        docs = yield from qs.to_list()
        self.assertEqual(len(docs), 4)
        self.assertTrue(isinstance(docs[0], self.test_doc))

    @async_test
    def test_get(self):
        d = self.test_doc(a=str(1))
        yield from d.save()

        collection = self.test_doc._collection
        qs = QuerySet(self.test_doc, collection)
        returned = yield from qs.get(id=d.id)
        self.assertEqual(d.id, returned.id)

    @async_test
    def test_get_with_no_doc(self):
        collection = self.test_doc._get_collection()
        qs = QuerySet(self.test_doc, collection)

        with self.assertRaises(self.test_doc.DoesNotExist):
            yield from qs.get(id='some')

    @async_test
    def test_get_with_multiple_docs(self):
        d = self.test_doc(a='a')
        yield from d.save()
        d = self.test_doc(a='a')
        yield from d.save()

        collection = self.test_doc._get_collection()
        qs = QuerySet(self.test_doc, collection)

        with self.assertRaises(self.test_doc.MultipleObjectsReturned):
            yield from qs.get(a='a')