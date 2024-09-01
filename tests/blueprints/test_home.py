from unittest import TestCase
from unittest.mock import patch

from flask import Flask

from invoicelytics.blueprints.home import HomeBlueprint
from invoicelytics.blueprints.invoice import InvoiceBlueprint


class TestHomeBlueprint(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.home_blueprint = HomeBlueprint()
        self.invoice_blueprint = InvoiceBlueprint()
        self.app.register_blueprint(self.home_blueprint.blueprint)
        self.app.register_blueprint(self.invoice_blueprint.blueprint)

        self.client = self.app.test_client()

    @patch("invoicelytics.blueprints.home.render_template")
    def test_home_render(self, mock_render_template):
        mock_render_template.return_value = "mock_rendered_template"

        response = self.client.get("/")

        mock_render_template.assert_called_once_with("home.html")
        self.assertEqual(response.data, b"mock_rendered_template")
