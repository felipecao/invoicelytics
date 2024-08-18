import os

from invoicelytics.entities.domain_entities import Base
from tests import test_faker
from unittest import TestCase

from sqlalchemy.orm import sessionmaker, scoped_session
from testcontainers.postgres import PostgresContainer

from invoicelytics.run import create_app, db


class BaseRepositoryTest(TestCase):
    _postgres = PostgresContainer("postgres:15")

    @classmethod
    def setUpClass(cls):
        cls._postgres.start()

        os.environ["DATABASE_URL"] = cls._postgres.get_connection_url(cls._postgres.get_container_host_ip())
        os.environ["FLASK_SECRET_KEY"] = test_faker.word()
        os.environ["UPLOAD_FOLDER"] = "/tmp"

        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        cls.engine = db.create_engine(os.environ["DATABASE_URL"])
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()
        cls._postgres.stop()

    def setUp(self):
        # Explicitly create a new connection and transaction
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()

        # Use sessionmaker to bind the session configuration to the connection
        session_factory = sessionmaker(bind=self.connection)
        self.session = scoped_session(session_factory)

        # Temporarily replace the session in use by the db object
        db.session = self.session

    def tearDown(self):
        # Ensure the database is emptied after tests
        self.transaction.rollback()
        db.session.remove()

    @staticmethod
    def save_entity(entity):
        db.session.add(entity)
        db.session.commit()
        return entity
