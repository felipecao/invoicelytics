from unittest import TestCase

from invoicelytics.entities.domain_entities import Invoice
from invoicelytics.support.helpers import get_value
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
