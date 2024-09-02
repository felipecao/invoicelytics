from uuid import UUID

from sqlalchemy import select

from invoicelytics.entities.domain_entities import User
from invoicelytics.run import db


class UserRepository:

    @staticmethod
    def find_by_id(user_id: UUID):
        return db.session.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def find_by_email(email: str):
        return db.session.scalar(select(User).where(User.email == email))
