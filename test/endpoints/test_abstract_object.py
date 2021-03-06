import json
import os
from unittest import TestCase

from lowerpines.endpoints.object import Field, AbstractObjectType, AbstractObject
from lowerpines.gmi import GMI


class TestField(TestCase):
    def setUp(self):
        self.name_api_field = 'test'
        self.name_varname = 'varname'

        self.basic_field = Field()
        self.api_field = Field(api_name=self.name_api_field)
        self.handler_field = Field(handler=int)

    def test_basic_field(self):
        self.basic_field.set_name(self.name_varname)
        self.assertEqual(self.basic_field.name, self.name_varname)
        self.assertEqual(self.basic_field.api_name, self.name_varname)
        self.assertEqual(self.basic_field.handler, str)

    def test_api_field(self):
        self.api_field.set_name(self.name_varname)
        self.assertEqual(self.api_field.name, self.name_varname)
        self.assertEqual(self.api_field.api_name, self.name_api_field)
        self.assertEqual(self.api_field.handler, str)

    def test_handler_field(self):
        self.handler_field.set_name(self.name_varname)
        self.assertEqual(self.handler_field.name, self.name_varname)
        self.assertEqual(self.handler_field.api_name, self.name_varname)
        self.assertEqual(self.handler_field.handler, int)


class MockAbstractObjectTypeObject(metaclass=AbstractObjectType):
    field1 = Field()
    field2 = Field(handler=int)
    field3 = Field(api_name='id')


class TestAbstractObjectType(TestCase):
    def setUp(self):
        self.mock = MockAbstractObjectTypeObject()

    def test_object_values(self):
        self.assertEqual(self.mock.field1, str())
        self.assertEqual(self.mock.field2, int())
        self.assertEqual(self.mock.field3, str())

    def test_fields_set(self):
        for f in self.mock._fields:
            if f.name == 'field1':
                self.assertEqual(f.handler, str)
                self.assertEqual(f.api_name, 'field1')
            elif f.name == 'field2':
                self.assertEqual(f.handler, int)
                self.assertEqual(f.api_name, 'field2')
            elif f.name == 'field3':
                self.assertEqual(f.handler, str)
                self.assertEqual(f.api_name, 'id')
            else:
                self.assertFalse(True)  # There shouldn't be any other fields


class MockAbstractObject(AbstractObject):
    field1 = Field()
    field2 = Field(handler=int)
    field3 = Field(api_name='id')
    field4 = Field(api_name='foo.bar')

    def __init__(self, gmi):
        self.gmi = gmi
        self.fields_loaded = False

    def on_fields_loaded(self):
        self.fields_loaded = True


JSON_TEST_DATA_1 = os.path.join(os.path.dirname(__file__), 'mock_abstract_object_1.json')
JSON_TEST_DATA_2 = os.path.join(os.path.dirname(__file__), 'mock_abstract_object_2.json')


class TestAbstractObject(TestCase):
    def setUp(self):
        self.gmi = GMI('mock_api_key')
        with open(JSON_TEST_DATA_1) as file:
            self.mock_obj = MockAbstractObject.from_json(self.gmi, json.load(file))
        with open(JSON_TEST_DATA_2) as file:
            self.for_overwrite = MockAbstractObject.from_json(self.gmi, json.load(file))

    def test_fields(self):
        self.assertEqual(self.mock_obj.field1, 'field1_data')
        self.assertEqual(self.mock_obj.field2, 2)
        self.assertEqual(self.mock_obj.field3, 'id_data')
        self.assertEqual(self.mock_obj.field4, 'foo.bar_data')

    def test_on_fields_loaded_called(self):
        self.assertTrue(self.mock_obj.fields_loaded)

    def test_refresh_from_other(self):
        self.for_overwrite._refresh_from_other(self.mock_obj)
        self.assertEqual(self.for_overwrite.field1, 'field1_data')
        self.assertEqual(self.for_overwrite.field2, 2)
        self.assertEqual(self.for_overwrite.field3, 'id_data')
        self.assertEqual(self.for_overwrite.field4, 'foo.bar_data')
