from unittest import TestCase

from flask import Flask
from invoicelytics.blueprints.health import HealthBlueprint


class TestHealthBlueprint(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.health_blueprint = HealthBlueprint()
        self.app.register_blueprint(self.health_blueprint.blueprint)
        self.client = self.app.test_client()

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"health": "ok"})
