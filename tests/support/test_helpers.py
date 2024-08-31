import json
from unittest import TestCase

from invoicelytics.entities.domain_entities import Invoice
from invoicelytics.support.helpers import get_value, to_json_bytes
from tests import test_faker


class TestHelpers(TestCase):
    def test_get_value_returns_data_point_value(self):
        data_point_name = "payee_name"
        company_name = test_faker.company()
        extracted_data_points = {data_point_name: company_name}
        instance = Invoice(payee_name="other name")

        result = get_value(extracted_data_points, instance, data_point_name)

        assert result == company_name

    def test_get_value_returns_instance_value(self):
        data_point_name = "payee_name"
        company_name = test_faker.company()
        extracted_data_points = {"currency": "EUR"}
        instance = Invoice(payee_name=company_name)

        result = get_value(extracted_data_points, instance, data_point_name)

        assert result == company_name

    def test_get_value_finds_nothing(self):
        data_point_name = test_faker.ssn()
        company_name = test_faker.company()
        extracted_data_points = {"currency": "EUR"}
        instance = Invoice(payee_name=company_name)

        result = get_value(extracted_data_points, instance, data_point_name)

        assert result is None

    def test_basic_dict(self):
        """
        Test that a basic dictionary is correctly converted to bytes.
        """
        input_dict = {"key": "value"}
        expected_output = json.dumps(input_dict).encode("utf-8")
        self.assertEqual(to_json_bytes(input_dict), expected_output)

    def test_empty_dict(self):
        """
        Test that an empty dictionary is correctly converted to bytes.
        """
        input_dict = {}
        expected_output = json.dumps(input_dict).encode("utf-8")
        self.assertEqual(to_json_bytes(input_dict), expected_output)

    def test_nested_dict(self):
        """
        Test that a nested dictionary is correctly converted to bytes.
        """
        input_dict = {"key": {"subkey": "subvalue"}}
        expected_output = json.dumps(input_dict).encode("utf-8")
        self.assertEqual(to_json_bytes(input_dict), expected_output)

    def test_dict_with_special_characters(self):
        """
        Test that a dictionary with special characters is correctly converted to bytes.
        """
        input_dict = {"key": "value", "special": "çäöüß"}
        expected_output = json.dumps(input_dict).encode("utf-8")
        self.assertEqual(to_json_bytes(input_dict), expected_output)

    def test_dict_with_numeric_values(self):
        """
        Test that a dictionary with numeric values is correctly converted to bytes.
        """
        input_dict = {"int": 1, "float": 1.5}
        expected_output = json.dumps(input_dict).encode("utf-8")
        self.assertEqual(to_json_bytes(input_dict), expected_output)

    def test_dict_with_boolean_and_none(self):
        """
        Test that a dictionary with boolean and None values is correctly converted to bytes.
        """
        input_dict = {"true": True, "false": False, "none": None}
        expected_output = json.dumps(input_dict).encode("utf-8")
        self.assertEqual(to_json_bytes(input_dict), expected_output)
