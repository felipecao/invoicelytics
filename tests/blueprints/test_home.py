import os
import tempfile
import unittest

from flask import Flask

from invoicelytics.blueprints.home import HomeBlueprint


class TestHomeBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.home_blueprint = HomeBlueprint()
        self.app.register_blueprint(self.home_blueprint.blueprint)

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

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)
