import os
import tempfile
from unittest import TestCase

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

        # Create a temporary directory for templates
        self.templates_dir = tempfile.TemporaryDirectory()
        self.app.template_folder = self.templates_dir.name

        # Create a mock home.html template
        with open(os.path.join(self.templates_dir.name, "home.html"), "w") as f:
            f.write('<h1 class="text-center">Welcome</h1>')

        self.client = self.app.test_client()

    def tearDown(self):
        # Clean up the temporary directory
        self.templates_dir.cleanup()

    def test_home_redirect(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/invoices")
